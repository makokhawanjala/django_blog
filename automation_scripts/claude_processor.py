import anthropic
import logging
from automation_scripts.config import (
    ANTHROPIC_API_KEY,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    BEDROCK_PRIMARY_REGION, BEDROCK_PRIMARY_MODEL,
)

logger = logging.getLogger(__name__)


def _make_bedrock_client(region: str) -> anthropic.AnthropicBedrock:
    kwargs = dict(aws_region=region)
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        kwargs['aws_access_key'] = AWS_ACCESS_KEY_ID
        kwargs['aws_secret_key'] = AWS_SECRET_ACCESS_KEY
    return anthropic.AnthropicBedrock(**kwargs)


def _get_client():
    """
    Returns (client, model_id).
    Tries Bedrock first (free via AWS IAM, 5 regions available).
    Falls back to direct Anthropic API if Bedrock is unavailable.
    """
    try:
        client = _make_bedrock_client(BEDROCK_PRIMARY_REGION)
        # Lightweight probe to confirm Bedrock is reachable
        client.messages.create(
            model=BEDROCK_PRIMARY_MODEL,
            max_tokens=5,
            messages=[{'role': 'user', 'content': 'OK'}],
        )
        logger.info(f'Using Bedrock ({BEDROCK_PRIMARY_REGION})')
        return client, BEDROCK_PRIMARY_MODEL
    except Exception as e:
        logger.warning(f'Bedrock unavailable ({e}), falling back to Anthropic API')
        return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY), 'claude-sonnet-4-20250514'


# Initialise once at import time
_client, _model = _get_client()


VOICE_SYSTEM_PROMPT = """
You write for machiavellimind.com. The blog covers dark psychology, Machiavellian strategy,
power dynamics, emotional discipline, and self-mastery. You write like a man speaking
directly to one person from a stage. Cold. Direct. No performance. No comfort. No fluff.

The reader is a man who is done being ordinary. Speak to that version of him.

VOICE RULES:
- Write like you are standing on a stage speaking directly to one person in the front row.
  Not lecturing. Not motivating. Transmitting. There is a difference.
- Short sentences hit harder than long ones. Use them.
- Every paragraph must earn its place. If it does not move the idea forward, cut it.
- No dashes inside sentences. Use a period or a new sentence instead.
- No AI language. No phrases like: "it is worth noting", "in today's world", "delve into",
  "navigate", "at the end of the day", "game-changer", "paradigm shift", "unpack", "foster",
  "leverage", "in conclusion", "this article will", "let us explore".
- No motivational fluff. No affirmations. No "you've got this" energy.
- No bullet point lists as a substitute for real writing. If you must list, write it as prose.
- No emoji. No hashtags. No YouTube CTAs.
- No filler transitions like "furthermore", "additionally", "in summary".
- Do not explain what you are about to say. Just say it.

STRUCTURE RULES:
- Word count: 1500 to 2500 words. Never go below 1500. Never go above 2500.
- Opening: No heading. No label. Start with a hook. The first 1 to 3 lines must stop the
  reader cold. Use one of these hook types:
    * An uncomfortable truth stated plainly.
    * A bold claim that challenges what the reader believes.
    * A short sharp statement that names a pain point without apology.
    * A question that makes the reader feel exposed.
  The hook must not start with "I want to share", "I have been thinking", "In today's world",
  or any other soft opener. It must hit immediately.
- After the hook: 2 to 4 short paragraphs that pull the reader deeper into the core idea.
  No section heading yet. Build tension. Make them need what comes next.
- Section headings: Use Roman numerals. Format: ## I. Title Here
  Each section heading should feel like a statement, not a label.
- Sections: 3 to 6 sections. Each section opens with a line that could stand alone as a hook.
  Each section closes with a line that lands with weight.
- Closing: No heading. No "conclusion" label. End with a short sharp statement that
  feels like a final transmission. The last line must be memorable. It should feel like the
  reader just got handed something they cannot put down.
- Section dividers between major sections: ---

CONTENT RULES:
- Pull only what serves the core idea from the transcript. Do not include everything.
  The transcript is raw material. Your job is to find the spine of the argument and
  build only around that.
- If the transcript contains a real story, historical reference, or concrete example,
  use it. Ground the ideas in something real.
- If the transcript mentions a historical figure, a psychological concept, or a documented
  event, you may expand on it with accurate detail. Do not invent facts.
- Never invent quotes. If you use a quote, it must be real.
- Machiavelli quotes as blockquotes: > "quote" — Machiavelli
- Bold for statements that are meant to land like a punch: **text**
- Italics for a shift in tone, an internal voice, or emphasis: *text*
- Strip everything that is noise: [Music], timestamps, filler phrases, repetition,
  YouTube subscriber prompts, comment prompts, affirmations, self-help clichés.
"""


