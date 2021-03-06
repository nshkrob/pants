# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

python_library(
  name = 'base',
  sources = ['test_base.py'],
  dependencies = [
    '3rdparty/python/twitter/commons:twitter.common.collections',
    'src/python/pants/backend/core/tasks:console_task',
    'src/python/pants/backend/core/tasks:task',
    'src/python/pants/base:cmd_line_spec_parser',
    'src/python/pants/base:target',
    'src/python/pants/commands:goal_runner',
    'src/python/pants/goal:context',
    'src/python/pants/goal:mkflag',
    'src/python/pants/goal',
    'tests/python/pants_test/base:context_utils',
    'tests/python/pants_test:base_test',
  ]
)

python_library(
  name = 'jvm_binary_test_base',
  sources = ['jvm_binary_test_base.py'],
  dependencies = [
    'tests/python/pants_test/jvm:jar_task_test_base',
  ]
)

python_test_suite(
  name = 'tasks',
  dependencies = [
    ':antlr_gen',
    ':binary_create',
    ':builddict',
    ':bundle_create',
    ':cache_manager',
    ':check_exclusives',
    ':check_published_deps',
    ':config',
    ':console_task',
    ':context',
    ':dependees',
    ':dependencies',
    ':depmap',
    ':detect_duplicates',
    ':filemap',
    ':filter',
    ':group_task',
    ':ivy_utils',
    ':jar_create',
    ':jar_publish',
    ':jar_task',
    ':jaxb_gen',
    ':jvm_run',
    ':jvm_task',
    ':jvmdoc_gen',
    ':list_goals',
    ':listtargets',
    ':markdown_to_html',
    ':minimal_cover',
    ':protobuf_gen',
    ':ragel_gen',
    ':roots',
    ':scrooge_gen',
    ':sorttargets',
    ':targets_help',
    ':what_changed',
    'tests/python/pants_test/tasks/jvm_compile/scala'
  ],
)

python_test_suite(
  name = 'integration',
  dependencies = [
    ':eclipse_integration',
    ':ensime_integration',
    ':idea_integration',
    ':ivy_resolve_integration',
    ':jar_publish_integration',
    ':jvm_bundle_integration',
    ':jvm_run_integration',
    ':markdown_to_html_integration',
    ':protobuf_integration',
    ':scala_repl_integration',
    'tests/python/pants_test/tasks/jvm_compile/java',
  ],
)

python_tests(
  name = 'antlr_gen',
  sources = ['test_antlr_gen.py'],
  dependencies = [
    '3rdparty/python/twitter/commons:twitter.common.dirutil',
    ':base',
    'src/python/pants/backend/codegen/targets:java',
    'src/python/pants/backend/codegen/tasks:antlr_gen',
    'tests/python/pants_test/jvm:nailgun_task_test_base',
  ],
)

python_tests(
  name = 'binary_create',
  sources = ['test_binary_create.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/jvm/tasks:binary_create',
  ]
)

python_tests(
  name = 'builddict',
  sources = ['test_builddict.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core:plugin',
    'src/python/pants/backend/core/tasks:builddictionary',
    'src/python/pants/backend/jvm:plugin',
    'src/python/pants/backend/python:plugin',
    'src/python/pants/goal',
    'src/python/pants/goal:task_registrar',
  ]
)

python_tests(
  name = 'bundle_create',
  sources = ['test_bundle_create.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/jvm/tasks:bundle_create',
  ]
)

