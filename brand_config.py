# brand_config.py

PLATFORM_SPECS = {
    "LinkedIn": {
        "icon":         "💼",
        "max_chars":     3000,
        "optimal_chars": 200,
        "hashtags":      "3-5 professional hashtags",
        "style":         (
            "Professional and insightful. Tell a story or share a lesson. "
            "Start with a strong hook (not 'I am excited to...'). "
            "Use line breaks for readability. End with a question or call to action. "
            "150-300 words optimal. No more than 5 hashtags at the end."
        )
    },
    "Twitter/X": {
        "icon":         "🐦",
        "max_chars":     280,
        "optimal_chars": 240,
        "hashtags":      "1-2 hashtags max",
        "style":         (
            "Punchy and direct. Max 280 characters. "
            "Hook must be in the very first line. "
            "Use simple language. 1-2 hashtags maximum. "
            "Can include a thread indicator (1/n) if content needs multiple tweets."
        )
    },
    "Instagram": {
        "icon":         "📸",
        "max_chars":     2200,
        "optimal_chars": 150,
        "hashtags":      "20-30 niche hashtags",
        "style":         (
            "Visual storytelling — write as if describing an image. "
            "Start with an attention-grabbing first line. "
            "Use emojis naturally throughout. "
            "Include a clear call to action. "
            "Add 20-30 relevant hashtags at the end separated by line break."
        )
    },
    "Facebook": {
        "icon":         "👥",
        "max_chars":     63206,
        "optimal_chars": 250,
        "hashtags":      "2-3 hashtags",
        "style":         (
            "Conversational and community-focused. "
            "Ask a question to drive comments. "
            "Medium length — 100-250 words. "
            "Personal and relatable tone. "
            "Consider ending with a poll question. 2-3 hashtags."
        )
    }
}

TONE_OPTIONS = {
    "Professional":    "formal, expert, data-driven, authoritative",
    "Casual & Friendly": "relaxed, approachable, conversational, warm",
    "Inspirational":   "motivating, uplifting, thought-provoking, aspirational",
    "Educational":     "informative, clear, helpful, teaching-focused",
    "Bold & Edgy":     "provocative, opinionated, direct, disruptive",
    "Storytelling":    "narrative-driven, personal, emotional, journey-based"
}

INDUSTRY_OPTIONS = [
    "Technology / AI / Software",
    "Finance / Banking / Fintech",
    "Healthcare / Medical",
    "Education / E-learning",
    "E-commerce / Retail",
    "Marketing / Advertising",
    "Real Estate",
    "HR / Recruitment",
    "Legal / Consulting",
    "Manufacturing / Supply Chain",
    "Food & Beverage",
    "Fashion / Lifestyle",
    "Other"
]

POST_TYPES = [
    "Educational — teach something valuable",
    "Behind the scenes — show how things work",
    "Success story — case study or win",
    "Opinion / Hot take — share a perspective",
    "Question — engage your audience",
    "Tips & Tricks — quick actionable advice",
    "Product / Service announcement",
    "Industry news commentary",
    "Team / Culture spotlight",
    "Personal story / Lesson learned"
]