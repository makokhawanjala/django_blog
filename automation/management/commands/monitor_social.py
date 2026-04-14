import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scan social platforms for reply opportunities and send digest'

    def handle(self, *args, **options):
        from blog.models import Post, SocialOpportunity
        from automation_scripts.social_monitor import collect_all_posts
        from automation_scripts.claude_processor import score_social_post
        from automation_scripts.notifier import send_opportunity_digest
        from automation_scripts.config import MIN_SCORE_THRESHOLD, MAX_OPPORTUNITIES_PER_DIGEST

        # Build article context for Claude scoring
        published = Post.published.all().order_by('-publish')[:10]
        articles = [
            {
                'id': p.id,
                'title': p.title,
                'url': f'https://machiavellimind.com{p.get_absolute_url()}'
            }
            for p in published
        ]

        self.stdout.write('Collecting posts from social platforms...')
        posts = collect_all_posts()
        self.stdout.write(f'Found {len(posts)} candidate posts')

        new_opportunities = []
        for post_data in posts:
            # Skip already stored
            if SocialOpportunity.objects.filter(post_url=post_data['post_url']).exists():
                continue

            score_result = score_social_post(
                post_data['post_text'],
                post_data['platform'],
                articles
            )
            score = score_result.get('score', 0.0)
            if score < MIN_SCORE_THRESHOLD:
                continue

            related = None
            related_id = score_result.get('related_article_id')
            if related_id:
                try:
                    related = Post.objects.get(id=related_id)
                except Post.DoesNotExist:
                    pass

            opp = SocialOpportunity.objects.create(
                platform=post_data['platform'],
                post_url=post_data['post_url'],
                post_text=post_data['post_text'],
                author=post_data.get('author', ''),
                engagement_count=post_data.get('engagement_count', 0),
                relevance_score=score,
                claude_reasoning=score_result.get('reasoning', ''),
                draft_reply=score_result.get('draft_reply', ''),
                related_article=related,
            )
            new_opportunities.append(opp)
            self.stdout.write(f'  Opportunity [{score:.2f}]: {post_data["platform"]} — {post_data["post_text"][:60]}')

        # Send digest email with top opportunities
        if new_opportunities:
            top = sorted(new_opportunities, key=lambda x: x.relevance_score, reverse=True)
            top = top[:MAX_OPPORTUNITIES_PER_DIGEST]
            send_opportunity_digest(top)
            self.stdout.write(self.style.SUCCESS(f'Digest sent: {len(top)} opportunities'))
        else:
            self.stdout.write('No new opportunities found above threshold')