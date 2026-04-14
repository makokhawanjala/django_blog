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
    # Core topics
    'dark psychology', 'machiavelli', 'machiavellian', 'manipulation',
    'power dynamics', 'social power', 'influence', 'persuasion',
    'psychological manipulation', 'covert manipulation', 'overt manipulation',
    'dark arts', 'mind games', 'gaslighting', 'coercive control',

    # Self-mastery — your content pillars
    'emotional control', 'discipline', 'self-mastery', 'self mastery',
    'stoicism', 'stoic', 'mental strength', 'self control', 'mindset',
    'emotional intelligence', 'impulse control', 'delayed gratification',
    'mental toughness', 'inner strength', 'self discipline', 'willpower',
    'emotional regulation', 'unshakeable', 'composure', 'cold mind',
    'detached', 'unbothered', 'monk mode',

    # Strategy / tactics
    'psychological tactics', 'strategy', 'dark triad', 'narcissist',
    'narcissism', 'psychopath', 'sociopath', 'machiavellianism',
    'strategic thinking', 'chess not checkers', 'long game',
    'power move', 'calculated', 'strategic silence', 'information warfare',
    'leverage', 'negotiation tactics', 'psychological warfare',

    # Social dynamics — matches your article angles
    'respect', 'disrespect', 'boundaries', 'toxic people', 'betrayal',
    'trust', 'loyalty', 'silence', 'detachment', 'frame control',
    'social hierarchy', 'status', 'dominance', 'social proof',
    'command respect', 'lose respect', 'earn respect', 'demand respect',
    'high value', 'low value', 'alpha', 'sigma', 'frame',
    'presence', 'aura', 'energy', 'intimidation',

    # Relationships — betrayal, trust, power
    'toxic relationship', 'toxic person', 'narcissistic abuse',
    'emotional abuse', 'walking on eggshells', 'love bombing',
    'discard', 'hoovering', 'triangulation', 'supply',
    'cutting people off', 'no contact', 'grey rock',
    'going ghost', 'disappearing', 'isolation',

    # Pain points your audience searches
    'people pleaser', 'nice guy', 'doormat', 'taken advantage',
    'family drama', 'fake friends', 'coworkers', 'workplace politics',
    'how to deal with manipulators', 'controlling people',
    'being used', 'used by people', 'stop being used',
    'always giving never receiving', 'one sided friendship',
    'one sided relationship', 'being walked over', 'no backbone',
    'spineless', 'pushover', 'stop being a pushover',
    'need validation', 'seek approval', 'approval seeking',
    'people use you', 'fake loyalty', 'false friends',

    # Power vocabulary from your titles
    'weak', 'weakness', 'authority', 'dominance',
    'never react', 'stop explaining', 'stop caring what people think',
    'move in silence', 'stay silent', 'say less', 'speak less',
    'cold blooded', 'ruthless', 'calculated', 'feared',
    'untouchable', 'unreadable', 'mysterious', 'unpredictable',
    'dangerous man', 'dangerous energy', 'powerful man',
    'never explain yourself', 'stop justifying yourself',

    # Family / money secrecy — your top content angle
    'never tell family', 'hide your income', 'hide your success',
    'family jealousy', 'family betrayal', 'family enemies',
    'relatives jealous', "don't tell anyone your salary",
    'keep salary private', 'financial privacy', 'money secrets',
    'family taking your money', 'family using you',

    # Solitude / independence
    'walk alone', 'lone wolf', 'solitude', 'embrace solitude',
    'better alone', 'being alone', "don't need anyone",
    'self reliance', 'self sufficient', 'independent mindset',

    # Specific trigger phrases matching your article titles
    'no one is coming to save you', 'nobody is coming',
    'your reaction is your weakness', 'reaction is vulnerability',
    'move in silence', 'fix yourself in secret',
    'return as a threat', 'disappear and reappear',
    'stop reacting', 'never let them see you sweat',
    'they fear what they cannot control', 'control your mind',
    'cut people off', 'burn bridges', 'ghost everyone',
]