python_tests(
  name = 'jvm_bundle_integration',
  sources = ['test_jvm_bundle_integration.py'],
  dependencies = [
    'src/python/pants/fs',
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'jvm_run_integration',
  sources = ['test_jvm_run_integration.py'],
  dependencies = [
    'src/python/pants/fs',
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'scala_repl_integration',
  sources = ['test_scala_repl_integration.py'],
  dependencies = [
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'cache_manager',
  sources = ['test_cache_manager.py'],
  dependencies = [
    ':base',
    'tests/python/pants_test/testutils',
    'src/python/pants/base:build_invalidator',
    'src/python/pants/base:cache_manager',
  ]
)

python_tests(
  name = 'check_exclusives',
  sources = ['test_check_exclusives.py'],
  dependencies = [
    ':base',
    'src/python/pants/base:config',
    'src/python/pants/goal:context',
    'src/python/pants/backend/core/tasks:check_exclusives',
    'src/python/pants/util:dirutil',
  ]
)

python_tests(
  name = 'check_published_deps',
  sources = ['test_check_published_deps.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/jvm/tasks:check_published_deps',
    'src/python/pants/base:build_file_aliases',
  ]
)

# XXX Uh shouldn't this be in base?
python_tests(
  name = 'config',
  sources = ['test_config.py'],
  dependencies = [
    ':base',
    'src/python/pants/base:config',
    'src/python/pants/util:contextutil',
  ]
)

python_tests(
  name = 'console_task',
  sources = ['test_console_task.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core/tasks:console_task',
  ]
)

# XXX this should be in goal
python_tests(
  name = 'context',
  sources = ['test_context.py'],
  dependencies = [
    ':base',
    'src/python/pants/base:config',
    'src/python/pants/goal:context',
  ]
)

python_tests(
  name = 'dependees',
  sources = ['test_dependees.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/codegen/targets:java',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/core/tasks:dependees',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/jvm/targets:scala',
    'src/python/pants/backend/python/targets:python',
    'src/python/pants/base:build_environment',
    'src/python/pants/base:build_file_aliases',
  ]
)

python_tests(
  name = 'dependencies',
  sources = ['test_dependencies.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/jvm/targets:scala',
    'src/python/pants/backend/jvm/tasks:dependencies',
    'src/python/pants/backend/python/targets:python',
    'src/python/pants/backend/python:python_requirement',
    'src/python/pants/base:exceptions',
  ]
)

python_tests(
  name = 'depmap',
  sources = ['test_depmap.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core:plugin',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/jvm:plugin',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/jvm/targets:scala',
    'src/python/pants/backend/jvm/tasks:depmap',
    'src/python/pants/backend/python:plugin',
    'src/python/pants/base:build_file_aliases',
  ]
)

python_tests(
  name = 'detect_duplicates',
  sources = ['test_detect_duplicates.py'],
  dependencies = [
    ':base',
    'src/python/pants/base:exceptions',
    'src/python/pants/backend/jvm/tasks:detect_duplicates',
    'src/python/pants/util:dirutil',
    'tests/python/pants_test/base:context_utils',
  ],
)

python_tests(
  name = 'filedeps',
  sources = ['test_filedeps.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/codegen/targets:java',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/jvm/targets:scala',
    'src/python/pants/backend/jvm/tasks:filedeps',
    'src/python/pants/base:build_file_aliases',
  ],
)

python_tests(
  name = 'filemap',
  sources = ['test_filemap.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core/tasks:filemap',
    'src/python/pants/base:source_root',
    'src/python/pants/backend/python/targets:python',
    'src/python/pants/base:build_file_aliases',
  ],
)

python_tests(
  name = 'filter',
  sources = ['test_filter.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/python/targets:python',
    'src/python/pants/backend/core/tasks:filter',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/base:build_file_aliases',
  ],
)

python_tests(
  name = 'idea_integration',
  sources = ['test_idea_integration.py'],
  dependencies = [
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'eclipse_integration',
  sources = ['test_eclipse_integration.py'],
  dependencies = [
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'ensime_integration',
  sources = ['test_ensime_integration.py'],
  dependencies = [
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'ivy_resolve_integration',
  sources = ['test_ivy_resolve_integration.py'],
  dependencies = [
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'ivy_utils',
  sources = ['test_ivy_utils.py'],
  dependencies = [
    'src/python/pants/backend/core:plugin',
    'src/python/pants/backend/jvm:plugin',
    'src/python/pants/backend/jvm:ivy_utils',
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:base_test',
    'tests/python/pants_test/base:context_utils',
  ]
)

python_tests(
  name = 'jar_create',
  sources = ['test_jar_create.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/android/targets:android',
    'src/python/pants/backend/codegen/targets:java',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/jvm/targets:scala',
    'src/python/pants/backend/jvm/tasks:jar_create',
    'src/python/pants/base:build_environment',
    'src/python/pants/base:build_file_aliases',
    'src/python/pants/base:source_root',
    'src/python/pants/goal:products',
    'src/python/pants/java:jar',
    'src/python/pants/util:contextutil',
    'src/python/pants/util:dirutil',
    'tests/python/pants_test/base:context_utils',
    'tests/python/pants_test/jvm:jar_task_test_base',
  ],
)

python_tests(
  name = 'jar_publish',
  sources = ['test_jar_publish.py'],
  dependencies = [
    '3rdparty/python:mock',
    ':base',
    'src/python/pants/backend/jvm/tasks:jar_publish',
    'src/python/pants/util:contextutil',
    'src/python/pants/util:dirutil',
  ],
)

python_tests(
  name = 'jar_publish_integration',
  sources = ['test_jar_publish_integration.py'],
  dependencies = [
    ':base',
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'list_goals',
  sources = ['test_list_goals.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core/tasks:list_goals',
    'src/python/pants/backend/core/tasks:common',
    'src/python/pants/goal',
    'src/python/pants/goal:task_registrar',
  ],
)

python_tests(
  name = 'listtargets',
  sources = ['test_listtargets.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core/tasks:listtargets',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/base:build_file_aliases',
    'src/python/pants/base:target',
  ],
)

python_tests(
  name = 'markdown_to_html',
  sources = ['test_markdown_to_html.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core/tasks:markdown_to_html',
  ]
)

python_tests(
  name='markdown_to_html_integration',
  sources=['test_markdown_to_html_integration.py'],
  dependencies=[
    'src/python/pants/backend/core/tasks:markdown_to_html',
    'src/python/pants/base:build_environment',
    'src/python/pants/util:dirutil',
    'tests/python/pants_test:int-test',
  ],
  coverage=[
    'pants.backend.core.tasks.markdown_to_html',
  ]
)

python_tests(
  name = 'minimal_cover',
  sources = ['test_minimal_cover.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/core/tasks:minimal_cover',
    'src/python/pants/backend/python/targets:python',
    'src/python/pants/base:build_file_aliases',
  ],
)

python_tests(
  name = 'protobuf_gen',
  sources = ['test_protobuf_gen.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/codegen/tasks:protobuf_gen',
    'src/python/pants/util:contextutil',
  ],
)

python_tests(
  name = 'protobuf_integration',
  sources = ['test_protobuf_integration.py'],
  dependencies = [
    'tests/python/pants_test:int-test',
  ],
)

python_tests(
  name = 'jaxb_gen',
  sources = ['test_jaxb_gen.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/codegen/tasks:jaxb_gen',
    'src/python/pants/backend/codegen/targets:java',
    'src/python/pants/util:contextutil',
  ],
)

python_tests(
  name = 'roots',
  sources = ['test_roots.py'],
  dependencies = [
    ':base',
    'src/python/pants/base:build_environment',
    'src/python/pants/base:target',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/core/tasks:roots',
  ],
)

python_tests(
  name = 'scrooge_gen',
  sources = ['test_scrooge_gen.py'],
  dependencies = [
    '3rdparty/python:mock',
    ':base',
    'src/python/pants/backend/codegen/targets:java',
    'src/python/pants/backend/codegen/tasks:scrooge_gen',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/base:build_file_aliases',
    'src/python/pants/base:exceptions',
  ],
)

python_tests(
  name = 'sorttargets',
  sources = ['test_sorttargets.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/python/targets:python',
    'src/python/pants/backend/core/tasks:sorttargets',
    'src/python/pants/base:build_file_aliases',
  ],
)

python_tests(
  name = 'targets_help',
  sources = ['test_targets_help.py'],
  dependencies = [
    ':base',
    'src/python/pants/base:build_environment',
    'src/python/pants/base:target',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/core/tasks:targets_help',
  ],
)

python_tests(
  name = 'what_changed',
  sources = ['test_what_changed.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/codegen/targets:java',
    'src/python/pants/backend/codegen/targets:python',
    'src/python/pants/backend/core/targets:common',
    'src/python/pants/backend/core/tasks:what_changed',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/python/targets:python',
    'src/python/pants/base:build_file_aliases',
    'src/python/pants/base:source_root',
    'src/python/pants/base:target',
  ],
)

python_tests(
  name = 'jar_task',
  sources = ['test_jar_task.py'],
  dependencies = [
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/jvm/tasks:jar_task',
    'src/python/pants/base:build_file_aliases',
    'src/python/pants/base:source_root',
    'src/python/pants/util:contextutil',
    'src/python/pants/util:dirutil',
    'tests/python/pants_test/jvm:jvm_tool_task_test_base',
  ]
)

python_tests(
  name = 'group_task',
  sources = ['test_group_task.py'],
  dependencies = [
    'src/python/pants/backend/core/tasks:check_exclusives',
    'src/python/pants/backend/core/tasks:group_task',
    'src/python/pants/backend/jvm/targets:java',
    'src/python/pants/backend/jvm/targets:scala',
    'src/python/pants/backend/python/targets:python',
    'src/python/pants/base:target',
    'src/python/pants/engine:engine',
    'tests/python/pants_test:base_test',
  ]
)

python_tests(
  name = 'jvm_run',
  sources = ['test_jvm_run.py'],
  dependencies = [
    ':base',
    'src/python/pants/backend/jvm/targets:jvm',
    'src/python/pants/backend/jvm/tasks:jvm_run',
    'src/python/pants/engine',
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:base_test',
  ]
)

python_tests(
  name = 'jvm_task',
  sources = ['test_jvm_task.py'],
  dependencies = [
    'src/python/pants/backend/core/tasks:check_exclusives',
    'src/python/pants/backend/jvm/tasks:jvm_task',
    'src/python/pants/util:dirutil',
    'tests/python/pants_test:base_test',
  ]
)

python_tests(
  name = 'jvmdoc_gen',
  sources = ['test_jvmdoc_gen.py'],
  dependencies = [
    'src/python/pants/backend/core/tasks:check_exclusives',
    'src/python/pants/backend/jvm/tasks:jvmdoc_gen',
    'src/python/pants/util:dirutil',
    'tests/python/pants_test:base_test',
  ]
)


python_tests(
  name = 'ragel_gen',
  sources = ['test_ragel_gen.py'],
  dependencies = [
    ':base',
    '3rdparty/python:mock',
    'src/python/pants/backend/codegen/targets:java',
    'src/python/pants/backend/codegen/tasks:ragel_gen',
    'src/python/pants/base:address',
    'src/python/pants/base:build_environment',
    'src/python/pants/base:build_file_aliases',
    'src/python/pants/goal:context',
    'src/python/pants/util:contextutil',
    'tests/python/pants_test:base_test',
  ],
)
