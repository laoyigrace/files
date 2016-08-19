@echo off

for /f "delims=" %%i in ('"dir /b/a-d/s *.py*"') do (
echo %%i
yapf.exe --style pep8 -i %%i
)
rem yapf python files success!
pause