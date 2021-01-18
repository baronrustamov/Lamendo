@echo off 

:start
cls

echo Running isort...
isort ./app
echo Done!
echo.
echo.


echo Running black...
py -m black ./app -S  --line-length=88
echo Done!
echo.
echo.


echo Running pylint...
py -m pylint ./app/main.py --disable=C0116,C0114,E0401,C0413,C0103,C0115,I1101,E1101,E0611,C0411
echo Done!
echo.


set /p run_again="Would you like to rerun? (y/n) "

if "%run_again%" EQU "y" (
    goto :start
)

pause
