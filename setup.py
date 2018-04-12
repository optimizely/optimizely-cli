import sys
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))
__version__ = None

with open(os.path.join(here, 'optimizely_cli', 'version.py')) as _file:
    exec(_file.read())

requirements = [
    'click==6.7',
    'requests[security]>=2.9.1',
    'findup==0.3.0',
    'six==1.11.0',
    'bravado==9.2.0',
]

test_requirements = requirements + [
    'flake8==3.5.0',
    'pytest==3.5.0',
]


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


setup(
    name='optimizely-cli',
    version=__version__,
    py_modules=['opti'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=requirements,
    tests_require=test_requirements,
    cmdclass={
        # Pulled from py.test docs.
        'test': PyTest,
    },
    entry_points='''
        [console_scripts]
        opti = optimizely_cli:cli
    ''',
)
