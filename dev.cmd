@echo off

set "WORKING_DIR=%~dp0"
cd "%WORKING_DIR%"

rem Start the React frontend server
start "npm" cmd /k "color 04 && cd react-app && npm install && npm start && title npm"

rem Start the FastAPI backend server
start "uvicorn" cmd /k "color 1e && cd fastapi && pip_install.cmd && if not exist save mkdir save && uvicorn main:app --reload"

rem Start the proxy server that glues the frontend and backend together
start "nginx" cmd /k "color 0a && cd nginx && if not exist logs mkdir logs && if not exist temp mkdir temp && nginx -c nginx.conf"

rem Wait for the services to start
timeout /t 15 /nobreak >nul

rem Open the browser and check git status
start "general" cmd /k "color 0e && start http://localhost && echo Ready"

