# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from argparse import ArgumentParser
import copy

from pants.option.help_formatter import PantsHelpFormatter
from pants.option.legacy_options import LegacyOptions
from pants.option.ranked_value import RankedValue


class RegistrationError(Exception):
  """An error at option registration time."""
  pass


class ParseError(Exception):
  """An error at flag parsing time."""
  pass


# Standard ArgumentParser prints usage and exists on error. We subclass so we can raise instead.
class CustomArgumentParser(ArgumentParser):
  def error(self, message):
    raise ParseError(message)


class Parser(object):
  """A parser in a scoped hierarchy.

  Options registered on a parser are also registered on all the parsers in inner scopes.
  Registration must be in outside-in order: we forbid registering options on an outer scope if
  we've already registered an option on one of its inner scopes. This is to ensure that
  re-registering the same option name on an inner scope correctly replaces the option inherited
  from the outer scope.

  :param env: a dict of environment variables.
  :param config: data from a config file (must support config.get(section, name, default=)).
  :param scope: the scope this parser acts for.
  :param parent_parser: the parser for the scope immediately enclosing this one, or
         None if this is the global scope.
  :param legacy_parser: an optparse.OptionParser instance for handling legacy options.
  """
  def __init__(self, env, config, scope, parent_parser, legacy_parser=None):
    self._env = env
    self._config = config
    self._scope = scope
    self._frozen = False  # If True, no more registration is allowed on this parser.
    # The argparser we use for actually parsing args.
    self._argparser = CustomArgumentParser(conflict_handler='resolve')

    # The argparser we use for formatting help messages.
    self._help_argparser = CustomArgumentParser(conflict_handler='resolve',
                                                formatter_class=PantsHelpFormatter)

    self._dest_forwardings = {}  # arg to dest.
    self._parent_parser = parent_parser  # A Parser instance, or None for the global scope parser.
    self._child_parsers = []  # List of Parser instances.
    if self._parent_parser:
      self._parent_parser._child_parsers.append(self)

    self._legacy_options = LegacyOptions(scope, legacy_parser) if legacy_parser else None

  def parse_args(self, args, namespace):
    """Parse the given args and set their values onto the namespace object's attributes."""
    namespace.add_forwardings(self._dest_forwardings)
    new_args = self._argparser.parse_args(args)
    namespace.update(vars(new_args))
    return namespace

  def format_help(self, legacy=False):
    if legacy:
      return self._legacy_options.format_help()
    else:
      return self._help_argparser.format_help()

  def register(self, *args, **kwargs):
    """Register an option, using argparse params."""
    if self._frozen:
      raise RegistrationError('Cannot register option %s in scope %s after registering options '
                              'in any of its inner scopes.' % (args[0], self._scope))
    # Prevent further registration in enclosing scopes.
    ancestor = self._parent_parser
    while ancestor:
      ancestor._frozen = True
      ancestor = ancestor._parent_parser

    clean_kwargs = copy.copy(kwargs)  # kwargs without legacy-related keys.
    kwargs = None  # Ensure no code below modifies kwargs accidentally.
    self._validate(args, clean_kwargs)
    legacy_dest = clean_kwargs.pop('legacy', None)
    dest = self._set_dest(args, clean_kwargs, legacy_dest)

    # Is this a boolean flag?
    if clean_kwargs.get('action') in ('store_false', 'store_true'):
      inverse_args = []
      help_args = []
      for flag in args:
        if flag.startswith('--') and not flag.startswith('--no-'):
          inverse_args.append('--no-' + flag[2:])
          help_args.append('--[no-]%s' % flag[2:])
        else:
          help_args.append(flag)
    else:
      inverse_args = None
      help_args = args

    # For help formatting we register only in this scope.
    # Note that we'll only display the default value for the scope in which
    # we registered, even though the default may be overridden in inner scopes.
    raw_default = self._compute_default(dest, clean_kwargs).value
    clean_kwargs_with_default = dict(clean_kwargs, default=raw_default)
    self._help_argparser.add_argument(*help_args, **clean_kwargs_with_default)

    # We register legacy options only in this scope.
    if self._legacy_options:
      self._legacy_options.register(args, clean_kwargs_with_default, legacy_dest)

    # For parsing we register on this and all enclosed scopes.
    if inverse_args:
      inverse_kwargs = self._create_inverse_kwargs(clean_kwargs)
      if self._legacy_options:
        self._legacy_options.register(inverse_args, inverse_kwargs, legacy_dest)
      self._register_boolean(dest, args, clean_kwargs, inverse_args, inverse_kwargs)
    else:
      self._register(dest, args, clean_kwargs)

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
    kwargs_with_default = dict(kwargs, default=ranked_default)
    group.add_argument(*args, **kwargs_with_default)
    group.add_argument(*inverse_args, **inverse_kwargs)

    # Propagate registration down to inner scopes.
    for child_parser in self._child_parsers:
      child_parser._register_boolean(dest, args, kwargs, inverse_args, inverse_kwargs)

  def _validate(self, args, kwargs):
    for k in ['nargs', 'required']:
      if k in kwargs:
        raise RegistrationError('%s unsupported in registration of option %s.' % (k, args))

  def _set_dest(self, args, kwargs, legacy_dest):
    """Maps the externally-used dest to a scoped one only seen internally.

    If an option is re-registered in an inner scope, it'll shadow the external dest but will
    use a different internal one. This is important in the case that an option is registered
    with two names (say -x, --xlong) and we only re-register one of them, say --xlong, in an
    inner scope. In this case we no longer want them to write to the same dest, so we can
    use both (now with different meanings) in the inner scope.

    Note: Modfies kwargs.
    """
    dest = self._infer_dest(args, kwargs)
    scoped_dest = '_%s_%s__' % (self._scope or 'DEFAULT', dest)
    kwargs['dest'] = scoped_dest
    self._dest_forwardings[dest] = scoped_dest
    # Also forward all option aliases, so there's still a way to reference -x (as options.x)
    # in the example above.
    for arg in args:
      self._dest_forwardings[arg.lstrip('-').replace('-', '_')] = scoped_dest

    # Support for legacy flags.  Remove when the transition to new options is complete.
    if legacy_dest:  # Forward another hop, to the legacy dest.
      self._dest_forwardings[scoped_dest] = legacy_dest
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
    env_val_str = self._env.get(env_var) if self._env else None

    env_val = None if env_val_str is None else value_type(env_val_str)
    config_val = self._config.get(config_section, dest, default=None) if self._config else None
    hardcoded_val = kwargs.get('default')
    return RankedValue.choose(None, env_val, config_val, hardcoded_val)

  def _create_inverse_kwargs(self, kwargs):
    inverse_kwargs = copy.copy(kwargs)
    inverse_action = 'store_true' if kwargs.get('action') == 'store_false' else 'store_false'
    inverse_kwargs['action'] = inverse_action
    inverse_kwargs.pop('default', None)
    return inverse_kwargs

  def __str__(self):
    return 'Parser(%s)' % self._scope
