import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
REDDIT_CLIENT_ID = settings.REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET = settings.REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT = settings.REDDIT_USER_AGENT
GOOGLE_ANALYTICS_PROPERTY_ID = settings.GOOGLE_ANALYTICS_PROPERTY_ID
BLOG_AUTHOR_ID = settings.BLOG_AUTHOR_ID
MONITORED_CHANNELS = settings.MONITORED_CHANNELS
NOTIFICATION_EMAIL = settings.NOTIFICATION_EMAIL

# Keywords Claude uses to score social posts for relevance
RELEVANCE_KEYWORDS = [
    'dark psychology', 'machiavelli', 'manipulation', 'power dynamics',
    'emotional control', 'discipline', 'self-mastery', 'stoicism',
    'psychological tactics', 'influence', 'persuasion', 'strategy',
    'how to deal with manipulators', 'mental strength', 'dark triad'
]

# Subreddits to monitor
TARGET_SUBREDDITS = [
    'psychology', 'stoicism', 'selfimprovement', 'socialskills',
    'powerofthedog', 'RedPillWomen', 'Manipulation', 'mentalhealth',
    'philosophy', 'getdisciplined'
]

# Minimum engagement threshold for a social post to be scored
MIN_ENGAGEMENT_TWITTER = 50   # likes + retweets combined
MIN_ENGAGEMENT_REDDIT = 20    # upvotes

# Minimum relevance score (0.0-1.0) to include in digest
MIN_SCORE_THRESHOLD = 0.65

# How many opportunities to include per digest email
MAX_OPPORTUNITIES_PER_DIGEST = 10

# ── AWS Bedrock configuration ─────────────────────────────────────────────────
# Credentials are read from environment / ~/.aws/credentials automatically
# by boto3. Only set these if you need to override the default chain.
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

# All 5 source regions for claude-sonnet-4, each with independent rate-limit quota.
# Parallel calls across these give 5x throughput at zero extra cost.
BEDROCK_REGION_CONFIGS = [
    {'region': 'us-east-1',      'model': 'us.anthropic.claude-sonnet-4-20250514-v1:0'},
    {'region': 'us-east-2',      'model': 'us.anthropic.claude-sonnet-4-20250514-v1:0'},
    {'region': 'us-west-2',      'model': 'us.anthropic.claude-sonnet-4-20250514-v1:0'},
    {'region': 'eu-west-1',      'model': 'eu.anthropic.claude-sonnet-4-20250514-v1:0'},
    {'region': 'ap-northeast-1', 'model': 'ap.anthropic.claude-sonnet-4-20250514-v1:0'},
]

# Region used for single-call operations (lowest latency in testing)
BEDROCK_PRIMARY_REGION = 'us-west-2'
BEDROCK_PRIMARY_MODEL  = 'us.anthropic.claude-sonnet-4-20250514-v1:0'