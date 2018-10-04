@ECHO OFF
SETLOCAL

git branch

:PROMPT
SET /P ONMASTER=Are you on the master branch (y/n)?
IF /I "%ONMASTER%" NEQ "y" GOTO END

git fetch upstream
git merge upstream/master
git push origin master

:END
ENDLOCAL
