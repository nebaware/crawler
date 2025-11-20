@echo off
echo Checking application status...
echo.
echo === CONTAINER STATUS ===
docker-compose ps
echo.
echo === WEB SERVICE LOGS (Last 20 lines) ===
docker-compose logs --tail=20 web
echo.
echo Press any key to see full logs...
pause > nul
docker-compose logs web
