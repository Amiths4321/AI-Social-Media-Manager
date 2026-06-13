# AI Social Media Manager

A production-ready AI social media content generation and management tool built as **Project 24** in the AI Solution Architecture learning series. Generate on-brand posts for every platform, repurpose long content into social snippets, build 30-day content calendars, and manage your entire content pipeline — all powered by Qwen2.5-VL.

---

## Where this fits in the AI development lifecycle

```
1-23. All previous projects    ✅
24.   AI Social Media Manager  ← this project (content generation + scheduling)
25.   Docker + AWS             Upcoming
```

---

## Features

- **Post generator** — describe a topic → platform-optimised posts for LinkedIn, Twitter/X, Instagram, Facebook
- **Content repurposer** — paste any long content → 5-10 social posts extracted automatically
- **Content calendar** — 30-day calendar with topics, post types, and optimal posting times
- **Hashtag optimiser** — platform-specific hashtags, emojis, and caption tips
- **Brand voice engine** — every post matches your defined brand tone and audience
- **Post library** — SQLite storage for all drafts, approved, and published posts
- **CSV export** — export approved posts for Buffer, Hootsuite, or any scheduling tool
- **Analytics dashboard** — posts by platform, status breakdown, trends

---

## Platform-Specific Generation

| Platform | Style | Length | Hashtags |
|---|---|---|---|
| LinkedIn | Professional storytelling, thought leadership | 150-300 words | 3-5 professional |
| Twitter/X | Punchy, hook in first line | Max 280 chars | 1-2 max |
| Instagram | Visual-first, emoji-rich, call to action | 100-150 words | 20-30 niche |
| Facebook | Conversational, community-focused, question/poll | 100-250 words | 2-3 |

---

## Project Structure

```
social_media_manager/
│
├── social_app.py        # Streamlit UI — main entry point
├── content_ai.py        # all AI generation functions
├── post_store.py        # SQLite post library and brand storage
├── brand_config.py      # platform specs, tones, industries, post types
│
├── social_posts.db      # auto-created SQLite database
├── exports/             # CSV exports saved here
│
└── requirements.txt
```

---

## Prerequisites

- Python 3.9+
- Virtual environment activated
- Ollama running on remote GPU at `http://10.22.39.192:11434`
- Model `qwen2.5vl:latest` pulled on the remote GPU

---

## Installation

```powershell
cd social_media_manager

# Activate venv
C:\Dev\venv\Scripts\Activate.ps1

# Install
pip install -r requirements.txt
```

### `requirements.txt`

```
streamlit
requests
python-dotenv
pandas
```

---

## Running the App

```powershell
cd "C:\Users\amith\Desktop\Confidential\Misc Projects\P3\social_media_manager"
C:\Dev\venv\Scripts\Activate.ps1
streamlit run social_app.py
```

Open `http://localhost:8501`.

---

## Brand Profile Setup

Before generating content, configure your brand in the sidebar:

| Field | Description | Example |
|---|---|---|
| Brand name | Your company or personal brand | TechCorp India |
| Industry | Your sector | Technology / AI / Software |
| Target audience | Who you are speaking to | Tech professionals and business leaders |
| Brand tone | Communication style | Professional / Casual / Inspirational |
| Brand values | Core principles | Innovation, Quality, Trust |
| Tagline / USP | What makes you unique | Building the future with AI |

---

## The 6 Tone Options

| Tone | Description | Best for |
|---|---|---|
| Professional | Formal, expert, data-driven | B2B, consulting, finance |
| Casual & Friendly | Relaxed, conversational, warm | Consumer brands, lifestyle |
| Inspirational | Motivating, uplifting, aspirational | Coaches, non-profits, fitness |
| Educational | Informative, clear, teaching-focused | EdTech, media, research |
| Bold & Edgy | Provocative, opinionated, disruptive | Startups, tech challengers |
| Storytelling | Narrative, personal, emotional | Founders, personal brands |

---

## The 6 Tabs

### Tab 1 — ✍️ Generate
Enter a topic → select platforms → click Generate.
Each platform gets its own optimised post.
Edit inline, then Save draft or Approve directly.
Click **Improve** to ask AI to make a post more engaging.

### Tab 2 — ♻️ Repurpose
Paste any long content (blog post, article, README, meeting notes).
AI extracts 3-10 distinct angles and writes a social post for each.
Perfect for getting maximum value from content you have already created.

### Tab 3 — 📅 Calendar
Generate a 30-day content plan with:
- Specific topic per day
- Post type (educational, story, question, tips, etc.)
- Platform recommendation
- Optimal posting time

Download as CSV or generate all posts at once.

### Tab 4 — #️⃣ Hashtags
Enter any topic → select platform → get:
- Optimised hashtag set (platform-appropriate quantity)
- Relevant emojis
- One platform-specific caption tip

### Tab 5 — 📚 Post Library
All generated posts stored here.
Filter by status (draft / approved / published) or platform.
Edit content inline, approve, mark as published, or delete.

