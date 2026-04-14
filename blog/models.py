from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, unique_for_date='publish')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)

    objects = models.Manager()       # The default manager.
    published = PublishedManager()   # Custom manager for published posts.
    tags = TaggableManager()         # Tagging functionality using django-taggit

    class Meta:
        ordering = ('-publish',)
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug,
        ])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'


# ── Pipeline 1: Transcript Queue ─────────────────────────────────────────────

class TranscriptQueue(models.Model):
    class Status(models.TextChoices):
        RAW = 'raw', 'Raw'
        PROCESSING = 'processing', 'Processing'
        DRAFT_CREATED = 'draft_created', 'Draft Created'
        FAILED = 'failed', 'Failed'

    video_id = models.CharField(max_length=50, unique=True)
    video_title = models.CharField(max_length=500)
    channel_id = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=200, blank=True)
    raw_transcript = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.RAW
    )
    draft_post = models.ForeignKey(
        Post, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='transcript_source'
    )
    error_message = models.TextField(blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-fetched_at',)

    def __str__(self):
        return f'{self.video_title} [{self.status}]'


# ── Pipeline 2: Social Opportunity ───────────────────────────────────────────

class SocialOpportunity(models.Model):
    class Platform(models.TextChoices):
        TWITTER = 'twitter', 'Twitter/X'
        REDDIT = 'reddit', 'Reddit'
        QUORA = 'quora', 'Quora'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        ACTIONED = 'actioned', 'Actioned'
        DISMISSED = 'dismissed', 'Dismissed'

    platform = models.CharField(max_length=20, choices=Platform.choices)
    post_url = models.URLField(unique=True)
    post_text = models.TextField()
    author = models.CharField(max_length=200, blank=True)
    engagement_count = models.IntegerField(default=0)
    relevance_score = models.FloatField(default=0.0)
    claude_reasoning = models.TextField(blank=True)
    draft_reply = models.TextField(blank=True)
    related_article = models.ForeignKey(
        Post, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='social_opportunities'
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    found_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-relevance_score', '-found_at')
        verbose_name_plural = 'Social Opportunities'

    def __str__(self):
        return f'[{self.platform}] {self.post_text[:80]}...'


# ── Pipeline 3: Comment Alert ─────────────────────────────────────────────────

class CommentAlert(models.Model):
    class Classification(models.TextChoices):
        SPAM = 'spam', 'Spam'
        LOW_VALUE = 'low_value', 'Low Value'
        WORTH_ENGAGING = 'worth_engaging', 'Worth Engaging'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        REPLIED = 'replied', 'Replied'
        DISMISSED = 'dismissed', 'Dismissed'

    comment = models.OneToOneField(
        Comment, on_delete=models.CASCADE, related_name='alert'
    )
    classification = models.CharField(
        max_length=20, choices=Classification.choices
    )
    claude_reasoning = models.TextField(blank=True)
    draft_reply = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    classified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-classified_at',)

    def __str__(self):
        return f'Alert: {self.comment} [{self.classification}]'