import time
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch YouTube transcripts and create draft posts via Claude'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backfill',
            action='store_true',
            help='Fetch ALL videos from each channel (no date filter). Safe to re-run — skips already processed video IDs.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=200,
            help='Max videos to fetch per channel when using --backfill (default: 200)',
        )

    def handle(self, *args, **options):
        from blog.models import Post, TranscriptQueue
        from automation_scripts.transcript_fetcher import (
            get_recent_video_ids, get_all_video_ids, fetch_transcript, FETCH_DELAY
        )
        from automation_scripts.claude_processor import clean_transcript_to_draft

        author = User.objects.get(id=settings.BLOG_AUTHOR_ID)
        channels = settings.MONITORED_CHANNELS
        backfill = options['backfill']
        limit = options['limit']

        if not channels:
            self.stdout.write('No channels configured in MONITORED_CHANNELS')
            return

        if backfill:
            self.stdout.write(
                self.style.WARNING(f'Backfill mode: fetching up to {limit} videos per channel.')
            )

        new_count = 0
        for channel_id in channels:
            self.stdout.write(f'Checking channel {channel_id}...')

            if backfill:
                videos = get_all_video_ids(channel_id, limit=limit)
            else:
                videos = get_recent_video_ids(channel_id, days_back=1)

            self.stdout.write(f'  Found {len(videos)} videos.')

            for video in videos:
                video_id = video['video_id']
                title = video['title']

                # Skip already processed
                if TranscriptQueue.objects.filter(video_id=video_id).exists():
                    self.stdout.write(f'  Skipping (already in queue): {title}')
                    continue

                self.stdout.write(f'  New video: {title}')
                transcript = fetch_transcript(video_id)
                time.sleep(FETCH_DELAY)  # avoid YouTube 429s
                if not transcript:
                    TranscriptQueue.objects.create(
                        video_id=video_id,
                        video_title=title,
                        channel_id=channel_id,
                        raw_transcript='',
                        status=TranscriptQueue.Status.FAILED,
                        error_message='No transcript available'
                    )
                    continue

                queue_entry = TranscriptQueue.objects.create(
                    video_id=video_id,
                    video_title=title,
                    channel_id=channel_id,
                    raw_transcript=transcript,
                    status=TranscriptQueue.Status.PROCESSING
                )

                # Send to Claude for cleaning
                result = clean_transcript_to_draft(transcript, title)
                if not result or not result.get('body'):
                    queue_entry.status = TranscriptQueue.Status.FAILED
                    queue_entry.error_message = 'Claude returned empty result'
                    queue_entry.save()
                    continue

                # Create Django draft post
                slug_base = slugify(result['title'])[:200]
                slug = slug_base
                counter = 1
                while Post.objects.filter(slug=slug).exists():
                    slug = f'{slug_base}-{counter}'
                    counter += 1

                draft = Post.objects.create(
                    title=result['title'],
                    slug=slug,
                    author=author,
                    body=result['body'],
                    status=Post.Status.DRAFT,
                    publish=timezone.now()
                )
                # Add tags
                for tag in result.get('tags', '').split(','):
                    tag = tag.strip()
                    if tag:
                        draft.tags.add(tag)

                queue_entry.status = TranscriptQueue.Status.DRAFT_CREATED
                queue_entry.draft_post = draft
                queue_entry.processed_at = timezone.now()
                queue_entry.save()

                new_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  Draft created: "{draft.title}" (ID: {draft.id})')
                )

        self.stdout.write(self.style.SUCCESS(f'Done. {new_count} new drafts created.'))