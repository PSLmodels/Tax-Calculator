@ECHO OFF
SETLOCAL

git branch

:PROMPT
SET /P ONMASTER=Are you on the master branch (y/n)?
IF /I "%ONMASTER%" NEQ "y" GOTO END

:PR-NUMBER
SET PRNUM=%1
IF "%PRNUM%" EQU "" GOTO ERROR

git fetch upstream pull/%PRNUM%/head:pr-%PRNUM%
git checkout pr-%PRNUM%
git status

:ERROR
ECHO Error: must specify PR number on command line
:END
ENDLOCAL
