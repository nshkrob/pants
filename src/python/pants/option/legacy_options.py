# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import copy



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
    self._prefix = scope.replace('.', '-')
    self._optparser = optparser

  def register(self, *args, **kwargs):
    """Register the option, using argparse params.

    Modifies kwargs in place by removing any legacy-related keys.
    """
    dest = kwargs.pop('legacy', None)
    if dest:
      self._optparser.add_option(*args, **kwargs)
      # The args/kwargs are argparse-style, whereas we need optparse-style, so
      # we perform necessary adjustments here.
      optparse_kwargs = copy.copy(kwargs)
      optparse_kwargs['dest'] = dest

      # The 'type' kwarg is a function in argparse but a string in optparse.
      typ = optparse_kwargs.pop('type', str)
      if typ not in LegacyOptions.OPTPARSE_TYPES:
        raise LegacyOptionsError('Invalid optparse type: %s' % typ)
      optparse_kwargs['type'] = typ.__name__

      # 'choice' is a string subtype in optparse.
      choices = optparse_kwargs.get('choices', None)
      if choices and typ == str:
        optparse_kwargs['type'] = 'choice'
      else:  # optparse doesn't support non-string choices, so remove the choices restriction.
        optparse_kwargs.pop('choices')

      action = optparse_kwargs.get('action', 'store')
      if action not in LegacyOptions.OPTPARSE_ACTIONS:
        raise LegacyOptionsError('Invalid optparse action: %s' % action)

      self._optparser.add_option(*args, **optparse_kwargs)
