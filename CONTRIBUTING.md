# Contributing

## Fixes, Features and Changes

Send a pull request to the master branch. We'll generally want documentation and [tests](Tests/README.rst) for new features. Tests or documentation on their own are also welcomed. Feel free to ask questions as an [issue](https://github.com/python-pillow/Pillow/issues/new) or on IRC (irc.freenode.net, #pil)

- Fork the repo
- Make a branch from master
- Add your changes + Tests
- Run the test suite. Try to run on both Python 2.x and 3.x, or you'll get tripped up. You can enable [Travis CI on your repo](https://travis-ci.org/profile/) to catch test failures prior to the pull request, and [Coveralls](https://coveralls.io/repos/new) to see if the changed code is covered by tests.
- Push to your fork, and make a pull request onto master. 

A few guidelines:
- Try to keep any code commits clean and separate from reformatting commits.
- All new code is going to need tests. 
- Try to follow PEP8. 

## Bugs

When reporting bugs, please include example code that reproduces the issue, and if possible a problem image. The best reproductions are self-contained scripts that pull in as few dependencies as possible. An entire Django stack is harder to handle. 

Let us know:
- What did you do?
- What did you expect to happen?
- What actually happened?
- What versions of Pillow and Python are you using?
