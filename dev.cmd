@echo off

WORKING_DIR=%USERPROFILE%\Desktop\Projects\DarkAgesAI
cd %WORKING_DIR%

start "npm" cmd /k "cd my-app && npm start"
start "uvicorn" cmd /k "cd fastapi && uvicorn main:app --reload"
start "nginx" cmd /k "cd nginx && nginx -c nginx.conf"
start "git" cmd /k "git status && echo Ready"



