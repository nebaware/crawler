@echo off
echo ========================================
echo DEBUGGING WEB CRAWLER APPLICATION
echo ========================================
echo.

echo 1. Checking Docker status...
docker --version
echo.

echo 2. Checking running containers...
docker-compose ps
echo.

echo 3. Checking web service logs (last 50 lines)...
docker-compose logs --tail=50 web
echo.

echo 4. Checking worker service logs (last 30 lines)...
docker-compose logs --tail=30 worker
echo.

echo 5. Checking if port 8081 is in use...
netstat -ano | findstr :8081
echo.

echo 6. Checking database connection...
docker-compose exec -T db pg_isready -U postgres
echo.

echo 7. Checking Redis connection...
docker-compose exec -T redis redis-cli ping
echo.

echo ========================================
echo DEBUG COMPLETE
echo ========================================
pause
