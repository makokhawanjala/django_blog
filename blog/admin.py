from django.contrib import admin

from .models import Post, Comment, TranscriptQueue, SocialOpportunity, CommentAlert


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'status', 'publish', 'created', 'updated')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')


@admin.register(TranscriptQueue)
class TranscriptQueueAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'channel_id', 'status', 'fetched_at', 'processed_at')
    list_filter = ('status', 'fetched_at')
    search_fields = ('video_title', 'channel_id')
    readonly_fields = ('raw_transcript', 'fetched_at', 'processed_at', 'error_message')
    ordering = ('-fetched_at',)


@admin.register(SocialOpportunity)
class SocialOpportunityAdmin(admin.ModelAdmin):
    list_display = (
        'platform', 'short_text', 'engagement_count',
        'relevance_score', 'status', 'found_at'
    )
    list_filter = ('platform', 'status', 'found_at')
    search_fields = ('post_text', 'author')
    readonly_fields = (
        'platform', 'post_url', 'post_text', 'author',
        'engagement_count', 'relevance_score', 'claude_reasoning',
        'draft_reply', 'related_article', 'found_at'
    )
    ordering = ('-relevance_score', '-found_at')

    def short_text(self, obj):
        return obj.post_text[:80]
    short_text.short_description = 'Post'

    actions = ['mark_actioned', 'mark_dismissed']

    def mark_actioned(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='actioned', reviewed_at=timezone.now())
    mark_actioned.short_description = 'Mark selected as actioned'

    def mark_dismissed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='dismissed', reviewed_at=timezone.now())
    mark_dismissed.short_description = 'Mark selected as dismissed'


@admin.register(CommentAlert)
class CommentAlertAdmin(admin.ModelAdmin):
    list_display = ('comment', 'classification', 'status', 'classified_at')
    list_filter = ('classification', 'status', 'classified_at')
    readonly_fields = ('comment', 'classification', 'claude_reasoning', 'draft_reply', 'classified_at')
    ordering = ('-classified_at',)

    actions = ['mark_replied', 'mark_dismissed']

    def mark_replied(self, request, queryset):
        queryset.update(status='replied')
    mark_replied.short_description = 'Mark selected as replied'

    def mark_dismissed(self, request, queryset):
        queryset.update(status='dismissed')
    mark_dismissed.short_description = 'Mark selected as dismissed'