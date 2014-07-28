# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from pants.backend.core.tasks.console_task import ConsoleTask
from pants.goal.phase import Phase


class ListGoals(ConsoleTask):
  @classmethod
  def register_options(cls, registry):
    super(ListGoals, cls).register_options(registry)
    registry.register('--all', default=False, action='store_true',
                      help='List all goals even if no description is available.',
                      legacy='goal_list_all')
    registry.register('--graph', default=False, action='store_true',
                      help='Generate a graphviz graph of installed goals.',
                      legacy='goal_list_graph')

  @classmethod
  def setup_parser(cls, option_group, args, mkflag):
    super(ListGoals, cls).setup_parser(option_group, args, mkflag)
    option_group.add_option(mkflag("all"),
                            dest="goal_list_all",
                            default=False,
                            action="store_true",
                            help="[%default] List all goals even if no description is available.")
    option_group.add_option(mkflag('graph'),
                            dest='goal_list_graph',
                            action='store_true',
                            help='[%default] Generate a graphviz graph of installed goals.')

  def console_output(self, targets):
    def report():
      yield 'Installed goals:'
      documented_rows = []
      undocumented = []
      max_width = 0
      for phase, _ in Phase.all():
        if phase.description:
          documented_rows.append((phase.name, phase.description))
          max_width = max(max_width, len(phase.name))
        elif self.options.all:
          undocumented.append(phase.name)
      for name, description in documented_rows:
        yield '  %s: %s' % (name.rjust(max_width), description)
      if undocumented:
        yield ''
        yield 'Undocumented goals:'
        yield '  %s' % ' '.join(undocumented)

    def graph():
      def get_cluster_name(phase):
        return 'cluster_%s' % phase.name.replace('-', '_')

      def get_goal_name(phase, goal):
        name = '%s_%s' % (phase.name, goal.name)
        return name.replace('-', '_')

      phase_by_phasename = {}
      for phase, goals in Phase.all():
        phase_by_phasename[phase.name] = phase

      yield '\n'.join([
        'digraph G {',
        '  rankdir=LR;',
        '  graph [compound=true];',
        ])
      for phase, installed_goals in Phase.all():
        yield '\n'.join([
          '  subgraph %s {' % get_cluster_name(phase),
          '    node [style=filled];',
          '    color = blue;',
          '    label = "%s";' % phase.name,
        ])
        for installed_goal in installed_goals:
          yield '    %s [label="%s"];' % (get_goal_name(phase, installed_goal),
                                          installed_goal.name)
        yield '  }'

      edges = set()
      for phase, installed_goals in Phase.all():
        for installed_goal in installed_goals:
          for dependency in installed_goal.dependencies:
            tail_goal = phase_by_phasename.get(dependency.name).goals()[-1]
            edge = 'ltail=%s lhead=%s' % (get_cluster_name(phase),
                                          get_cluster_name(Phase.of(tail_goal)))
            if edge not in edges:
              yield '  %s -> %s [%s];' % (get_goal_name(phase, installed_goal),
                                          get_goal_name(Phase.of(tail_goal), tail_goal),
                                          edge)
            edges.add(edge)
      yield '}'

    return graph() if self.options.graph else report()
