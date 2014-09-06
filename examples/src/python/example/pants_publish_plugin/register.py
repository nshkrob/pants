# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from example.pants_publish_plugin.extra_test_jar_example import ExtraTestJarExample
from pants.goal.goal import Goal
from pants.goal.task_registrar import TaskRegistrar as task

task(name='extra_test_jar_example', action=ExtraTestJarExample).install('jar')
