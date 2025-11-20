# 🚀 Distributed Web Crawler & Search Engine

A production-ready web crawler built with Django, Celery, Redis, and PostgreSQL featuring full-text search capabilities.

## Features

- **Distributed Crawling**: Celery workers for concurrent page processing
- **Full-Text Search**: PostgreSQL FTS with relevance ranking and highlighting
- **Politeness**: Per-domain rate limiting to respect server resources
- **Deduplication**: 24-hour cache to prevent duplicate crawls
- **Resilience**: Task persistence and automatic retries
- **Scalability**: Horizontal scaling with Docker Compose
- **Interactive Presentation**: Built-in architecture slides

## Architecture

```
User → Django (Web UI) → Redis (Task Queue) → Celery Workers → PostgreSQL (Storage + Search)
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)

### 1. Start Services

```bash
docker-compose up -d
```

This starts:
- Django web server (port 8081)
- Celery worker
- PostgreSQL database
- Redis broker

### 2. Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### 3. Access the Application

Open your browser to: **http://localhost:8081**

## Usage

### Start a Crawl

1. Enter a URL in the dashboard (e.g., `https://example.com`)
2. Click "Start Crawl"
3. The system will crawl the page and follow links (up to 2 levels deep)

### Search Indexed Pages

1. Type your search query in the search box
2. Results are ranked by relevance
3. Search snippets highlight matching keywords

### View Architecture Slides

Click "View Crawler Architecture Slides" to see the interactive presentation explaining the system design.

## Scaling

Scale workers horizontally for faster crawling:

```bash
docker-compose up --scale worker=5 -d
```

## Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Setup

```bash
python test_setup.py
```

### Run Locally (without Docker)

1. Start PostgreSQL and Redis locally
2. Update environment variables in `search_engine/settings.py`
3. Run migrations: `python manage.py migrate`
4. Start Django: `python manage.py runserver`
5. Start Celery: `celery -A search_engine worker --loglevel=info`

## Project Structure

```
.
├── crawler/                    # Main Django app
│   ├── models.py              # CrawledPage model with FTS
│   ├── views.py               # Dashboard and presentation views
│   ├── tasks.py               # Celery crawling tasks
│   ├── urls.py                # URL routing
│   └── templates/             # HTML templates
│       ├── dashboard.html     # Main UI
│       └── web_crawler_architecture.html  # Presentation
├── search_engine/             # Django project settings
│   ├── settings.py            # Configuration
│   ├── celery.py              # Celery setup
│   └── urls.py                # Root URL config
├── docker-compose.yml         # Service orchestration
├── Dockerfile                 # Container definition
└── requirements.txt           # Python dependencies
```

## Key Technologies

- **Django 4.0+**: Web framework and ORM
- **Celery 5.2+**: Distributed task queue
- **Redis 6+**: Message broker and cache
- **PostgreSQL 16**: Database with Full-Text Search
- **BeautifulSoup4**: HTML parsing
- **Docker**: Containerization

## Configuration

Environment variables (set in `docker-compose.yml`):

- `DB_HOST`: PostgreSQL host
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASS`: Database password
- `CELERY_BROKER`: Redis connection URL

## Troubleshooting

### Check service status
```bash
docker-compose ps
```

### View logs
```bash
docker-compose logs -f web
docker-compose logs -f worker
```

### Reset database
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

## License

Educational project for demonstration purposes.
