#!/bin/bash

set -e

coverage erase
make clean
make install-coverage
