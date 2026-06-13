# content_ai.py
import os
import json
import requests
from datetime  import datetime, timedelta
from dotenv    import load_dotenv
from brand_config import PLATFORM_SPECS, TONE_OPTIONS

load_dotenv()

OLLAMA_HOST  = os.getenv("OLLAMA_HOST",  "http://10.22.39.192:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5vl:latest")
FENCE        = "```"


def call_llm(prompt: str, max_tokens: int = 1024) -> str:
    resp = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model":   OLLAMA_MODEL,
            "prompt":  prompt,
            "stream":  False,
            "options": {"temperature": 0.7, "num_predict": max_tokens}
        },
        timeout=120
    )
    resp.raise_for_status()
    return resp.json()["response"].strip()


def build_brand_context(brand: dict) -> str:
    """Build brand voice context string."""
    tone_desc = TONE_OPTIONS.get(brand.get("tone", "Professional"), "professional")
    return (
        f"BRAND: {brand.get('name', 'Our Company')}\n"
        f"INDUSTRY: {brand.get('industry', 'Technology')}\n"
        f"TARGET AUDIENCE: {brand.get('audience', 'Professionals')}\n"
        f"TONE: {brand.get('tone', 'Professional')} — {tone_desc}\n"
        f"KEY VALUES: {brand.get('values', 'Innovation, Quality, Trust')}\n"
        f"TAGLINE / USP: {brand.get('tagline', '')}\n"
    )


# ── 1. Generate posts for all platforms ──────────────────────────────────────

def generate_posts(
    topic:     str,
    brand:     dict,
    platforms: list[str],
    post_type: str = "Educational — teach something valuable"
) -> dict[str, str]:
    """Generate one post per selected platform for a given topic."""
    brand_ctx = build_brand_context(brand)
    posts     = {}

    for platform in platforms:
        spec   = PLATFORM_SPECS.get(platform, {})
        style  = spec.get("style", "")
        max_ch = spec.get("optimal_chars", 200)
        htags  = spec.get("hashtags", "3-5 hashtags")

        prompt = (
            f"You are a social media expert writing for {platform}.\n\n"
            f"BRAND CONTEXT:\n{brand_ctx}\n"
            f"POST TYPE: {post_type}\n"
            f"TOPIC: {topic}\n\n"
            f"PLATFORM GUIDELINES FOR {platform.upper()}:\n{style}\n\n"
            f"Write ONE {platform} post about the topic above.\n"
            f"Target length: ~{max_ch} characters.\n"
            f"Include {htags}.\n"
            f"Match the brand tone exactly.\n"
            f"Do NOT include any preamble — output the post directly."
        )

        posts[platform] = call_llm(prompt, max_tokens=512)

    return posts


# ── 2. Repurpose long content ─────────────────────────────────────────────────

def repurpose_content(
    long_content: str,
    brand:        dict,
    platforms:    list[str],
    num_posts:    int = 5
) -> list[dict]:
    """Turn one long piece of content into multiple social posts."""
    brand_ctx = build_brand_context(brand)

    prompt = (
        f"You are a content repurposing expert.\n\n"
        f"BRAND CONTEXT:\n{brand_ctx}\n\n"
        f"ORIGINAL CONTENT:\n{long_content[:3000]}\n\n"
        f"Extract {num_posts} distinct social media post ideas from this content.\n"
        f"Each post should cover a different angle or insight.\n"
        f"Target platforms: {', '.join(platforms)}\n\n"
        f"Respond in this EXACT JSON format:\n"
        f"{FENCE}json\n"
        f"[\n"
        f"  {{\n"
        f'    "angle": "Short description of this post angle",\n'
        f'    "platform": "{platforms[0] if platforms else "LinkedIn"}",\n'
        f'    "content": "The actual post content with hashtags"\n'
        f"  }}\n"
        f"]\n"
        f"{FENCE}"
    )

    raw = call_llm(prompt, max_tokens=2048)

    try:
        if FENCE in raw:
            parts = raw.split(FENCE)
            for part in parts:
                if part.startswith("json"):
                    raw = part[4:].strip()
                    break
                elif part.strip().startswith("["):
                    raw = part.strip()
                    break
        result = json.loads(raw.strip())
        return result if isinstance(result, list) else []
    except Exception:
        return [{"angle": "Key insight", "platform": platforms[0] if platforms else "LinkedIn",
                 "content": raw[:500]}]


# ── 3. Content calendar ───────────────────────────────────────────────────────

