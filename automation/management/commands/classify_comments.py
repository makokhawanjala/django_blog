import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Classify new blog comments and flag worth-engaging ones'

    def handle(self, *args, **options):
        from automation_scripts.comment_classifier import (
            get_unclassified_comments, classify_and_store
        )

        comments = get_unclassified_comments()
        count = comments.count()
        self.stdout.write(f'Found {count} unclassified comments')

        classified = 0
        for comment in comments:
            classify_and_store(comment)
            classified += 1

        self.stdout.write(self.style.SUCCESS(f'Classified {classified} comments'))