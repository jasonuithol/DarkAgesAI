@echo off

set "WORKING_DIR=%~dp0"
cd "%WORKING_DIR%"

echo Starting the React frontend server
start "npm" cmd /k "color 04 && cd react-app && npm install && npm start && title npm"

echo Starting the FastAPI backend server
set "FASTAPI_DIR=%WORKING_DIR%\fastapi"
cd "%FASTAPI_DIR%"
if not exist save ( 
    mkdir save 
)
start "uvicorn" cmd /k "color 1e & cd %FASTAPI_DIR% & pip install -r requirements.txt & uvicorn main:app --reload"

echo Starting the proxy server that glues the frontend and backend together
set "NGINX_DIR=%WORKING_DIR%\nginx"
cd "%NGINX_DIR%"
if not exist logs ( 
    mkdir logs 
)
if not exist temp ( 
    mkdir temp 
)
taskkill /IM nginx.exe /F >nul 2>&1
start "nginx" cmd /k "color 0a & cd %NGINX_DIR% & nginx -t && echo launching application proxy (nginx) && nginx"

echo Waiting 30 seconds for the services to start
timeout /t 5 /nobreak >nul

echo Waiting 25 seconds for the services to start
timeout /t 5 /nobreak >nul

echo Waiting 20 seconds for the services to start
timeout /t 5 /nobreak >nul

echo Waiting 15 seconds for the services to start
timeout /t 5 /nobreak >nul

echo Waiting 10 seconds for the services to start
timeout /t 5 /nobreak >nul

echo Waiting 5 seconds for the services to start
timeout /t 5 /nobreak >nul

echo Starting web browser (http://localhost)
start "general" cmd /k "color 0e & start http://localhost & echo Use this window to run `taskkill /IM (process name) /F` or other business."

echo Press any key to close this window
pause >nul

rem TODO: Kill all the processes opened by this script here.
