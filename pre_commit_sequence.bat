@echo off 

:start
cls

echo Running isort...
py -m isort .
echo Done!
echo.
echo.


echo Running black...
py -m black . -S  --line-length=88
echo Done!
echo.
echo.


echo Running pylint...
py -m pylint server.py --disable=C0116,C0114,E0401,C0413,C0103,C0115,I1101,E1101
echo Done!
echo.


set /p run_again="Would you like to rerun? (y/n) "

if "%run_again%" EQU "y" (
    goto :start
)

pause
