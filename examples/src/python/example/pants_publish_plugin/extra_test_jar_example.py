import os

from pants.backend.jvm.targets.java_library import JavaLibrary
from pants.backend.jvm.tasks.jar_task import JarTask
from pants.util.dirutil import safe_mkdir

##
## See `Appendix A` in the 'publish' documentation:
##
##    http://pantsbuild.github.io/publish.html
##
## for tips on how to adapt this example task for your own custom publishing needs.
##
class ExtraTestJarExample(JarTask):

  def __init__(self, context, workdir):
    super(ExtraTestJarExample, self).__init__(context, workdir)

    self.context.products.require('java')


  def execute(self):
    safe_mkdir(self.workdir)
    targets = self.context.targets()

    def process(target):
      self.context.log.info("Processing target %s" % target)
      jar_name = "%s.%s-extra_example.jar" % (target.provides.org, target.provides.name)
      jar_path = os.path.join(self.workdir, jar_name)
      example_file_name = os.path.join(self.workdir, "example.txt")

      with self.open_jar(jar_path, overwrite=True, compressed=True) as open_jar:
        with open(example_file_name, 'w') as f:
          f.write("This is an example test file.\n")
        open_jar.write(os.path.join(self.workdir, example_file_name), "example.txt")

      # IMPORTANT: this string *must* match the string that you have set in pants.ini. Otherwise,
      # things mysteriously won't work.
      self.context.products.get('extra_test_jar_example').add(target, self.workdir).append(jar_name)
      self.context.log.info("Made a jar: %s" % jar_path)

    for target in targets:
      target.walk(process, predicate=lambda target: isinstance(target, JavaLibrary))
