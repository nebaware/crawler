# Quick Start Guide

## Option 1: Using Startup Scripts (Recommended)

### Windows:
```cmd
start.bat
```

### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

## Option 2: Manual Docker Commands

### 1. Start all services:
```bash
docker-compose up -d
```

### 2. Run database migrations:
```bash
docker-compose exec web python manage.py migrate
```

### 3. Access the application:
Open your browser to: **http://localhost:8081**

## Verify Services are Running

```bash
docker-compose ps
```

You should see 4 services running:
- web (Django)
- worker (Celery)
- db (PostgreSQL)
- redis

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f worker
```

## Stop the Application

```bash
docker-compose down
```

## Troubleshooting

### Services won't start?
1. Make sure Docker Desktop is running
2. Check if ports 8081, 5432, 6379 are available
3. Try: `docker-compose down -v` then start again

### Database errors?
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Can't access http://localhost:8081?
- Wait 10-15 seconds for services to fully start
- Check logs: `docker-compose logs web`
- Verify port 8081 is not in use by another app

## What to Do After Starting

1. **Start a Crawl:**
   - Enter a URL like `https://example.com`
   - Click "Start Crawl"
   - Wait for results to appear

2. **Search Pages:**
   - Type a search query
   - View ranked results with highlighted snippets

3. **View Architecture:**
   - Click "View Crawler Architecture Slides"
   - Navigate through the presentation

## Scaling Workers

To crawl faster, scale up workers:

```bash
docker-compose up --scale worker=5 -d
```

## Create Admin User (Optional)

```bash
docker-compose exec web python manage.py createsuperuser
```

Then access admin at: http://localhost:8081/admin
