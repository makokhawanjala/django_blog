import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_unclassified_comments():
    """Returns Comment objects that do not yet have a CommentAlert record."""
    from blog.models import Comment, CommentAlert
    classified_ids = CommentAlert.objects.values_list('comment_id', flat=True)
    return Comment.objects.exclude(id__in=classified_ids).select_related('post')


def classify_and_store(comment) -> None:
    """Runs Claude classification on one comment and saves a CommentAlert."""
    from blog.models import CommentAlert
    from automation_scripts.claude_processor import classify_comment

    result = classify_comment(comment.body, comment.post.title)
    if not result:
        return

    CommentAlert.objects.create(
        comment=comment,
        classification=result.get('classification', 'low_value'),
        claude_reasoning=result.get('reasoning', ''),
        draft_reply=result.get('draft_reply', ''),
    )
    logger.info(f'Classified comment {comment.id} as {result.get("classification")}')