def clean_transcript_to_draft(raw_transcript: str, video_title: str) -> dict:
    """
    Takes a raw YouTube transcript and returns a dict with:
      - title: suggested article title
      - body: formatted markdown body
      - tags: comma-separated tag suggestions
      - meta_description: 155-char SEO meta description
    """
    try:
        message = _client.messages.create(
            model=_model,
            max_tokens=16000,
            system=VOICE_SYSTEM_PROMPT,
            messages=[{
                'role': 'user',
                'content': f"""Video title: {video_title}

Raw transcript:
{raw_transcript}

Read the transcript fully. Identify the single strongest argument or idea running through it.
Build the article around that spine only. Cut everything that does not serve it.

The article must be between 1500 and 2500 words.
It must sound like a man speaking from a stage directly to one person.
It must not sound like it was written by AI.
It must not contain any of the forbidden phrases or patterns listed in your instructions.

Return ONLY a JSON object with exactly these four keys. No preamble. No markdown code fences.
Pure JSON only.

{{
  "title": "A strong article title in the blog voice. Cold, direct, no punctuation tricks.",
  "body": "The full formatted markdown article body. 1500 to 2500 words.",
  "tags": "comma-separated lowercase tags, maximum 8, e.g. discipline,power,machiavelli",
  "meta_description": "Exactly 155 characters. Keyword-rich. Written in the blog voice. No fluff."
}}"""
            }]
        )
        import json
        text = message.content[0].text.strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f'Claude transcript cleaning failed: {e}')
        return {}


def score_social_post(post_text: str, platform: str, published_articles: list[dict]) -> dict:
    """
    Scores a social media post for reply opportunity.
    Returns:
      - score: float 0.0-1.0
      - reasoning: one sentence why
      - draft_reply: 3-4 sentence reply ending with a natural article link
      - related_article_id: ID of the most relevant published article or None
    """
    articles_context = '\n'.join([
        f'- ID {a["id"]}: "{a["title"]}" → {a["url"]}'
        for a in published_articles
    ])
    try:
        message = _client.messages.create(
            model=_model,
            max_tokens=8000,
            system=(
                'You are a social media strategist for machiavellimind.com. '
                'The blog covers dark psychology, Machiavellian strategy, power dynamics, '
                'and self-mastery. The voice is cold, direct, and authoritative. '
                'When drafting replies, write in that same voice. No fluff. No emoji. '
                'Short sentences. Return only valid JSON. No preamble. No code fences.'
            ),
            messages=[{
                'role': 'user',
                'content': f"""Blog: machiavellimind.com — dark psychology, Machiavellian strategy, power dynamics.

Published articles:
{articles_context}

Platform: {platform}
Post: {post_text}

Score this post as a reply opportunity for the blog. Return ONLY JSON with:
- "score": float 0.0-1.0 (how worth replying to based on relevance + engagement opportunity)
- "reasoning": one sentence explaining the score
- "draft_reply": 3-4 sentences in the blog's cold authoritative voice, ending naturally with the most relevant article URL. Do not say "check out" or "read more". Let the insight lead.
- "related_article_id": the integer ID of the most relevant article, or null

No preamble. Pure JSON only."""
            }]
        )
        import json
        return json.loads(message.content[0].text.strip())
    except Exception as e:
        logger.error(f'Claude social scoring failed: {e}')
        return {'score': 0.0, 'reasoning': '', 'draft_reply': '', 'related_article_id': None}


