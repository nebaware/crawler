#!/usr/bin/env python
"""
Quick setup verification script for the Web Crawler project.
Run this to check if all components are properly configured.
"""

import os
import sys

def check_imports():
    """Check if all required packages are installed"""
    print("Checking Python packages...")
    required = [
        'django',
        'celery',
        'redis',
        'requests',
        'bs4',
        'psycopg2',
        'django_redis',
        'django_celery_results',
        'lxml'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✓ All packages installed\n")
    return True

def check_django_setup():
    """Check Django configuration"""
    print("Checking Django setup...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_engine.settings')
    
    try:
        import django
        django.setup()
        print("  ✓ Django configured")
        
        from django.conf import settings
        print(f"  ✓ Database: {settings.DATABASES['default']['ENGINE']}")
        print(f"  ✓ Celery Broker: {settings.CELERY_BROKER_URL}")
        print(f"  ✓ Cache Backend: {settings.CACHES['default']['BACKEND']}")
        
        return True
    except Exception as e:
        print(f"  ✗ Django setup failed: {e}")
        return False

def check_urls():
    """Check URL configuration"""
    print("\nChecking URL routes...")
    try:
        from django.urls import reverse
        
        routes = ['home', 'start_crawl', 'crawler_presentation']
        for route in routes:
            url = reverse(route)
            print(f"  ✓ {route}: {url}")
        
        return True
    except Exception as e:
        print(f"  ✗ URL check failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Web Crawler Setup Verification")
    print("=" * 60 + "\n")
    
    checks = [
        check_imports(),
        check_django_setup(),
        check_urls()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✓ All checks passed! Setup is complete.")
        print("\nNext steps:")
        print("1. Start services: docker-compose up -d")
        print("2. Run migrations: docker-compose exec web python manage.py migrate")
        print("3. Access dashboard: http://localhost:8081")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
    print("=" * 60)

if __name__ == '__main__':
    main()
