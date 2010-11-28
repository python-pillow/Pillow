from setuptools import setup


def read(file):
    f = open(file, 'rb')
    return f.read()

NAME='pillow'
VERSION='1.3'

setup(
    name=NAME,
    version=VERSION,
    description='Python Imaging Library (fork)',
    long_description=(
        read('README.txt') +
        read('docs/INSTALL.txt') +
        read('docs/HISTORY.txt')),
    author='Alex Clark (fork author)',
    author_email='aclark@aclark.net',
    )
