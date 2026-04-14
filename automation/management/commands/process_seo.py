from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate SEO metadata for published posts that do not have it yet'

    def handle(self, *args, **options):
        from blog.models import Post
        from automation.models import PostSEO
        from automation_scripts.seo_processor import process_post_seo

        processed_ids = PostSEO.objects.values_list('post_id', flat=True)
        posts = Post.published.exclude(id__in=processed_ids)
        count = posts.count()
        self.stdout.write(f'Found {count} posts without SEO metadata')

        for post in posts:
            process_post_seo(post.id)
            self.stdout.write(f'  Processed: {post.title}')

        self.stdout.write(self.style.SUCCESS(f'Done. {count} posts processed.'))