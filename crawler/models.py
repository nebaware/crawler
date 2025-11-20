from django.db import models
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex

class CrawledPage(models.Model):
    url = models.URLField(unique=True, max_length=1000, db_index=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    content = models.TextField(blank=True)
    status_code = models.IntegerField(default=200)
    crawled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['-crawled_at']),
        ]
        ordering = ['-crawled_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        CrawledPage.objects.filter(pk=self.pk).update(
            search_vector=SearchVector('title', weight='A') + SearchVector('content', weight='B')
        )

    def __str__(self):
        return self.title or self.url