def classify_comment(comment_body: str, post_title: str) -> dict:
    """
    Classifies a blog comment and drafts a reply if worth engaging.
    Returns:
      - classification: 'spam' | 'low_value' | 'worth_engaging'
      - reasoning: one sentence
      - draft_reply: reply text or empty string
    """
    try:
        message = _client.messages.create(
            model=_model,
            max_tokens=8000,
            system=(
                'You are a comment classifier for machiavellimind.com. '
                'The blog covers dark psychology, Machiavellian strategy, power dynamics, '
                'and self-mastery. The voice is cold, direct, and authoritative. '
                'When drafting replies, write in that same voice. No fluff. No emoji. '
                'Short sentences. Return only valid JSON. No preamble. No code fences.'
            ),
            messages=[{
                'role': 'user',
                'content': f"""Blog post: "{post_title}"

Comment: {comment_body}

Classify this comment and return ONLY JSON with:
- "classification": one of "spam", "low_value", "worth_engaging"
- "reasoning": one sentence
- "draft_reply": if worth_engaging, a 2-3 sentence reply in the blog voice. Otherwise empty string.

spam = bot, promotional, gibberish
low_value = generic ("great post!"), adds nothing
worth_engaging = genuine question, pushback, insight, or personal story

No preamble. Pure JSON only."""
            }]
        )
        import json
        return json.loads(message.content[0].text.strip())
    except Exception as e:
        logger.error(f'Claude comment classification failed: {e}')
        return {'classification': 'low_value', 'reasoning': '', 'draft_reply': ''}

def generate_seo_metadata(post_title: str, post_body: str) -> dict:
    """
    Generates SEO metadata for a published post.
    Returns:
      - meta_description: 155-char description
      - suggested_tags: list of tag strings
      - internal_link_notes: internal linking suggestions
    """
    try:
        message = _client.messages.create(
            model=_model,
            max_tokens=1000,
            system=(
                'You are an SEO specialist for machiavellimind.com. '
                'The blog covers dark psychology, Machiavellian strategy, power dynamics, '
                'and self-mastery. The voice is cold, direct, and authoritative. '
                'Return only valid JSON. No preamble. No code fences. No markdown.'
            ),
            messages=[{
                'role': 'user',
                'content': f"""Post title: {post_title}

Post body (first 1000 chars):
{post_body[:1000]}

Return ONLY JSON with:
- "meta_description": exactly 155 characters, keyword-rich, in the blog's voice
- "suggested_tags": list of 6-8 lowercase tag strings
- "internal_link_notes": 1-2 sentence note on where internal links could be added

No preamble. Pure JSON only."""
            }]
        )
        import json
        return json.loads(message.content[0].text.strip())
    except Exception as e:
        logger.error(f'Claude SEO generation failed: {e}')
        return {}


def generate_analytics_brief(analytics_data: dict) -> str:
    """
    Takes a dict of raw GA4 + Search Console data and returns a plain-English
    weekly brief as a markdown string.
    """
    try:
        message = _client.messages.create(
            model=_model,
            max_tokens=8000,
            messages=[{
                'role': 'user',
                'content': f"""You are a concise analytics advisor for machiavellimind.com.

Raw analytics data (last 7 days):
{analytics_data}

Write a plain-English weekly brief covering:
1. Which article performed best and why it likely resonated
2. Any keywords starting to surface in Search Console
3. One specific content recommendation based on what's working
4. One thing to fix or improve based on the data

Be direct. No fluff. No headers. Under 300 words."""
            }]
        )
        return message.content[0].text.strip()
    except Exception as e:
        logger.error(f'Claude analytics brief failed: {e}')
        return ''