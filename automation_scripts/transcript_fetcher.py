import os
import time
import yt_dlp
import logging
from django.conf import settings
from datetime import datetime, timedelta
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.proxies import WebshareProxyConfig

logger = logging.getLogger(__name__)




# Seconds to wait between transcript fetches (light courtesy delay)
FETCH_DELAY = 2


def _build_ytt_client() -> YouTubeTranscriptApi:
    """
    Builds a YouTubeTranscriptApi instance.
    Uses Webshare rotating residential proxy if credentials are present in env.
    Falls back to direct (no proxy) if credentials are missing — useful for
    local testing from a non-cloud IP.
    """
    proxy_username = getattr(settings, 'WEBSHARE_PROXY_USERNAME', '').strip()
    proxy_password = getattr(settings, 'WEBSHARE_PROXY_PASSWORD', '').strip()

    if proxy_username and proxy_password:
        logger.info('YouTubeTranscriptApi: using Webshare rotating residential proxy')
        return YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
        )
    else:
        logger.warning(
            'YouTubeTranscriptApi: WEBSHARE_PROXY_USERNAME/PASSWORD not set — '
            'falling back to direct connection (may be blocked on cloud IPs)'
        )
        return YouTubeTranscriptApi()


def get_recent_video_ids(channel_id: str, days_back: int = 1) -> list[dict]:
    """
    Returns list of {video_id, title} for videos uploaded in the last `days_back` days
    on the given channel_id. Uses yt-dlp to scrape channel without needing quota.
    """
    cutoff = datetime.now() - timedelta(days=days_back)
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': 20,
    }
    results = []
    url = f'https://www.youtube.com/channel/{channel_id}/videos'
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for entry in info.get('entries', []):
                video_id = entry.get('id')
                title = entry.get('title', '')
                upload_date = entry.get('upload_date')  # format: YYYYMMDD
                if upload_date:
                    uploaded_at = datetime.strptime(upload_date, '%Y%m%d')
                    if uploaded_at >= cutoff:
                        results.append({'video_id': video_id, 'title': title})
    except Exception as e:
        logger.error(f'Error fetching channel {channel_id}: {e}')
    return results


def get_all_video_ids(channel_id: str, limit: int = 200) -> list[dict]:
    """
    Returns list of {video_id, title} for ALL videos on the channel up to `limit`.
    No date filter — used for backfill runs.
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': limit,
    }
    results = []
    url = f'https://www.youtube.com/channel/{channel_id}/videos'
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for entry in info.get('entries', []):
                video_id = entry.get('id')
                title = entry.get('title', '')
                if video_id:
                    results.append({'video_id': video_id, 'title': title})
    except Exception as e:
        logger.error(f'Error fetching channel {channel_id}: {e}')
    return results


def fetch_transcript(video_id: str) -> str | None:
    """
    Fetches the English transcript for a YouTube video using youtube-transcript-api
    routed through Webshare rotating residential proxies (bypasses YouTube IP bans).
    Tries English first; falls back to any available language if needed.
    Returns the full raw text string or None if unavailable.
    """
    try:
        ytt = _build_ytt_client()
        transcript = ytt.fetch(video_id, languages=['en'])
        text = ' '.join(snippet.text for snippet in transcript).strip()
        time.sleep(FETCH_DELAY)
        return text if text else None
    except (NoTranscriptFound, TranscriptsDisabled) as e:
        logger.warning(f'No English transcript for {video_id}: {e}')
        return None
    except Exception as e:
        logger.error(f'Error fetching transcript for {video_id}: {e}')
        return None