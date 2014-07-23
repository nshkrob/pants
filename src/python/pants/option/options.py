# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import copy
import sys

from pants.option.arg_splitter import ArgSplitter
from pants.option.option_value_container import OptionValueContainer
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
  def __init__(self, env, config, known_scopes, args=sys.argv):
    splitter = ArgSplitter(known_scopes)
    self._scope_to_flags, self._target_specs = splitter.split_args(args)
    self._help = splitter.help
    self._parser_hierarchy = ParserHierarchy(env, config, known_scopes)
    self._values_by_scope = {}  # Arg values, parsed per-scope on demand.

  @property
  def help(self):
    """Whether the command line indicates a request for help."""
    return self._help

  @property
  def target_specs(self):
    """The targets to operate on."""
    return self._target_specs

  @property
  def goals(self):
    """The requested goals."""
    return set([g for g in self._scope_to_flags.keys() if g and not '.' in g])

  def get_global_parser(self):
    """Returns the parser for the given scope, so code can register on it directly."""
    return self.get_parser('')

  def register_global(self, *args, **kwargs):
    """Register an option in the global scope, using argparse params."""
    self.register('', *args, **kwargs)

  def register_global_boolean(self, *args, **kwargs):
    """Register a boolean option in the global scope, using argparse params.

    An inverse option will be automatically created. E.g., --foo will have a companion --no-foo.
    """
    self.register_boolean('', *args, **kwargs)

  def get_parser(self, scope):
    """Returns the parser for the given scope, so code can register on it directly."""
    return self._parser_hierarchy.get_parser_by_scope(scope)

  def register(self, scope, *args, **kwargs):
    """Register an option in the given scope, using argparse params."""
    self.get_parser(scope).register(*args, **kwargs)

  def register_boolean(self, scope, *args, **kwargs):
    """Register a boolean option in the given scope, using argparse params.

    An inverse option will be automatically created. E.g., --foo will have a companion --no-foo.
    """
    self._parser_hierarchy.get_parser_by_scope(scope).register_boolean(*args, **kwargs)

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
    else:
      values = copy.deepcopy(self.for_scope(scope.rpartition('.')[0]))

    # Now add our values.
    flags_in_scope = self._scope_to_flags.get(scope, [])
    self._parser_hierarchy.get_parser_by_scope(scope).parse_args(flags_in_scope, values)
    self._values_by_scope[scope] = values
    return values
