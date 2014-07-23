# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import argparse

from pants.base.build_environment import pants_release
from pants.goal import Phase


class PantsHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
  def add_usage(self, usage, actions, groups, prefix=None):
    pass

  def add_text(self, text):
    pass

  def start_section(self, heading):
    pass

  def end_section(self):
    pass

  def add_argument(self, action):
    if action.help is not argparse.SUPPRESS:
      # find all invocations
      get_invocation = self._format_action_invocation
      invocations = [get_invocation(action)]
      for subaction in self._iter_indented_subactions(action):
        invocations.append(get_invocation(subaction))

      # update the maximum item length
      invocation_length = max([len(s) for s in invocations])
      action_length = invocation_length + self._current_indent
      self._action_max_length = max(self._action_max_length,
                                    action_length)

      # add the item to the list
      self._add_item(self._format_action, [action])


def new_print_help(options):
  if options.goals:
    for goal in options.goals:
      phase = Phase(goal)
      if not phase.goals():
        print('\nUnknown goal: %s' % goal)
      else:
        print('\n%s options:' % goal)
        options.format_help(goal)
  else:
    print(pants_release())
    print('\nUsage:')
    print('  ./pants new [option ...] [goal ...] [target...]  Attempt the specified goals.')
    print('  ./pants new help                                 Get help.')
    print('  ./pants new help [goal]                          Get help for the specified goal.')
    print('  ./pants new goals                                List all installed goals.')
    print('')
    print('  [target] accepts two special forms:')
    print('    dir:  to include all targets in the specified directory.')
    print('    dir:: to include all targets found recursively under the directory.')

    print('\nFriendly docs:\n  http://pantsbuild.github.io/')

    print('\nGlobal options:')
    print(options.format_global_help())