### Tab 6 — 📊 Analytics
Visual breakdown of your content pipeline:
- Posts by platform (bar chart)
- Posts by status (bar chart)
- Key metrics: total, drafts, approved, published
- Export all approved posts as CSV

---

## Recommended Workflow

```
Step 1: Set up brand profile (sidebar)
Step 2: Generate posts for today's topic (Tab 1)
Step 3: Edit and approve the best ones (Tab 1 or Tab 5)
Step 4: Repurpose existing content for more posts (Tab 2)
Step 5: Generate 30-day calendar (Tab 3)
Step 6: Export approved posts as CSV (Tab 6)
Step 7: Import CSV into Buffer / Hootsuite / Later for scheduling
```

---

## Content Repurposing — What Works Best

| Source content | Expected output |
|---|---|
| Blog post (1000 words) | 7-10 social posts from different angles |
| Meeting summary | 4-6 posts about decisions and learnings |
| Product README | 5-8 posts highlighting features and benefits |
| Research report | 6-10 posts with key statistics and insights |
| Case study | 5-7 posts about problem, solution, results |
| Annual report | 8-12 posts with financial and business highlights |

---

## Post Types Available

| Type | Description |
|---|---|
| Educational | Teach something valuable |
| Behind the scenes | Show how things work |
| Success story | Case study or win |
| Opinion / Hot take | Share a perspective |
| Question | Engage your audience |
| Tips & Tricks | Quick actionable advice |
| Product / Service announcement | Launch or feature update |
| Industry news commentary | React to news |
| Team / Culture spotlight | People and values |
| Personal story / Lesson learned | Authentic narrative |

---

## Known Fix — SQL Reserved Keyword

The original `post_store.py` used `values` as a column name in the brands table. This is a reserved SQL keyword and causes:

```
sqlite3.OperationalError: near "values": syntax error
```

**Fix applied:** Column renamed to `brand_values` in the SQL schema. The Python dict key remains `"values"` throughout the code — only the database column name changed.

If you see this error, delete `social_posts.db` and restart:

```powershell
Remove-Item social_posts.db -ErrorAction SilentlyContinue
streamlit run social_app.py
```

---

## Integrating with Scheduling Tools

After exporting your CSV from the Analytics tab:

### Buffer
Settings → Content → Import → Upload CSV
CSV columns map to: content → Message, scheduled_for → Schedule Date, platform → Profile

### Hootsuite
Planner → Bulk Composer → Upload CSV
Use the same CSV format

### Meta Business Suite (Facebook + Instagram)
Content → Creator Studio → Schedule → Import

---

## Extending the Project

### Add image prompt generation

```python
def generate_image_prompt(post_content: str, platform: str) -> str:
    """Generate a DALL-E or Stable Diffusion prompt for the post image."""
    prompt = (
        f"Based on this {platform} post, write a detailed image generation prompt.\n"
        f"The image should visually represent the post's message.\n\n"
        f"POST:\n{post_content}\n\n"
        f"IMAGE PROMPT:"
    )
    return call_llm(prompt, max_tokens=200)
```

### Add competitor analysis

```python
def analyse_competitor_content(competitor_posts: list[str], brand: dict) -> str:
    """Analyse competitor posts and suggest differentiation."""
    posts_text = "\n\n".join(competitor_posts[:5])
    prompt = (
        f"Analyse these competitor social media posts and suggest how "
        f"{brand['name']} can differentiate its content.\n\n"
        f"COMPETITOR POSTS:\n{posts_text}\n\n"
        f"OUR BRAND: {brand['name']} — {brand['tagline']}\n\n"
        f"DIFFERENTIATION STRATEGY:"
    )
    return call_llm(prompt)
```

### Add A/B testing variants

```python
def generate_ab_variants(post: str, platform: str, brand: dict) -> list[str]:
    """Generate 3 variants of a post for A/B testing."""
    variants = []
    angles = ["different hook", "question-based opening", "statistic-led opening"]
    for angle in angles:
        improved = improve_post(post, platform, brand, angle)
        variants.append(improved)
    return variants
```

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `near "values": syntax error` | Reserved SQL keyword in schema | Delete `social_posts.db`, use fixed `post_store.py` |
| `Ollama connection error` | Remote GPU not reachable | Check `curl http://10.22.39.192:11434/api/tags` |
| `JSON parse error in repurpose` | LLM returned non-JSON | Fallback used automatically, retry |
| Calendar generates 0 posts | JSON parse failed | Retry — LLM temperature 0.7 means occasional format variations |

---

## Part of a Larger Project Series

| # | Project | Core skill learned |
|---|---|---|
| 6 | Multi-Agent Research | Web research, content synthesis |
| 16 | Document Generator | Structured content creation |
| 23 | Memory Chatbot | Brand voice consistency via personality |
| 24 | **AI Social Media Manager** | **Platform-specific generation, content calendar, repurposing** |
| 25 | Docker + AWS | Containers, cloud deployment |

---

## Author

Built as part of an AI Solution Architecture learning project.
Model: `qwen2.5vl:latest` via Ollama on remote GPU `10.22.39.192:11434`
Storage: SQLite (local, persistent)
No OpenAI · No Anthropic · Fully open source
