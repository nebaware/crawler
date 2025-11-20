from django.shortcuts import render, redirect
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchHeadline, SearchVector
from django.contrib import messages
from .models import CrawledPage
from .tasks import crawl_page_task
import json
from celery import current_app

def home(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        try:
            search_query = SearchQuery(query)
            vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
            results = CrawledPage.objects.annotate(
                rank=SearchRank(vector, search_query),
                headline=SearchHeadline('content', search_query, start_sel='<mark>', stop_sel='</mark>')
            ).filter(rank__gte=0.1).order_by('-rank')
        except Exception as e:
            messages.error(request, f'Search error: {str(e)}')
    else:
        results = CrawledPage.objects.all().order_by('-crawled_at')[:20]

    return render(request, 'dashboard.html', {'results': results, 'query': query})

def start_crawl(request):
    if request.method == "POST":
        url = request.POST.get('url')
        print(f"DEBUG: Received crawl request for URL: {url}")
        if url:
            try:
                task = crawl_page_task.delay(url)
                print(f"DEBUG: Task created with ID: {task.id}")
                messages.success(request, f'✅ Crawl task started for: {url} (Task ID: {task.id})')
            except Exception as e:
                print(f"DEBUG: Error starting crawl: {str(e)}")
                messages.error(request, f'❌ Failed to start crawl: {str(e)}')
        else:
            messages.warning(request, '⚠️ Please provide a valid URL')
    return redirect('home')

def crawler_presentation(request):
    top_pages = CrawledPage.objects.order_by('-crawled_at')[:5]

    crawl_times = ["10:00", "10:05", "10:10", "10:15", "10:20"]
    crawl_counts = [5, 12, 18, 25, 30]

    # Try to get worker info, but don't fail if Celery is unavailable
    worker_names = []
    worker_task_counts = []
    try:
        i = current_app.control.inspect()
        active = i.active() or {}
        worker_names = list(active.keys())
        worker_task_counts = [len(active[w]) for w in worker_names]
    except Exception as e:
        # If Celery is not available, use mock data for presentation
        worker_names = ['worker@crawler-1', 'worker@crawler-2']
        worker_task_counts = [3, 5]

    return render(request, 'web_crawler_architecture.html', {
        'top_pages': top_pages,
        'crawl_times': json.dumps(crawl_times),
        'crawl_counts': json.dumps(crawl_counts),
        'worker_names': json.dumps(worker_names),
        'worker_task_counts': json.dumps(worker_task_counts),
    })
