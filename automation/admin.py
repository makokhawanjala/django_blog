from django.contrib import admin
from automation.models import WeeklyDigest, PostSEO


@admin.register(WeeklyDigest)
class WeeklyDigestAdmin(admin.ModelAdmin):
    list_display = ('week_start', 'top_performing_article', 'created_at')
    readonly_fields = (
        'week_start', 'analytics_summary', 'top_performing_article',
        'recommended_content_type', 'search_console_insights', 'raw_data', 'created_at'
    )
    ordering = ('-week_start',)


@admin.register(PostSEO)
class PostSEOAdmin(admin.ModelAdmin):
    list_display = ('post', 'meta_description', 'generated_at')
    readonly_fields = ('post', 'meta_description', 'suggested_tags', 'internal_link_notes', 'generated_at')
    ordering = ('-generated_at',)