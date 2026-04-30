# Django AI Blog Automation System

A production-ready Django blog with 5 Claude-powered automation pipelines that run on a schedule with zero manual input. This is the exact system running live at [machiavellimind.com](https://machiavellimind.com) — 360+ posts generated, all pipelines green on Railway.

**Rule that governs everything:** Claude drafts. You decide. Nothing goes live without your action.

---

## What It Does

| Pipeline | Trigger | What Claude Does | What You Do |
|---|---|---|---|
| 1 — Transcript Fetcher | Daily cron (6am UTC) | Pulls YouTube transcripts, rewrites in your voice, creates draft posts | Review, edit, publish |
| 2 — Social Monitor | Every 6 hours | Scores Reddit/Twitter posts for reply opportunity, drafts replies | Edit reply, post manually, mark actioned |
| 3 — Comment Classifier | Every 2 hours | Classifies every incoming blog comment, drafts replies for worthy ones | Approve/reject comment, edit reply, post |
| 4 — SEO Processor | On post publish (signal) + daily cron | Generates meta description, tags, internal link suggestions | Apply suggestions in admin |
| 5 — Weekly Digest | Sunday 8am UTC | Reads GA4 data, writes plain-English analytics brief | Read brief, act on recommendations |

---

## Architecture Overview

```
YouTube Channels
      │
      ▼
fetch_transcripts.py  ──►  TranscriptQueue (DB)  ──►  Django Admin (Drafts)
      │
      └── yt-dlp → raw transcript → Claude API → formatted draft post


Reddit / Twitter
      │
      ▼
monitor_social.py  ──►  SocialOpportunity (DB)  ──►  Email Digest  ──►  Django Admin
      │
      └── PRAW/requests → posts → Claude API → scored + draft reply


Blog Comments (incoming)
      │
      ▼
classify_comments.py  ──►  CommentAlert (DB)  ──►  Django Admin
      │
      └── Django signal → Claude API → classification + draft reply


Published Post (on save)
      │
      ▼
signals.py  ──►  process_seo.py  ──►  PostSEO (DB)  ──►  Django Admin
      │
      └── post_save signal → Claude API → meta description + tags


Google Analytics GA4
      │
      ▼
weekly_digest.py  ──►  WeeklyDigest (DB)  ──►  Email Brief
      │
      └── GA4 API → raw data → Claude API → plain-English brief
```

---

## Stack

- **Python** 3.11+
- **Django** 5.0
- **PostgreSQL** (via Railway)
- **Anthropic Claude API** (`anthropic==0.94.0`) — `claude-sonnet-4-20250514`
- **YouTube transcripts** — `yt-dlp`, `youtube-transcript-api`
- **Reddit API** — `praw==7.8.1`
- **Google Analytics** — `google-analytics-data`
- **Railway** — hosting + cron job scheduling
- **Gunicorn** + **WhiteNoise** — production serving
- **python-decouple** — environment variable management

---

## Prerequisites

Before deploying, you need accounts and API keys for the following:

- **Railway** account — free tier works for getting started (railway.app)
- **Anthropic API key** — from console.anthropic.com
- **YouTube Data API v3 key** — from Google Cloud Console (console.cloud.google.com)
- **Reddit API credentials** — create a "script" app at reddit.com/prefs/apps
- **Gmail account** with App Password enabled — for notification emails (not your login password — generate at myaccount.google.com/apppasswords after enabling 2FA)
- **Google Analytics GA4 property** — optional, only required for Pipeline 5 (weekly digest)

---

## Quick Start (Local)

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Create and activate virtual environment
python -m venv env
source env/bin/activate        # Linux/Mac
# env\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Open .env and fill in every value — see .env.example for descriptions

# Run migrations
python manage.py migrate

# Create a superuser for Django admin
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin` to access the Django admin panel.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in every value before running anything.

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key — generate one at djecrety.ir |
| `DEBUG` | Yes | Set to `False` in production |
| `ALLOWED_HOSTS` | Yes | Your Railway domain + custom domain |
| `CSRF_TRUSTED_ORIGINS` | Yes | Same as ALLOWED_HOSTS with `https://` prefix |
| `DATABASE_URL` | Yes | PostgreSQL connection string from Railway |
| `ANTHROPIC_API_KEY` | Yes | Powers all 5 Claude-based pipelines |
| `YOUTUBE_API_KEY` | Yes | YouTube Data API v3 — for Pipeline 1 |
| `REDDIT_CLIENT_ID` | Yes | Reddit app client ID — for Pipeline 2 |
| `REDDIT_CLIENT_SECRET` | Yes | Reddit app secret — for Pipeline 2 |
| `REDDIT_USER_AGENT` | Yes | Descriptive string, e.g. `myblog/1.0 by yourusername` |
| `GOOGLE_ANALYTICS_PROPERTY_ID` | No | GA4 property ID — for Pipeline 5 only |
| `NOTIFICATION_EMAIL` | Yes | Where digest emails are sent |
| `EMAIL_HOST` | Yes | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | Yes | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Yes | Gmail App Password (not your login password) |
| `BLOG_AUTHOR_ID` | Yes | Django User ID of the blog author (default: `1`) |
| `MONITORED_CHANNELS` | Yes | Comma-separated YouTube channel IDs to monitor |

---

## Running the Pipelines Manually

All 5 pipelines can be triggered manually at any time for testing:

```bash
# Pipeline 1 — Fetch YouTube transcripts and create draft posts
python manage.py fetch_transcripts

# Pipeline 2 — Scan Reddit/Twitter for reply opportunities
python manage.py monitor_social

# Pipeline 3 — Classify unprocessed blog comments
python manage.py classify_comments

# Pipeline 4 — Generate SEO metadata for published posts
python manage.py process_seo

# Pipeline 5 — Generate and email weekly analytics brief
python manage.py weekly_digest
```

After running, check Django admin for results:
- **TranscriptQueue** — new entries from Pipeline 1
- **Social Opportunities** — scored posts from Pipeline 2
- **Comment Alerts** — classified comments from Pipeline 3
- **Post SEOs** — generated metadata from Pipeline 4
- **Weekly Digests** — analytics briefs from Pipeline 5

---

## Deploying to Railway

See **[SETUP.md](./SETUP.md)** for the complete Railway deployment guide.

Summary of what SETUP.md covers:

1. Fork and clone the repo
2. Create a Railway project and connect your GitHub fork
3. Add a PostgreSQL database service
4. Set all environment variables in the Railway dashboard
5. Run migrations via the Railway terminal
6. Configure all 5 cron jobs in Railway

**Railway cron job schedule:**

| Command | Schedule | Description |
|---|---|---|
| `python manage.py fetch_transcripts` | `0 6 * * *` | Daily at 6am UTC |
| `python manage.py monitor_social` | `0 6,12,18,0 * * *` | Every 6 hours |
| `python manage.py classify_comments` | `0 */2 * * *` | Every 2 hours |
| `python manage.py process_seo` | `0 7 * * *` | Daily at 7am UTC |
| `python manage.py weekly_digest` | `0 8 * * 0` | Sundays at 8am UTC |

---

## Project Structure

```
Blog/
├── automation/                          # Django app — pipeline runners
│   ├── models.py                        # WeeklyDigest, PostSEO models
│   ├── admin.py                         # Admin for WeeklyDigest, PostSEO
│   └── management/
│       └── commands/
│           ├── fetch_transcripts.py     # Pipeline 1
│           ├── monitor_social.py        # Pipeline 2
│           ├── classify_comments.py     # Pipeline 3
│           ├── process_seo.py           # Pipeline 4
│           └── weekly_digest.py         # Pipeline 5
│
├── automation_scripts/                  # Core logic — imported by commands
│   ├── config.py                        # Centralised settings for all scripts
│   ├── transcript_fetcher.py            # yt-dlp YouTube transcript acquisition
│   ├── claude_processor.py             # All Claude API calls (single module)
│   ├── social_monitor.py               # Reddit + Twitter post collection
│   ├── comment_classifier.py           # Comment triage logic
│   ├── seo_processor.py                # SEO metadata generation
│   ├── analytics_fetcher.py            # GA4 data pull
│   └── notifier.py                     # Email digest sender
│
├── blog/                                # Django blog app
│   ├── models.py                        # Post, Comment, TranscriptQueue,
│   │                                    # SocialOpportunity, CommentAlert
│   ├── views.py                         # Blog views
│   ├── admin.py                         # Admin for all blog models
│   ├── signals.py                       # post_save → SEO trigger
│   ├── apps.py                          # Registers signals on startup
│   └── templates/blog/                  # HTML templates
│
├── mysite/                              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── static/css/blog.css                  # Stylesheet
├── logs/                                # Cron job log output
├── Procfile                             # Railway process config
├── requirements.txt                     # All Python dependencies
├── .env.example                         # Environment variable template
├── SETUP.md                             # Full Railway deployment guide
└── crontab.txt                          # Local cron schedule (WSL/Linux)
```

---

## Django Admin — Daily Workflow

After deploying, your daily workflow lives entirely in the Django admin at `/admin`:

- **TranscriptQueue** — review draft posts created overnight from YouTube transcripts. Open the linked Post draft, sharpen the voice, click Publish.
- **Social Opportunities** — review scored Reddit/Twitter posts from the overnight digest email. Edit the draft reply until it sounds like you. Post it yourself. Mark as Actioned in admin.
- **Comment Alerts** — read comments flagged as `worth_engaging`. Edit the draft reply. Post it yourself. Mark as Replied.
- **Post SEOs** — check SEO suggestions for recently published posts. Apply meta description and tag recommendations manually.
- **Weekly Digests** (Sundays) — read the analytics brief. Act on the content recommendation for the coming week.

The pipelines handle volume. You handle quality and publishing decisions.

---

## Customising for Your Niche

Four things to configure in `automation_scripts/config.py` before your first run:

```python
# 1. YouTube channel IDs to monitor (or set via MONITORED_CHANNELS env var)
MONITORED_CHANNELS = ['UCxxxxxx', 'UCyyyyyy']

# 2. Subreddits to watch for reply opportunities
TARGET_SUBREDDITS = ['psychology', 'stoicism', 'selfimprovement', ...]

# 3. Keywords that make a post relevant to your niche
RELEVANCE_KEYWORDS = ['dark psychology', 'stoicism', 'power dynamics', ...]

# 4. Claude voice prompt — in claude_processor.py, update VOICE_SYSTEM_PROMPT
# to describe your blog's tone, style, and formatting rules
```

---

## Estimated Monthly Running Cost

| Service | Cost |
|---|---|
| Railway (Hobby plan) | ~$5–10/month |
| Anthropic Claude API | ~$5–20/month depending on volume |
| YouTube Data API v3 | Free (10,000 units/day quota) |
| Reddit API | Free |
| Google Analytics | Free |
| **Total** | **~$10–30/month** |

---

## License

MIT License. Free to use for personal projects and client work. See [LICENSE](./LICENSE) for full terms.

---

## Built By

Amos Makokha — [machiavellimind.com](https://machiavellimind.com)
