# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import os
import pytest

from pants.util.contextutil import temporary_dir
from pants_test.pants_run_integration_test import PantsRunIntegrationTest
from pants_test.tasks.test_base import is_exe

def shared_artifacts(version):
  return {'com/pants/examples/hello-greet/{0}/'.format(version):
          ['ivy-{0}.xml'.format(version),
            'hello-greet-{0}.jar'.format(version),
            'hello-greet-{0}.pom'.format(version),
            'hello-greet-{0}-sources.jar'.format(version)]}

class JarPublishIntegrationTest(PantsRunIntegrationTest):
  SCALADOC = is_exe('scaladoc')
  JAVADOC = is_exe('javadoc')


  @pytest.mark.skipif('not JarPublishIntegrationTest.SCALADOC',
                      reason='No scaladoc binary on the PATH.')
  def test_scala_publish(self):
    unique_artifacts = {'com/pants/example/jvm-example-lib/0.0.1-SNAPSHOT':
                        ['ivy-0.0.1-SNAPSHOT.xml',
                         'jvm-example-lib-0.0.1-SNAPSHOT.jar',
                         'jvm-example-lib-0.0.1-SNAPSHOT.pom',
                         'jvm-example-lib-0.0.1-SNAPSHOT-sources.jar'],
                        'com/pants/example/hello/welcome/0.0.1-SNAPSHOT':
                        ['ivy-0.0.1-SNAPSHOT.xml',
                         'welcome-0.0.1-SNAPSHOT.jar',
                         'welcome-0.0.1-SNAPSHOT.pom',
                         'welcome-0.0.1-SNAPSHOT-sources.jar'],}
    self.publish_test('examples/src/scala/com/pants/example:jvm-run-example-lib',
                      dict(unique_artifacts.items() + shared_artifacts('0.0.1-SNAPSHOT').items()),
                      extra_options=['--doc-scaladoc-skip'],
                      expected_primary_artifact_count=3)

  @pytest.mark.skipif('not JarPublishIntegrationTest.JAVADOC',
                      reason='No javadoc binary on the PATH.')
  def test_java_publish(self):
    self.publish_test('examples/src/java/com/pants/examples/hello/greet',
                      shared_artifacts('0.0.1-SNAPSHOT'),)

  def test_named_snapshot(self):
    name = "abcdef0123456789"
    self.publish_test('examples/src/java/com/pants/examples/hello/greet',
                      shared_artifacts(name),
                      extra_options=['--publish-named-snapshot=%s' % name])

  def test_publish_extras(self):
    self.publish_test('examples/src/java/com/pants/examples/hello/greet',
                      {'com/pants/examples/hello-greet/0.0.1-SNAPSHOT/':
                        ['ivy-0.0.1-SNAPSHOT.xml',
                         'hello-greet-0.0.1-SNAPSHOT.jar',
                         'hello-greet-0.0.1-SNAPSHOT.pom',
                         'hello-greet-0.0.1-SNAPSHOT-sources.jar',
                         'hello-greet-extra_example-0.0.1-SNAPSHOT-classy.jar']},
                      extra_options=['--doc-javadoc-skip'],
                      extra_config={
                        'jar-publish': {
                          'publish_extras': {
                            'extra_test_jar_example': {
                              'override_name': '{0}-extra_example',
                              'classifier': 'classy',
                              },
                            },
                          },
                        'backends': {
                          'packages': [
                            'example.pants_publish_plugin',
                            ],
                          },
                        },
                      extra_env={'WRAPPER_SRCPATH': 'examples/src/python'})


  def publish_test(self, target, artifacts, extra_options=None, extra_config=None,
                   expected_primary_artifact_count=1, extra_env=None):
    """Tests that publishing the given target results in the expected output.

    :param target: Target to test.
    :param artifacts: A map from directories to a list of expected filenames.
    :param extra_options: Extra command-line options to the pants run.
    :param extra_config: Extra pants.ini configuration for the pants run.
    :param expected_primary_artifact_count: Number of artifacts we expect to be published.
    :param extra_env: Extra environment variables for the pants run."""

    with temporary_dir() as publish_dir:
      options = ['--publish-local=%s' % publish_dir,
                 '--no-publish-dryrun',
                 '--publish-force']
      if extra_options:
        options.extend(extra_options)

      yes = 'y' * expected_primary_artifact_count
      pants_run = self.run_pants(['goal', 'publish', target] + options, config=extra_config,
                                 stdin_data=yes, extra_env=extra_env)
      self.assertEquals(pants_run.returncode, self.PANTS_SUCCESS_CODE,
                        "goal publish expected success, got {0}\n"
                        "got stderr:\n{1}\n"
                        "got stdout:\n{2}\n".format(pants_run.returncode,
                                                    pants_run.stderr_data,
                                                    pants_run.stdout_data))
      for directory, artifact_list in artifacts.items():
        for artifact in artifact_list:
          artifact_path = os.path.join(publish_dir, directory, artifact)
          self.assertTrue(os.path.exists(artifact_path))
