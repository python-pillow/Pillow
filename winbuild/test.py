#!/usr/bin/env python3

import subprocess, os, multiprocessing, glob

from config import *

def test_one(params):
    python, architecture = params
    try:
        print ("Running: %s, %s" %params)
        command = [r'%s\%s%s\Scripts\python.exe' % (VIRT_BASE, python, architecture),
                   'test-installed.py',
                   '--processes=-0',
                   '--process-timeout=30',
                   ]
        command.extend(glob.glob('Tests/test*.py'))
        proc = subprocess.Popen(command, 
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        (trace, stderr) = proc.communicate()
        status = proc.returncode
        print ("Done with %s, %s -- %s" % (python, architecture, status ))
        return (python, architecture, status, trace)
    except Exception as msg:
        print ("Error with %s, %s: %s" % (python, architecture, msg))
        return (python, architecture, -1, str(msg))


if __name__=='__main__':

    os.chdir('..')
    pool = multiprocessing.Pool()
    matrix = [(python, architecture)  for python in pythons 
                                  for architecture in ('', 'x64')]

    results = pool.map(test_one, matrix)

    for (python, architecture, status, trace) in results:
        print ("%s%s: %s" % (python, architecture, status))

        
        
                            

               
