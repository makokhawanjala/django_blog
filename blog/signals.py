import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from blog.models import Post

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post)
def trigger_seo_on_publish(sender, instance, created, **kwargs):
    """
    Fires after every Post save. When a post transitions to Published status,
    queues SEO metadata generation via the process_seo management command.
    Does not block the save — runs in background thread.
    """
    if instance.status == Post.Status.PUBLISHED:
        import threading
        from automation_scripts.seo_processor import process_post_seo
        thread = threading.Thread(
            target=process_post_seo,
            args=(instance.id,),
            daemon=True
        )
        thread.start()
        logger.info(f'SEO processing queued for post {instance.id}: {instance.title}')