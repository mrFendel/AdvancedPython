from setuptools import setup, find_packages
from sphinx.setup_command import BuildDoc

cmdclass = {'build_sphinx': BuildDoc}
name = 'AdvancedPython'
version = '0.1'

setup(
    name=name,
    version=version,
    author='mrFendel',
    cmdclass=cmdclass,
    packages=find_packages(),
    url='',
    license='MIT',
    author_email='novkov.ivan@physech.edu',
    description='AdvancedPythonCourse',
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'source_dir': ('setup.py', 'doc'),
            },
        'console_scripts': [
            'stem_cli_main = stem.cli_main:stem_cli_main'
        ]
    }
)
