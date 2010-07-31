from distutils.core import setup, Extension

PIL_BUILD_DIR   = '..'
PIL_IMAGING_DIR = PIL_BUILD_DIR+'/libImaging'

defs = []
try:
    import numarray
    defs.append(('WITH_NUMARRAY',None))
except ImportError:
    pass

sane = Extension('_sane',
                 include_dirs = [PIL_IMAGING_DIR],
                 libraries = ['sane'],
                 library_dirs = [PIL_IMAGING_DIR],
                 define_macros = defs,
                 sources = ['_sane.c'])

setup (name = 'pysane',
       version = '2.0',
       description = 'This is the pysane package',
       py_modules = ['sane'],
       ext_modules = [sane])
