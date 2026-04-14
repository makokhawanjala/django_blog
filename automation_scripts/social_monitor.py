import requests
import logging
from automation_scripts.config import (
    REDDIT_USER_AGENT,
    TARGET_SUBREDDITS, RELEVANCE_KEYWORDS, MIN_ENGAGEMENT_REDDIT
)

logger = logging.getLogger(__name__)


def fetch_reddit_posts(limit_per_sub: int = 25) -> list[dict]:
    """
    Fetches hot and new posts from target subreddits matching relevance keywords.
    Uses Reddit's public JSON API — no API key or PRAW required.
    Returns list of {platform, post_url, post_text, author, engagement_count}
    """
    results = []
    keyword_set = {k.lower() for k in RELEVANCE_KEYWORDS}
    headers = {'User-Agent': REDDIT_USER_AGENT}

    for subreddit_name in TARGET_SUBREDDITS:
        for listing in ('hot', 'new'):
            url = f'https://www.reddit.com/r/{subreddit_name}/{listing}.json?limit={limit_per_sub}'
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    logger.warning(f'Reddit public API returned {response.status_code} for r/{subreddit_name}/{listing}')
                    continue
                data = response.json()
                for child in data.get('data', {}).get('children', []):
                    post = child.get('data', {})
                    score = post.get('score', 0)
                    if score < MIN_ENGAGEMENT_REDDIT:
                        continue
                    text = f'{post.get("title", "")} {post.get("selftext", "")}'.lower()

                    import time
                    created_utc = post.get('created_utc', 0)
                    if (time.time() - created_utc) > 86400:
                        continue
                    if any(kw in text for kw in keyword_set):
                        results.append({
                            'platform': 'reddit',
                            'post_url': f'https://reddit.com{post.get("permalink", "")}',
                            'post_text': f'{post.get("title", "")}\n\n{post.get("selftext", "")[:500]}',
                            'author': post.get('author', ''),
                            'engagement_count': score,
                        })

            except Exception as e:
                logger.error(f'Reddit fetch error for r/{subreddit_name}/{listing}: {e}')

    return results


def fetch_twitter_search_posts(keywords: list[str]) -> list[dict]:
    """
    Uses Twitter API v2 recent search to find relevant posts.
    Requires TWITTER_BEARER_TOKEN in environment (add to .env if using).
    Returns list of {platform, post_url, post_text, author, engagement_count}

    NOTE: If Twitter API access is unavailable, this returns an empty list
    and the pipeline continues with Reddit results only.
    """
    import os
    bearer_token = os.environ.get('TWITTER_BEARER_TOKEN', '')
    if not bearer_token:
        logger.info('No TWITTER_BEARER_TOKEN set — skipping Twitter search')
        return []

    results = []
    query = ' OR '.join([f'"{kw}"' for kw in keywords[:5]]) + ' -is:retweet lang:en'
    headers = {'Authorization': f'Bearer {bearer_token}'}
    params = {
        'query': query,
        'max_results': 20,
        'tweet.fields': 'public_metrics,author_id,created_at',
        'expansions': 'author_id',
        'user.fields': 'username'
    }
    try:
        response = requests.get(
            'https://api.twitter.com/2/tweets/search/recent',
            headers=headers, params=params, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            users = {u['id']: u['username'] for u in data.get('includes', {}).get('users', [])}
            for tweet in data.get('data', []):
                metrics = tweet.get('public_metrics', {})
                engagement = metrics.get('like_count', 0) + metrics.get('retweet_count', 0)
                results.append({
                    'platform': 'twitter',
                    'post_url': f'https://x.com/i/web/status/{tweet["id"]}',
                    'post_text': tweet['text'],
                    'author': users.get(tweet.get('author_id'), ''),
                    'engagement_count': engagement,
                })
        else:
            logger.warning(f'Twitter API returned {response.status_code}')
    except Exception as e:
        logger.error(f'Twitter fetch error: {e}')
    return results


def collect_all_posts() -> list[dict]:
    """Entry point — collects from all platforms and returns combined list."""
    posts = []
    posts.extend(fetch_reddit_posts())
    posts.extend(fetch_twitter_search_posts(RELEVANCE_KEYWORDS[:5]))
    logger.info(f'Collected {len(posts)} posts across all platforms')
    return posts