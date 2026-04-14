from django.db import models
from blog.models import Post


class WeeklyDigest(models.Model):
    week_start = models.DateField(unique=True)
    analytics_summary = models.TextField()
    top_performing_article = models.CharField(max_length=500, blank=True)
    recommended_content_type = models.TextField(blank=True)
    search_console_insights = models.TextField(blank=True)
    raw_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-week_start',)
        verbose_name = 'Weekly Digest'

    def __str__(self):
        return f'Digest: week of {self.week_start}'


class PostSEO(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='seo')
    meta_description = models.CharField(max_length=200, blank=True)
    suggested_tags = models.JSONField(default=list)
    internal_link_notes = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Post SEO'

    def __str__(self):
        return f'SEO: {self.post.title}'