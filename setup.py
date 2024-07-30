from distutils.core import setup

setup(
   name = 'yifanhu',
   packages = ['yifanhu'],
   version = '0.1.0',
   license = 'GPLv3+',
   description = 'Python-friendly yifanhu library with networkx compatibility.',
   author = 'Ryan Rudes',
   author_email = 'ryanrudes@gmail.com',
   url = 'https://github.com/ryanrudes/forceatlas',
   download_url = 'https://github.com/phlawlessDevelopment/yifanhu/archive/refs/tags/v0.1.0.tar.gz',
   keywords = ['networkx', 'yifanhu', 'graph-layout', 'force-directed-graphs'],
   install_requires = ['networkx', 'pandas'],
   package_data = {
      "yifanhu": ["ext/yifanhu.jar", "ext/gephi-toolkit-0.9.2-all.jar"]
   }
)
