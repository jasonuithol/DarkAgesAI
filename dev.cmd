@echo off

set "WORKING_DIR=%~dp0"
cd "%WORKING_DIR%"

rem Start the React frontend server
start "npm" cmd /k "cd react-app && npm install && npm start"

rem Start the FastAPI backend server
start "uvicorn" cmd /k "cd fastapi && pip_install.cmd && uvicorn main:app --reload"

rem Wait for the services to start
timeout /t 5 /nobreak >nul

rem Start the proxy server that glues the frontend and backend together
start "nginx" cmd /k "cd nginx && nginx -c nginx.conf"

rem Open the browser and check git status
start "git" cmd /k "start http://localhost && git status && echo Ready"

