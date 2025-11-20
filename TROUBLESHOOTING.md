# Troubleshooting Guide

## Problem: Browser Shows Nothing / Blank Page

### Step 1: Run Debug Script
```cmd
debug.bat
```

This will show you what's wrong.

### Step 2: Check if Services are Running

```cmd
docker-compose ps
```

**Expected Output:**
All services should show "Up" status:
- web (Up)
- worker (Up)
- db (Up)
- redis (Up)

**If services are not running:**
```cmd
docker-compose up -d
```

### Step 3: Check Web Service Logs

```cmd
docker-compose logs web
```

**Look for these issues:**

#### Issue A: Migration Error
If you see "no such table" or "relation does not exist":
```cmd
docker-compose exec web python manage.py migrate
```

#### Issue B: Database Connection Error
If you see "could not connect to server":
```cmd
docker-compose restart db
timeout /t 5 /nobreak
docker-compose restart web
```

#### Issue C: Port Already in Use
If you see "address already in use":
```cmd
REM Find what's using port 8081
netstat -ano | findstr :8081

REM Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

REM Restart
docker-compose restart web
```

### Step 4: Verify Web Server is Running

```cmd
docker-compose exec web python manage.py check
```

Should show: "System check identified no issues"

### Step 5: Test Direct Connection

```cmd
curl http://localhost:8081
```

Or open Command Prompt and run:
```cmd
powershell -Command "Invoke-WebRequest -Uri http://localhost:8081"
```

### Step 6: Check Browser

1. Try different browsers (Chrome, Firefox, Edge)
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try incognito/private mode
4. Try: http://127.0.0.1:8081 instead of localhost

## Common Issues & Solutions

### Issue: "docker-compose: command not found"

**Solution:**
```cmd
REM Use docker compose (without hyphen) for newer Docker versions
docker compose up -d
docker compose ps
docker compose logs web
```

### Issue: Services Keep Restarting

**Solution:**
```cmd
REM Check what's failing
docker-compose logs --tail=100

REM Complete reset
docker-compose down -v
docker-compose up -d
timeout /t 10 /nobreak
docker-compose exec web python manage.py migrate
```

### Issue: Database Migration Fails

**Solution:**
```cmd
REM Wait for database to be ready
timeout /t 10 /nobreak

REM Try migration again
docker-compose exec web python manage.py migrate

REM If still fails, reset database
docker-compose down -v
docker-compose up -d db
timeout /t 10 /nobreak
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Issue: "Error: No such service: web"

**Solution:**
```cmd
REM Make sure you're in the correct directory
cd /d %~dp0

REM Check if docker-compose.yml exists
dir docker-compose.yml

REM Start services
docker-compose up -d
```

### Issue: Blank Page / No CSS

**Solution:**
The templates should work without static files, but if you see unstyled content:

1. Check if Bootstrap CDN is loading (check browser console F12)
2. Check internet connection (Bootstrap loads from CDN)
3. Try hard refresh: Ctrl+F5

## Manual Verification Steps

### 1. Check Docker Desktop is Running
- Open Docker Desktop application
- Make sure it shows "Running" status

### 2. Verify Services One by One

```cmd
REM Start database first
docker-compose up -d db
timeout /t 5 /nobreak

REM Start redis
docker-compose up -d redis
timeout /t 3 /nobreak

REM Start web
docker-compose up -d web
timeout /t 5 /nobreak

REM Run migrations
docker-compose exec web python manage.py migrate

REM Start worker
docker-compose up -d worker
```

### 3. Test Database Connection

```cmd
docker-compose exec web python manage.py dbshell
```

Type `\q` to exit.

### 4. Test Django Shell

```cmd
docker-compose exec web python manage.py shell
```

Then type:
```python
from crawler.models import CrawledPage
print(CrawledPage.objects.count())
exit()
```

## Still Not Working?

### Complete Fresh Start

```cmd
REM Stop everything
docker-compose down -v

REM Remove all containers and images
docker system prune -a

REM Start fresh
docker-compose up -d

REM Wait for services
timeout /t 15 /nobreak

REM Run migrations
docker-compose exec web python manage.py migrate

REM Check status
docker-compose ps

REM View logs
docker-compose logs -f web
```

### Get Detailed Logs

```cmd
REM Save logs to file
docker-compose logs > logs.txt

REM Open the file and look for ERROR or CRITICAL messages
notepad logs.txt
```

## Contact Information

If none of these work, provide:
1. Output of `docker-compose ps`
2. Output of `docker-compose logs web`
3. Your Windows version
4. Docker Desktop version
