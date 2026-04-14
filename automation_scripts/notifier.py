import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_opportunity_digest(opportunities: list) -> None:
    """
    Sends an email digest of social reply opportunities.
    Each opportunity is a SocialOpportunity model instance.
    """
    if not opportunities:
        logger.info('No opportunities to send in digest')
        return

    lines = ['=== SOCIAL REPLY OPPORTUNITIES ===\n']
    for i, opp in enumerate(opportunities, 1):
        lines.append(f'--- Opportunity {i} ---')
        lines.append(f'Platform: {opp.platform.upper()}')
        lines.append(f'Score: {opp.relevance_score:.2f}')
        lines.append(f'Why: {opp.claude_reasoning}')
        lines.append(f'Post: {opp.post_url}')
        lines.append(f'Text: {opp.post_text[:200]}')
        lines.append(f'\nDRAFT REPLY (edit before posting):\n{opp.draft_reply}')
        if opp.related_article:
            lines.append(f'Related article: {opp.related_article.get_absolute_url()}')
        lines.append('')

    body = '\n'.join(lines)
    try:
        send_mail(
            subject=f'[machiavellimind] {len(opportunities)} Reply Opportunities',
            message=body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.NOTIFICATION_EMAIL],
            fail_silently=False,
        )
        logger.info(f'Digest email sent with {len(opportunities)} opportunities')
    except Exception as e:
        logger.error(f'Email send failed: {e}')


def send_weekly_analytics_brief(brief_text: str, week_start: str) -> None:
    """Sends the weekly analytics brief email."""
    try:
        send_mail(
            subject=f'[machiavellimind] Weekly Brief — {week_start}',
            message=brief_text,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.NOTIFICATION_EMAIL],
            fail_silently=False,
        )
        logger.info('Weekly brief email sent')
    except Exception as e:
        logger.error(f'Weekly brief email failed: {e}')