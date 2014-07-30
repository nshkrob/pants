# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import copy
import sys

from pants.base.build_environment import pants_release
from pants.goal.phase import Phase
from pants.option.arg_splitter import ArgSplitter
from pants.option.option_value_container import OptionValueContainer
from pants.option.parser import ParseError
from pants.option.parser_hierarchy import ParserHierarchy


class OptionError(Exception):
  pass


class Options(object):
  """The outward-facing API for interacting with options.

  Supports option registration and reading option values.

  Examples:

 The value in global scope of option 'foo_bar' (registered in global scope) will be selected
 in the following order:
    - The value of the --foo-bar flag in global scope.
    - The value of the PANTS_DEFAULT_FOO_BAR environment variable.
    - The value of the foo_bar key in the [DEFAULT] section of pants.ini.
    - The hard-coded value provided at registration time.
    - None.

  The value in scope 'sco.pe' of option 'foo_bar' (registered in global scope) will be selected
  in the following order:
    - The value of the --foo-bar flag in scope 'sco.pe'.
    - The value of the --foo-bar flag in scope 'sco'.
    - The value of the --foo-bar flag in global scope.
    - The value of the PANTS_SCO_PE_FOO_BAR environment variable.
    - The value of the PANTS_SCO_FOO_BAR environment variable.
    - The value of the PANTS_DEFAULT_FOO_BAR environment variable.
    - The value of the foo_bar key in the [sco.pe] section of pants.ini.
    - The value of the foo_bar key in the [sco] section of pants.ini.
    - The value of the foo_bar key in the [DEFAULT] section of pants.ini.
    - The hard-coded value provided at registration time.
    - None.

  The value in scope 'sco.pe' of option 'foo_bar' (registered in scope 'sco') will be selected
  in the following order:
    - The value of the --foo-bar flag in scope 'sco.pe'.
    - The value of the --foo-bar flag in scope 'sco'.
    - The value of the PANTS_SCO_PE_FOO_BAR environment variable.
    - The value of the PANTS_SCO_FOO_BAR environment variable.
    - The value of the foo_bar key in the [sco.pe] section of pants.ini.
    - The value of the foo_bar key in the [sco] section of pants.ini.
    - The value of the foo_bar key in the [DEFAULT] section of pants.ini
      (because of automatic config file fallback to that section).
    - The hard-coded value provided at registration time.
    - None.
  """
  def __init__(self, env, config, known_scopes, args=sys.argv, legacy_parser=None):
    splitter = ArgSplitter(known_scopes)
    self._scope_to_flags, self._target_specs = splitter.split_args(args)
    self._is_help = splitter.is_help
    self._parser_hierarchy = ParserHierarchy(env, config, known_scopes, legacy_parser)
    self._legacy_parser = legacy_parser  # Old-style options, used temporarily during transition.
    self._legacy_values = None  # Values parsed from old-stype options.
    self._values_by_scope = {}  # Arg values, parsed per-scope on demand.

  @property
  def target_specs(self):
    """The targets to operate on."""
    return self._target_specs

  @property
  def phases(self):
    """The requested phases."""
    # TODO: Order them in some way? We don't know anything about the topological
    # order here, but it would be nice to, e.g., display help in that order.
    return set([g.partition('.')[0] for g in self._scope_to_flags.keys() if g])

  @property
  def is_help(self):
    """Whether the command line indicates a request for help."""
    return self._is_help

  def set_legacy_values(self, legacy_values):
    self._legacy_values = legacy_values

  def format_global_help(self, legacy=False):
    return self.get_global_parser().format_help(legacy=legacy)

  def format_help(self, scope, legacy=False):
    return self.get_parser(scope).format_help(legacy=legacy)

  def register_global(self, *args, **kwargs):
    """Register an option in the global scope, using argparse params."""
    self.register('', *args, **kwargs)

  def get_global_parser(self):
    """Returns the parser for the given scope, so code can register on it directly."""
    return self.get_parser('')

  def get_parser(self, scope):
    """Returns the parser for the given scope, so code can register on it directly."""
    return self._parser_hierarchy.get_parser_by_scope(scope)

  def register(self, scope, *args, **kwargs):
    """Register an option in the given scope, using argparse params."""
    self.get_parser(scope).register(*args, **kwargs)

  def for_global_scope(self):
    """Return the option values for the global scope.

    Values are attributes of the returned object, e.g., options.foo.
    Computed lazily.
    """
    return self.for_scope('')

  def for_scope(self, scope):
    """Return the option values for the given scope.

    Values are attributes of the returned object, e.g., options.foo.
    Computed lazily per scope.
    """
    # Short-circuit, if already computed.
    if scope in self._values_by_scope:
      return self._values_by_scope[scope]

    # First get enclosing scope's option values, if any.
    if scope == '':
      values = OptionValueContainer()
      if self._legacy_values:
        values.update(vars(self._legacy_values))  # Proxy legacy option values.
    else:
      values = copy.copy(self.for_scope(scope.rpartition('.')[0]))

    # Now add our values.
    try:
      flags_in_scope = self._scope_to_flags.get(scope, [])
      self._parser_hierarchy.get_parser_by_scope(scope).parse_args(flags_in_scope, values)
      self._values_by_scope[scope] = values
      return values
    except ParseError as e:
      self.print_help(str(e))
      sys.exit(1)

  def print_help(self, msg=None, phases=None, legacy=False):
    """Print a help screen, followed by an optional message.

    Note: Ony useful if called after options have been registered.
    """
    phases = phases or self.phases
    if phases:
      for phase_name in phases:
        phase = Phase(phase_name)
        if not phase.goals():
          print('\nUnknown goal: %s' % phase_name)
        else:
          print('\n%s options:' % phase.name)
          print(self.format_help('%s' % phase.name, legacy=legacy))
          for goal in phase.goals():
            if goal.name != phase.name:  # Otherwise we registered on the phase scope.
              scope = '%s.%s' % (phase.name, goal.name)
              print('\n%s options:' % scope)
              print(self.format_help(scope, legacy=legacy))
    else:
      print(pants_release())
      print('\nUsage:')
      print('  ./pants goal [option ...] [goal ...] [target...]  Attempt the specified goals.')
      print('  ./pants goal help                                 Get help.')
      print('  ./pants goal help [goal]                          Get help for the specified goal.')
      print('  ./pants goal goals                                List all installed goals.')
      print('')
      print('  [target] accepts two special forms:')
      print('    dir:  to include all targets in the specified directory.')
      print('    dir:: to include all targets found recursively under the directory.')

      print('\nFriendly docs:\n  http://pantsbuild.github.io/')

      print('\nGlobal options:')
      print(self.format_global_help())

    if msg is not None:
      print(msg)
