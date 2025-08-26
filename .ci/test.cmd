python.exe -c "from PIL import Image"
IF ERRORLEVEL 1 EXIT /B
python.exe -bb -m pytest -vv -x -W always --cov PIL --cov Tests --cov-report term --cov-report xml Tests