# Subreddits to monitor
TARGET_SUBREDDITS = [
    # Dark psychology / manipulation — direct topic match
    'darkpsychology',
    'Manipulation',
    'socialengineering',
    'coercivecontrol',
    'psychologyofsex',          # influence + persuasion overlap

    # Power, strategy, self-mastery
    'decidingtobebetter',
    'getdisciplined',
    'selfimprovement',
    'selfmastery',
    'BettermentBookClub',       # 48 Laws of Power discussions live here
    'thedavidgogginsfan',       # mental toughness, no excuses audience

    # Stoicism / philosophy
    'Stoicism',
    'philosophy',
    'Nietzsche',
    'JordanPeterson',
    'Epictetus',                # hardcore stoicism — high-quality discussions
    'MarcusAurelius',

    # Men's communities — your primary reader
    'AskMen',
    'AskMenOver30',
    'AskMenOver40',             # slightly older, more life experience = your reader
    'becomeaman',
    'TheRedPill',               # power dynamics, frame — exact match
    'marriedredpill',           # applied power dynamics
    'seduction',                # frame control, social influence
    'MensRights',               # betrayal, unfairness themes
    'menslib',                  # different angle, still discusses power + relationships

    # Narcissistic abuse / manipulation victims
    'NarcissisticAbuse',
    'raisedbynarcissists',
    'raisedbyborderlines',
    'CPTSD',                    # trauma from manipulation — emotionally engaged audience
    'emotionalabuse',
    'abusiverelationships',

    # Relationships — betrayal, trust, loyalty
    'relationship_advice',
    'relationships',
    'survivinginfidelity',
    'DeadBedrooms',             # detachment, walking away — your content angles
    'BreakUps',
    'ExNoContact',              # grey rock, no contact — perfect overlap
    'JUSTNOFAMILY',
    'JUSTNOMIL',
    'EstrangedAdultChildren',   # cutting family off — exact article topic

    # Family / money secrecy — matches your top articles
    'povertyfinance',           # "never tell family your salary" resonates here
    'personalfinance',
    'financialindependence',
    'leanfire',                 # quiet wealth, financial privacy mindset
    'ChoosingBeggars',          # family/friend exploitation stories — high engagement

    # Workplace — your coworker content
    'antiwork',
    'work',
    'careerguidance',
    'jobs',
    'Layoffs',
    'TrueOffMyChest',           # confessional posts — betrayal, coworker stories

    # Psychology — broad reach
    'psychology',
    'cognitivepsychology',
    'BehavioralEconomics',      # influence + persuasion angle
    'neuroscience',             # brain rewiring angle — your "rewire" articles

    # Broad self-help — large audiences
    'productivity',
    'LifeAdvice',
    'Advice',
    'offmychest',
    'confessions',              # betrayal stories — huge, emotional audience
    'TIFU',                     # high engagement — people being used/manipulated
    'AmItheAsshole',            # betrayal, disrespect, boundaries — massive traffic
    'entitledpeople',           # power + manipulation dynamics
    'entitledparents',          # family control themes — exact overlap

    # Success / wealth mindset
    'Entrepreneur',
    'Hustlers',
    'passive_income',
    'sweatystartup',            # grounded, no-BS mindset — your reader

    # Mindfulness / solitude angle
    'Meditation',
    'loneliness',               # solitude, walking alone — your content
    'intj',                     # strategic, independent, lone wolf personality type
    'intp',
    'infj',                     # "dark empath" audience — huge overlap
]

# Minimum engagement threshold for a social post to be scored by Claude
MIN_ENGAGEMENT_TWITTER = 20   # likes + retweets combined
MIN_ENGAGEMENT_REDDIT = 5     # upvotes (niche subs score lower)

# Minimum relevance score (0.0–1.0) for Claude to include in digest
MIN_SCORE_THRESHOLD = 0.40

# How many top opportunities to include per digest email
MAX_OPPORTUNITIES_PER_DIGEST = 15

# ── AWS Bedrock configuration ─────────────────────────────────────────────────
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

# All 5 source regions for claude-sonnet-4, each with independent rate-limit quota.
BEDROCK_REGION_CONFIGS = [
    {'region': 'us-east-1',      'model': 'us.anthropic.claude-sonnet-4-20250514-v1:0'},
    {'region': 'us-east-2',      'model': 'us.anthropic.claude-sonnet-4-20250514-v1:0'},
    {'region': 'us-west-2',      'model': 'us.anthropic.claude-sonnet-4-20250514-v1:0'},
    {'region': 'eu-west-1',      'model': 'eu.anthropic.claude-sonnet-4-20250514-v1:0'},
    {'region': 'ap-northeast-1', 'model': 'ap.anthropic.claude-sonnet-4-20250514-v1:0'},
]

# Region used for single-call operations
BEDROCK_PRIMARY_REGION = 'us-west-2'
BEDROCK_PRIMARY_MODEL  = 'us.anthropic.claude-sonnet-4-20250514-v1:0'