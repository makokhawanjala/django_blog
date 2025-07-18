from django import template
from blog.models import Post
import markdown
from django.utils.safestring import mark_safe

register = template.Library()
@register.simple_tag
def total_posts():
    """Returns the total number of published posts."""
    return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    """Returns the latest published posts."""
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

@register.filter(name = 'markdown')
def markdown_format(text):
    """Converts Markdown text to HTML."""
    return mark_safe(markdown.markdown(text))
