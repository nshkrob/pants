# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from pants.option.parser import Parser


class ParserHierarchy(object):
  """A hierarchy of scoped Parser instances.

  A scope is a dotted string: foo.bar. The foo bar encloses the foo.bar scope etc.
  The empty string represents the global scope.

  We use these scopes to represent phases and tasks.  This structure organizes the
  Parser instances that know how to parse flags for each phase and task.
  """
  def __init__(self, env, config, all_scopes, legacy_parser=None):
    # Sorting ensures that ancestors precede descendants.
    all_scopes = sorted(set(list(all_scopes) + ['']))
    self._parser_by_scope = {}
    for scope in all_scopes:
      parent_parser = None if scope == '' else self._parser_by_scope[scope.rpartition('.')[0]]
      self._parser_by_scope[scope] = Parser(env, config, scope, parent_parser, legacy_parser)

  def get_parser_by_scope(self, scope):
    return self._parser_by_scope[scope]
