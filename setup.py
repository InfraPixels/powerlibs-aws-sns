try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.0.1'

with open('requirements/production.txt') as requirements_file:
    requires = [line for line in requirements_file]

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='powerlibs-aws-sns',
    version=version,
    description="Python libraries to facilitate publishing on Amazon SNS",
    long_description=readme,
    author='Cléber Zavadniak',
    author_email='cleberman@gmail.com',
    url='https://github.com/Dronemapp/powerlibs-aws-sns',
    license=license,
    packages=['powerlibs.aws.sns'],
    package_data={'': ['LICENSE', 'README.md']},
    include_package_data=True,
    install_requires=requires,
    zip_safe=False,
    keywords='generic libraries',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ),
)
