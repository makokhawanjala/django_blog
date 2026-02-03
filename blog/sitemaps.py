# blog/sitemaps.py
from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    changefreq = "weekly"  # Tells search engines how often the content changes
    priority = 0.9          # Importance (1.0 = highest)

    def items(self):
        return Post.published.all()  # Only include published posts

    def lastmod(self, obj):
        return obj.updated  # Use the updated timestamp for freshness
