python.exe -c "from PIL import Image"
IF ERRORLEVEL 1 EXIT /B
python.exe -bb -m pytest -vv -x -W always Tests -m "isolated"
IF ERRORLEVEL 1 EXIT /B
python.exe -bb -m pytest -vv -x -W always Tests -m "not isolated" --numprocesses=logical --dist=worksteal --cov PIL --cov Tests --cov-report term --cov-report xml
