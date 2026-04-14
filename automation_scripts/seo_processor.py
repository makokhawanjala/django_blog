import logging

logger = logging.getLogger(__name__)


def process_post_seo(post_id: int) -> None:
    """
    Generates SEO metadata for a post and stores it in a PostSEO record.
    Called by the Django signal after a post is published.
    """
    from blog.models import Post
    from automation.models import PostSEO
    from automation_scripts.claude_processor import generate_seo_metadata

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        logger.error(f'Post {post_id} not found for SEO processing')
        return

    # Skip if SEO already generated
    if PostSEO.objects.filter(post=post).exists():
        return

    result = generate_seo_metadata(post.title, post.body)
    if not result:
        return

    PostSEO.objects.create(
        post=post,
        meta_description=result.get('meta_description', ''),
        suggested_tags=result.get('suggested_tags', []),
        internal_link_notes=result.get('internal_link_notes', ''),
    )
    logger.info(f'SEO metadata generated for post {post.id}: {post.title}')