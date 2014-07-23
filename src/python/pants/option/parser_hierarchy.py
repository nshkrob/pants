# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from argparse import ArgumentParser
import copy

from pants.option.help_formatter import PantsHelpFormatter
from pants.option.ranked_value import RankedValue


class RegistrationError(Exception):
  pass


class Parser(object):
  """A parser in a scoped hierarchy.

  Options registered on a parser are also registered on all the parsers in enclosed scopes.
  Registration must be in outside-in order: we forbid registering options on an outer scope if
  we've already registered an option on one of its inner scopes. This is to ensure that
  re-registering the same option name on an inner scope correctly replaces the option inherited
  from the outer scope.

  :param config anything that supports get(section, name, default=).
  """
  def __init__(self, env, config, scope, parent_parser):
    self._env = env
    self._config = config
    self._scope = scope
    self._locked = False  # If True, no more registration is allowed on this parser.
    # The argparser we use for actually parsing args.
    self._argparser = ArgumentParser(conflict_handler='resolve')

    # The argparser we use for formatting help messages.
    self._help_argparser = ArgumentParser(conflict_handler='resolve',
                                          formatter_class=PantsHelpFormatter)

    self._dest_forwardings = {}  # arg to dest.
    self._parent_parser = parent_parser  # A Parser instance, or None for the global scope parser.
    self._child_parsers = []  # List of Parser instances.
    if self._parent_parser:
      self._parent_parser._child_parsers.append(self)

  def parse_args(self, args, namespace):
    """Parse the given args and set their values onto the namespace object's attributes."""
    namespace.add_forwardings(self._dest_forwardings)
    new_args = self._argparser.parse_args(args)
    namespace.update(vars(new_args))
    return namespace

  def format_help(self):
    return self._help_argparser.format_help()

  def register(self, *args, **kwargs):
    """Register an option, using argparse params."""
    if self._locked:
      raise RegistrationError('Cannot register option %s in scope %s after registering options '
                              'in any of its inner scopes.' % (args[0], self._scope))
    # Prevent further registration in enclosing scopes.
    if self._parent_parser:
      self._parent_parser._lock()
    dest = self._set_dest(args, kwargs)

    # For help formatting we register only in this scope.
    raw_default = self._compute_default(dest, kwargs).value
    kwargs_with_default = dict(kwargs, default=raw_default)
    self._help_argparser.add_argument(*args, **kwargs_with_default)

    # For parsing we register on this and all enclosed scopes.
    self._register(dest, args, kwargs)

  def register_boolean(self, *args, **kwargs):
    """Register a boolean option, using argparse params.

    An inverse option will be automatically created. E.g., --foo will have a companion --no-foo
    (unless the flag already starts with '--no-').
    """
    if self._locked:
      raise RegistrationError('Cannot register option %s in scope %s after registering options '
                              'in any of its inner scopes.' % (args[0], self._scope))
    # Prevent further registration in enclosing scopes.
    if self._parent_parser:
      self._parent_parser._lock()
    dest = self._set_dest(args, kwargs)

    inverse_args = []
    help_args = []
    for flag in args:
      if flag.startswith('--') and not flag.startswith('--no-'):
        inverse_args.append('--no-' + flag[2:])
        help_args.append('--[no-]%s' % flag[2:])
      else:
        help_args.append(flag)

    # For help formatting we register only in this scope.
    raw_default = self._compute_default(dest, kwargs).value
    kwargs_with_default = dict(kwargs, default=raw_default)
    self._help_argparser.add_argument(*help_args, **kwargs_with_default)

    # For parsing we register the flag, and its inverse, on this and all enclosed scopes.
    if inverse_args:
      action = kwargs.get('action')
      if action not in ('store_false', 'store_true'):
        raise RegistrationError('Invalid action for boolean flag: %s' % action)
      inverse_action = 'store_true' if action == 'store_false' else 'store_false'
      inverse_kwargs = copy.copy(kwargs)
      inverse_kwargs['action'] = inverse_action
      self._register_boolean(dest, args, kwargs, inverse_args, inverse_kwargs)
    else:
      self._register(dest, args, kwargs)

  def _register(self, dest, args, kwargs):
    ranked_default = self._compute_default(dest, kwargs)
    kwargs_with_default = dict(kwargs, default=ranked_default)
    self._argparser.add_argument(*args, **kwargs_with_default)
    # Propagate registration down to inner scopes.
    for child_parser in self._child_parsers:
      child_parser._register(dest, args, kwargs)

  def _register_boolean(self, dest, args, kwargs, inverse_args, inverse_kwargs):
    group = self._argparser.add_mutually_exclusive_group()
    ranked_default = self._compute_default(dest, kwargs)
    inverse_ranked_default = RankedValue(ranked_default.rank, not ranked_default.value)
    kwargs_with_default = dict(kwargs, default=ranked_default)
    inverse_kwargs_with_default = dict(inverse_kwargs, default=inverse_ranked_default)
    group.add_argument(*args, **kwargs_with_default)
    group.add_argument(*inverse_args, **inverse_kwargs_with_default)

    # Propagate registration down to inner scopes.
    for child_parser in self._child_parsers:
      child_parser._register_boolean(dest, args, kwargs, inverse_args, inverse_kwargs)

  def _set_dest(self, args, kwargs):
    """Maps the externally-used dest to a scoped one only seen internally.

    If an option is re-registered in an inner scope, it'll shadow the external dest but will
    use a different internal one. This is important in the case that an option is registered
    with two names (say -x, --xlong) and we only re-register one of them, say --xlong, in an
    inner scope. In this case we no longer want them to write to the same dest, so that
    we can use both (now with different meanings) in the inner scope.
    """
    dest = self._infer_dest(args, kwargs)
    scoped_dest = '_%s_%s__' % (self._scope or 'DEFAULT', dest)
    kwargs['dest'] = scoped_dest
    self._dest_forwardings[dest] = scoped_dest
    # Also forward all option aliases, so there's still a way to reference -x (as options.x)
    # in the example above.
    for arg in args:
      self._dest_forwardings[arg.lstrip('-').replace('-', '_')] = scoped_dest
    return dest

  def _infer_dest(self, args, kwargs):
    # Replicated from the dest inference logic in argparse:
    # '--foo-bar' -> 'foo_bar' and '-x' -> 'x'.
    dest = kwargs.get('dest')
    if dest:
      return dest
    arg = next((a for a in args if a.startswith('--')), args[0])
    return arg.lstrip('-').replace('-', '_')

  def _compute_default(self, dest, kwargs):
    """Compute the default value to use for an option's registration."""
    config_section = 'DEFAULT' if self._scope == '' else self._scope
    env_var = 'PANTS_%s_%s' % (config_section.upper().replace('.', '_'), dest.upper())

    value_type = kwargs.get('type', str)
    env_value_str = self._env.get(env_var)
    env_value = None if env_value_str is None else value_type(env_value_str)
    config_value = self._config.get(config_section, dest, default=None)
    hardcoded_value = kwargs.get('default')

    if env_value is not None:
      return RankedValue(RankedValue.ENVIRONMENT, env_value)
    elif config_value is not None:
      return RankedValue(RankedValue.CONFIG, config_value)
    elif hardcoded_value is not None:
      return RankedValue(RankedValue.HARDCODED, hardcoded_value)
    else:
      return RankedValue(RankedValue.NONE, None)

  def _lock(self):
    if not self._locked:
      self._locked = True
      if self._parent_parser:
        self._parent_parser._lock()

  def __str__(self):
    return 'Parser(%s)' % self._scope


class ParserHierarchy(object):
  def __init__(self, env, config, all_scopes):
    # Sorting ensures that ancestors precede descendants.
    all_scopes = sorted(set(list(all_scopes) + ['']))
    self._parser_by_scope = {}
    for scope in all_scopes:
      parent_parser = None if scope == '' else self._parser_by_scope[scope.rpartition('.')[0]]
      self._parser_by_scope[scope] = Parser(env, config, scope, parent_parser)

  def get_parser_by_scope(self, scope):
    return self._parser_by_scope[scope]
