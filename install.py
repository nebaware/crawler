import os

# --- Project Structure & Content ---

files = {
    # 1. Docker Configuration
    "docker-compose.yml": r"""
version: '3.8'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DB_HOST=db
      - DB_NAME=postgres
      - DB_USER=postgres
      - DB_PASS=supersecretpassword
      - CELERY_BROKER=redis://redis:6379/0

  worker:
    build: .
    command: celery -A search_engine worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DB_HOST=db
      - DB_NAME=postgres
      - DB_USER=postgres
      - DB_PASS=supersecretpassword
      - CELERY_BROKER=redis://redis:6379/0

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=supersecretpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

volumes:
  postgres_data:
""",

    "Dockerfile": r"""
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Postgres and C compilers
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
""",

    "requirements.txt": r"""
Django>=4.0
psycopg2-binary>=2.9
celery>=5.2
redis>=4.0
requests>=2.27
beautifulsoup4>=4.10
""",

    # 2. Manage.py
    "manage.py": r"""
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_engine.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",

    # 3. Project Settings (search_engine/)
    "search_engine/__init__.py": r"""
from .celery import app as celery_app
__all__ = ('celery_app',)
""",

    "search_engine/celery.py": r"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_engine.settings')

app = Celery('search_engine')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
""",

    "search_engine/urls.py": r"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crawler.urls')),
]
""",

    "search_engine/wsgi.py": r"""
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_engine.settings')
application = get_wsgi_application()
""",

    "search_engine/settings.py": r"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-production-key-change-me'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres', # Required for Search
    'crawler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'search_engine.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'search_engine.wsgi.application'

# Database (Configured for Docker)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'supersecretpassword')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': '5432',
    }
}

# Celery Settings
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

# Cache (Using Redis)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CELERY_BROKER_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
""",

    # 4. App Files (crawler/)
    "crawler/__init__.py": "",
    "crawler/admin.py": "from django.contrib import admin\nfrom .models import CrawledPage\nadmin.site.register(CrawledPage)",
    "crawler/apps.py": "from django.apps import AppConfig\nclass CrawlerConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'crawler'",

    "crawler/models.py": r"""
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector

class CrawledPage(models.Model):
    url = models.URLField(unique=True, max_length=1000)
    title = models.CharField(max_length=1000, null=True, blank=True)
    content = models.TextField(blank=True)
    status_code = models.IntegerField(default=200)
    crawled_at = models.DateTimeField(auto_now_add=True)
    
    # Postgres Full Text Search Field
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update search index
        CrawledPage.objects.filter(pk=self.pk).update(
            search_vector=(
                SearchVector('title', weight='A') + 
                SearchVector('content', weight='B')
            )
        )

    def __str__(self):
        return self.title or self.url
""",

    "crawler/tasks.py": r"""
from celery import shared_task
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from django.core.cache import cache
from .models import CrawledPage

@shared_task(bind=True, max_retries=3)
def crawl_page_task(self, url, depth=0, max_depth=2):
    # 1. Check if already visited
    # We use a cache lock to prevent infinite recursion loops
    if not cache.add(f"visited:{url}", "true", timeout=60*60*24):
        return f"Already visited: {url}"

    print(f"Crawling: {url}")

    try:
        # 2. Rate Limiting per domain
        domain = urlparse(url).netloc
        if cache.get(f"lock:{domain}"):
            # Retry later if domain is busy
            raise self.retry(countdown=2)
        
        cache.set(f"lock:{domain}", "true", timeout=1) # 1 sec polite delay

        # 3. Download
        headers = {'User-Agent': 'MySearchEngineBot/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 4. Save
            title = soup.title.string if soup.title else "No Title"
            text = soup.get_text(separator=' ', strip=True)[:10000]
            
            CrawledPage.objects.update_or_create(
                url=url,
                defaults={'title': title, 'content': text, 'status_code': 200}
            )

            # 5. Recurse
            if depth < max_depth:
                for link in soup.find_all('a', href=True):
                    abs_link = urljoin(url, link['href'])
                    # Only follow links on same domain for this demo
                    if urlparse(abs_link).netloc == domain:
                        crawl_page_task.delay(abs_link, depth + 1, max_depth)
            
            return f"Success: {url}"
    
    except Exception as exc:
        print(f"Failed {url}: {exc}")
        return f"Failed: {url}"
""",

    "crawler/urls.py": r"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crawl/', views.start_crawl, name='start_crawl'),
]
""",

    "crawler/views.py": r"""
from django.shortcuts import render, redirect
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, SearchHeadline
from .models import CrawledPage
from .tasks import crawl_page_task

def home(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Full Text Search Logic
        search_query = SearchQuery(query)
        vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
        
        results = CrawledPage.objects.annotate(
            rank=SearchRank(vector, search_query),
            headline=SearchHeadline('content', search_query, start_sel='<mark>', stop_sel='</mark>')
        ).filter(rank__gte=0.1).order_by('-rank')
    else:
        results = CrawledPage.objects.all().order_by('-crawled_at')[:20]

    return render(request, 'dashboard.html', {'results': results, 'query': query})

def start_crawl(request):
    if request.method == "POST":
        url = request.POST.get('url')
        if url:
            crawl_page_task.delay(url)
    return redirect('home')
""",

    "crawler/templates/dashboard.html": r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Search Engine</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style> mark { background-color: #fff3cd; padding: 0 2px; } </style>
</head>
<body class="bg-light">
<div class="container py-5">
    <h1 class="text-center mb-4">🚀 Distributed Web Crawler</h1>

    <div class="card shadow-sm p-4 mb-4">
        <form action="{% url 'start_crawl' %}" method="POST" class="d-flex gap-2">
            {% csrf_token %}
            <input type="url" name="url" class="form-control" placeholder="https://example.com" required>
            <button class="btn btn-primary">Start Crawl</button>
        </form>
    </div>

    <form method="GET" class="mb-4">
        <div class="input-group">
            <input type="text" name="q" class="form-control" placeholder="Search indexed pages..." value="{{ query }}">
            <button class="btn btn-success">Search</button>
        </div>
    </form>

    <div class="card shadow-sm">
        <div class="card-body">
            <table class="table table-hover">
                <thead>
                    <tr><th>Rank</th><th>Title / Snippet</th><th>URL</th></tr>
                </thead>
                <tbody>
                    {% for page in results %}
                    <tr>
                        <td>{{ page.rank|default:"-"|floatformat:2 }}</td>
                        <td>
                            <strong>{{ page.title|truncatechars:60 }}</strong><br>
                            <small class="text-muted">{{ page.headline|safe|default:page.content|truncatechars:100 }}</small>
                        </td>
                        <td><a href="{{ page.url }}" target="_blank">Link</a></td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="3" class="text-center">No results found.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""
}

def install():
    print("Installing Search Engine Project...")
    for filepath, content in files.items():
        # Create directories if they don't exist
        dirname = os.path.dirname(filepath)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        
        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
            print(f"Created: {filepath}")
            
    print("\nInstallation Complete! ✅")
    print("------------------------------------------------")
    print("HOW TO RUN:")
    print("1. Ensure you have Docker Installed.")
    print("2. Run command: docker-compose up --build")
    print("3. Open http://localhost:8000 in your browser.")
    print("4. Note: First run takes time (building containers).")
    print("5. Note: You need to run migrations once DB is up.")
    print("   Run: docker-compose exec web python manage.py migrate")

if __name__ == "__main__":
    install()