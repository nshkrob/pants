# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import copy
from optparse import OptionGroup


class LegacyOptionsError(Exception):
  pass


class LegacyOptions(object):
  """Register new-style options in the old style.

  This is so we can support old-style command-lines during migration to the new options system.
  """

  # Optparse can only support options of these types. After migration is complete and this
  # class is deleted, feel free to use other types for your new-style options.
  OPTPARSE_TYPES = set([str, int, long, float, complex])

  OPTPARSE_ACTIONS = set(['store', 'store_const', 'store_true', 'store_false',
                          'append', 'append_const', 'count'])

  def __init__(self, scope, optparser):
    """Register for the given scope, into the given optparser."""
    self._scope_prefix = scope.replace('.', '-')
    self._optparser = optparser
    self._optparser_group = self._get_option_group(scope, optparser)
    if self._optparser_group:
      self._optparser.add_option_group(self._optparser_group)
    self._registered_dests = set()  # Needed for printing help messages.

  def register(self, args, kwargs, legacy_dest=None, legacy_args=None):
    """Register the option, using argparse params."""
    if legacy_dest:
      optparse_kwargs = copy.copy(kwargs)

      # The args/kwargs are argparse-style, whereas we need optparse-style, so
      # we perform necessary adjustments here.
      optparse_args = []
      for arg in legacy_args or args:
        if arg.startswith('--no-'):
          optparse_args.append('--no-%s-%s' % (self._scope_prefix, arg[5:]))
          optparse_kwargs.pop('help', None)
        elif arg.startswith('--'):
          optparse_args.append('--%s-%s' % (self._scope_prefix, arg[2:]))
        elif arg.startswith('-'):
          if self._scope_prefix == '':
            optparse_args.append(arg)
          else:
            raise LegacyOptionsError('Short legacy options only allowed at global scope.')

      optparse_kwargs['dest'] = legacy_dest

      # The 'type' kwarg is a function in argparse but a string in optparse.
      typ = optparse_kwargs.pop('type', None)
      if typ:
        if typ in LegacyOptions.OPTPARSE_TYPES:
          optparse_kwargs['type'] = typ.__name__
        else:
          raise LegacyOptionsError('Invalid optparse type: %s' % typ)

      # 'choice' is a string subtype in optparse.
      choices = optparse_kwargs.get('choices', None)
      if choices and (typ is None or typ == str):
        optparse_kwargs['type'] = 'choice'
      else:  # optparse doesn't support non-string choices, so ignore the choices restriction.
        optparse_kwargs.pop('choices', None)

      action = optparse_kwargs.get('action', 'store')
      if action not in LegacyOptions.OPTPARSE_ACTIONS:
        raise LegacyOptionsError('Invalid optparse action: %s' % action)

      options_container = self._optparser_group or self._optparser
      options_container.add_option(*optparse_args, **optparse_kwargs)
      self._registered_dests.add(legacy_dest)

  def format_help(self):
    self._optparser.formatter.store_option_strings(self._optparser)
    if self._optparser_group and self._optparser_group.option_list:
      return self._optparser_group.format_help(self._optparser.formatter)
    else:
      return ''

  def _get_option_group(self, scope, optparser):
    if not scope:
      return None
    # See if we have an existing option group (from options registered the old way).
    for option_group in optparser.option_groups:
      if option_group.title == scope:
        return option_group
    return OptionGroup(optparser, scope)

