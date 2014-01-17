#!/usr/bin/env python
from livereload.task import Task
from livereload.compiler import shell

Task.add('*.rst', shell('make html'))
Task.add('*/*.rst', shell('make html'))
Task.add('_static/*.css', shell('make clean html'))
Task.add('_templates/*', shell('make clean html'))
Task.add('Makefile', shell('make html'))
Task.add('conf.py', shell('make html'))
