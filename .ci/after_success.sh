#!/bin/bash

# gather the coverage data
python3 -m pip install coverage
python3 -m coverage xml
