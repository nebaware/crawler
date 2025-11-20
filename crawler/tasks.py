from celery import shared_task
import requests
from bs4 import BeautifulSoup
from .models import CrawledPage

@shared_task
def crawl_page_task(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
        # Parse HTML to extract title
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else url
        
        # Extract text content (remove scripts and styles)
        for script in soup(["script", "style"]):
            script.decompose()
        content = soup.get_text(separator=' ', strip=True)
        
        CrawledPage.objects.update_or_create(
            url=url,
            defaults={
                'title': title[:1000],  # Limit title length
                'content': content[:50000],  # Limit content length
                'status_code': response.status_code
            }
        )
        return f"Successfully crawled: {url}"
    except Exception as e:
        error_msg = f"Crawl failed for {url}: {str(e)}"
        print(error_msg)
        return error_msg
