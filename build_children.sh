#!/bin/bash

# Get last child project build number from branch named "latest"
BUILD_NUM=$(curl -s 'https://api.travis-ci.org/repos/python-pillow/pillow-wheels/branches/latest' | grep -o '^{"branch":{"id":[0-9]*,' | grep -o '[0-9]' | tr -d '\n')

# Restart last child project build
curl -X POST https://api.travis-ci.org/builds/$BUILD_NUM/restart --header "Authorization: token "$AUTH_TOKEN
