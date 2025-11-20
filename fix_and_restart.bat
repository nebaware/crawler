@echo off
echo ========================================
echo FIXING AND RESTARTING APPLICATION
echo ========================================
echo.

echo Step 1: Stopping all services...
docker-compose down
echo.

echo Step 2: Starting database and redis...
docker-compose up -d db redis
echo Waiting 10 seconds for database to initialize...
timeout /t 10 /nobreak > nul
echo.

echo Step 3: Starting web service...
docker-compose up -d web
echo Waiting 5 seconds for web service...
timeout /t 5 /nobreak > nul
echo.

echo Step 4: Running database migrations...
docker-compose exec -T web python manage.py migrate
echo.

echo Step 5: Starting worker...
docker-compose up -d worker
echo.

echo Step 6: Checking status...
docker-compose ps
echo.

echo Step 7: Testing web service...
docker-compose exec -T web python manage.py check
echo.

echo ========================================
echo DONE! Opening browser...
echo ========================================
start http://localhost:8081
echo.
echo If browser shows nothing, run: check_status.bat
pause
