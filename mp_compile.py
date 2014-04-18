# A monkey patch of the base distutils.ccompiler to use parallel builds
# Tested on 2.7, looks to be identical to 3.3.

from multiprocessing import Pool, cpu_count
from distutils.ccompiler import CCompiler
import os

# hideous monkeypatching.  but. but. but.
def _mp_compile_one(tp):
    (self, obj, build, cc_args, extra_postargs, pp_opts) = tp
    try:
        src, ext = build[obj]
    except KeyError:
        return
    self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
    return

def _mp_compile(self, sources, output_dir=None, macros=None,
                include_dirs=None, debug=0, extra_preargs=None,
                extra_postargs=None, depends=None):
    """Compile one or more source files.
    
    see distutils.ccompiler.CCompiler.compile for comments.
    """
    # A concrete compiler class can either override this method
    # entirely or implement _compile().
    
    macros, objects, extra_postargs, pp_opts, build = \
            self._setup_compile(output_dir, macros, include_dirs, sources,
                                depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)


    try:
        max_procs = int(os.environ.get('MAX_CONCURRENCY', cpu_count()))
    except:
        max_procs = None
    pool = Pool(max_procs)
    try:
        print ("Building using %d processes" % pool._processes)
    except: pass
    arr = [(self, obj, build, cc_args, extra_postargs, pp_opts) for obj in objects]
    results = pool.map_async(_mp_compile_one,arr)
    
    pool.close()
    pool.join()
    # Return *all* object filenames, not just the ones we just built.
    return objects

CCompiler.compile = _mp_compile
