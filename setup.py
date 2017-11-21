from setuptools import setup, find_packages

requirements = [
    'click==6.7',
    'requests[security]>=2.9.1',
    'findup==0.3.0',
    'six==1.11.0',
    'bravado==9.2.0',
]

test_requirements = requirements + [
    'flake8==3.5.0',
]

setup(
    name='optimizely-cli',
    version='0.1',
    py_modules=['opti'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=requirements,
    tests_require=test_requirements,
    entry_points='''
        [console_scripts]
        optimizely = optimizely_cli:cli
    ''',
)
