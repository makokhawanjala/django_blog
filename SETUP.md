# Railway Deployment Guide

Complete step-by-step guide to deploy this system to Railway with all 5 pipelines running.

## Step 1 — Fork and Clone

Fork this repo to your GitHub account, then clone it locally.

## Step 2 — Create a Railway Project

1. Go to railway.app and create a new project
2. Click "Deploy from GitHub repo" and select your fork
3. Railway will detect the Procfile automatically

## Step 3 — Add a PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" then "PostgreSQL"
3. Once provisioned, click the database service and copy the `DATABASE_URL` from the Variables tab

## Step 4 — Set Environment Variables

In your Railway web service, go to Variables and add every value from `.env.example`:

- `SECRET_KEY` — generate one at djecrety.ir
- `DEBUG` — set to `False`
- `ALLOWED_HOSTS` — your Railway domain (find it under Settings > Domains)
- `CSRF_TRUSTED_ORIGINS` — same as ALLOWED_HOSTS with `https://` prefix
- `DATABASE_URL` — paste from Step 3
- `ANTHROPIC_API_KEY` — from console.anthropic.com
- `YOUTUBE_API_KEY` — from Google Cloud Console
- `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` — from apps.reddit.com
- `REDDIT_USER_AGENT` — any descriptive string
- `NOTIFICATION_EMAIL` and email SMTP values

## Step 5 — Run Migrations

In Railway, open your web service terminal and run:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Step 6 — Configure the 5 Cron Jobs

In Railway, click "New Service" and select "Cron Job" for each pipeline below:

| Pipeline | Command | Schedule |
|---|---|---|
| Transcript Fetcher | `python manage.py fetch_transcripts` | `0 6 * * *` (daily 6am) |
| SEO Processor | `python manage.py process_seo` | `0 7 * * *` (daily 7am) |
| Social Monitor | `python manage.py monitor_social` | `0 */4 * * *` (every 4 hours) |
| Comment Classifier | `python manage.py classify_comments` | `0 */2 * * *` (every 2 hours) |
| Weekly Digest | `python manage.py weekly_digest` | `0 8 * * 1` (Mondays 8am) |

Set the same environment variables on each cron service (or use Railway's shared variables).

## Step 7 — Configure Your Niche

In `automation_scripts/config.py`, update:

- `YOUTUBE_CHANNELS` — list of YouTube channel IDs to monitor
- `REDDIT_SUBREDDITS` — list of subreddits to monitor
- `REDDIT_KEYWORDS` — keywords that trigger reply opportunity alerts
- `BLOG_NICHE` — description of your blog topic (used in Claude prompts)

## Step 8 — Verify Everything Is Running

After your first cron runs, check Railway logs for each service. A successful run ends with "Completed successfully." Your Django admin should start showing new draft posts within 24 hours.