def generate_content_calendar(
    brand:       dict,
    days:        int = 30,
    posts_per_week: int = 5
) -> list[dict]:
    """Generate a content calendar with topic and post type per day."""
    brand_ctx  = build_brand_context(brand)
    total_posts = (days // 7) * posts_per_week

    prompt = (
        f"You are a social media strategist.\n\n"
        f"BRAND CONTEXT:\n{brand_ctx}\n\n"
        f"Create a {days}-day social media content calendar.\n"
        f"Generate {total_posts} posts total — roughly {posts_per_week} per week.\n"
        f"Mix different post types and platforms for variety.\n\n"
        f"Respond in EXACT JSON format:\n"
        f"{FENCE}json\n"
        f"[\n"
        f"  {{\n"
        f'    "day": 1,\n'
        f'    "platform": "LinkedIn",\n'
        f'    "post_type": "Educational",\n'
        f'    "topic": "Specific topic to post about",\n'
        f'    "best_time": "9:00 AM"\n'
        f"  }}\n"
        f"]\n"
        f"{FENCE}\n\n"
        f"Vary platforms across the week. Use optimal posting times per platform.\n"
        f"Topics should be specific and relevant to the brand's industry."
    )

    raw = call_llm(prompt, max_tokens=3000)

    try:
        if FENCE in raw:
            parts = raw.split(FENCE)
            for part in parts:
                if part.startswith("json"):
                    raw = part[4:].strip()
                    break
                elif part.strip().startswith("["):
                    raw = part.strip()
                    break
        calendar = json.loads(raw.strip())

        # Add actual dates
        start_date = datetime.now()
        for item in calendar:
            day_offset = item.get("day", 1) - 1
            item["date"] = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")

        return calendar
    except Exception:
        return []


# ── 4. Hashtag optimiser ──────────────────────────────────────────────────────

def generate_hashtags(
    topic:    str,
    platform: str,
    brand:    dict
) -> dict:
    """Generate optimised hashtags for a platform."""
    spec = PLATFORM_SPECS.get(platform, {})

    prompt = (
        f"You are a social media hashtag expert.\n\n"
        f"BRAND: {brand.get('name', 'Brand')}\n"
        f"INDUSTRY: {brand.get('industry', 'Technology')}\n"
        f"PLATFORM: {platform}\n"
        f"TOPIC: {topic}\n\n"
        f"Generate optimised hashtags for {platform}.\n"
        f"Guideline: {spec.get('hashtags', '5 hashtags')}\n\n"
        f"Include:\n"
        f"- High volume tags (broad reach)\n"
        f"- Medium niche tags (engaged audience)\n"
        f"- Brand/industry specific tags\n\n"
        f"Also suggest 3-5 relevant emojis for this post.\n\n"
        f"Respond in JSON:\n"
        f"{FENCE}json\n"
        f"{{\n"
        f'  "hashtags": ["#tag1", "#tag2"],\n'
        f'  "emojis": ["🚀", "💡"],\n'
        f'  "caption_tip": "One tip for this platform"\n'
        f"}}\n"
        f"{FENCE}"
    )

    raw = call_llm(prompt, max_tokens=512)

    try:
        if FENCE in raw:
            parts = raw.split(FENCE)
            for part in parts:
                if part.startswith("json"):
                    raw = part[4:].strip()
                    break
        return json.loads(raw.strip())
    except Exception:
        return {
            "hashtags":    [f"#{brand.get('industry', 'tech').replace(' ', '')}"],
            "emojis":      ["🚀", "💡"],
            "caption_tip": "Post at optimal time for your audience"
        }


# ── 5. Improve existing post ──────────────────────────────────────────────────

def improve_post(
    post:      str,
    platform:  str,
    brand:     dict,
    goal:      str = "more engagement"
) -> str:
    """Improve an existing post for better performance."""
    spec      = PLATFORM_SPECS.get(platform, {})
    brand_ctx = build_brand_context(brand)

    prompt = (
        f"You are a social media expert.\n"
        f"Improve this {platform} post to achieve: {goal}\n\n"
        f"BRAND:\n{brand_ctx}\n"
        f"PLATFORM STYLE: {spec.get('style', '')}\n\n"
        f"ORIGINAL POST:\n{post}\n\n"
        f"Rewrite it to be more {goal}.\n"
        f"Keep the core message but make it more compelling.\n"
        f"Output the improved post only — no explanation."
    )

    return call_llm(prompt, max_tokens=512)


# ── 6. Batch generate week of posts ──────────────────────────────────────────

def generate_week_of_posts(brand: dict, platforms: list[str]) -> list[dict]:
    """Generate a full week of varied posts."""
    from brand_config import POST_TYPES
    import random

    topics_prompt = (
        f"Generate 7 specific, engaging content topics for a {brand.get('industry', 'tech')} brand "
        f"called {brand.get('name', 'Brand')} targeting {brand.get('audience', 'professionals')}.\n"
        f"Make each topic distinct and valuable.\n"
        f"Respond with a JSON array of 7 topic strings only.\n"
        f"{FENCE}json\n[\"topic1\", \"topic2\"]\n{FENCE}"
    )

    raw = call_llm(topics_prompt, max_tokens=512)
    try:
        if FENCE in raw:
            parts = raw.split(FENCE)
            for p in parts:
                if p.startswith("json"):
                    raw = p[4:].strip()
                    break
        topics = json.loads(raw.strip())
    except Exception:
        topics = [f"Topic {i+1} for {brand.get('industry', 'tech')}" for i in range(7)]

    week_posts = []
    for i, topic in enumerate(topics[:7]):
        platform  = platforms[i % len(platforms)]
        post_type = POST_TYPES[i % len(POST_TYPES)]
        posts     = generate_posts(topic, brand, [platform], post_type)

        week_posts.append({
            "day":       i + 1,
            "date":      (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
            "platform":  platform,
            "topic":     topic,
            "post_type": post_type,
            "content":   posts.get(platform, ""),
            "status":    "draft"
        })

    return week_posts