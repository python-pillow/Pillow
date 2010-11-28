from setuptools import setup


def read(file):
    return open(file, 'rb').read()

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
    url='http://github.org/collective/pillow',
    classifiers=[
        "Development Status :: 6 - Mature",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
        "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Multimedia :: Graphics :: Viewers",
        ],
    )
