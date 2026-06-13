# post_store.py
import sqlite3
from datetime import datetime
from pathlib  import Path

DB_PATH    = "social_posts.db"
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS posts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            platform      TEXT,
            topic         TEXT,
            post_type     TEXT,
            content       TEXT,
            hashtags      TEXT,
            status        TEXT DEFAULT 'draft',
            scheduled_for TEXT,
            created_at    TEXT,
            updated_at    TEXT,
            brand_name    TEXT
        );

        CREATE TABLE IF NOT EXISTS brands (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT UNIQUE,
            industry     TEXT,
            audience     TEXT,
            tone         TEXT,
            brand_values TEXT,
            tagline      TEXT,
            created_at   TEXT
        );
    """)
    conn.commit()
    conn.close()


# ── User operations ───────────────────────────────────────────────────────────

def save_post(post: dict) -> int:
    conn = get_conn()
    now  = datetime.now().isoformat()
    cur  = conn.execute(
        "INSERT INTO posts (platform, topic, post_type, content, hashtags, "
        "status, scheduled_for, created_at, updated_at, brand_name) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            post.get("platform", ""),
            post.get("topic", ""),
            post.get("post_type", ""),
            post.get("content", ""),
            post.get("hashtags", ""),
            post.get("status", "draft"),
            post.get("scheduled_for", ""),
            now, now,
            post.get("brand_name", "")
        )
    )
    conn.commit()
    post_id = cur.lastrowid
    conn.close()
    return post_id


def get_posts(
    status:   str = None,
    platform: str = None,
    limit:    int = 50
) -> list:
    conn  = get_conn()
    query = "SELECT * FROM posts WHERE 1=1"
    args  = []

    if status:
        query += " AND status = ?"
        args.append(status)
    if platform:
        query += " AND platform = ?"
        args.append(platform)

    query += " ORDER BY created_at DESC LIMIT ?"
    args.append(limit)

    rows = conn.execute(query, args).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_post_status(post_id: int, status: str):
    conn = get_conn()
    conn.execute(
        "UPDATE posts SET status = ?, updated_at = ? WHERE id = ?",
        (status, datetime.now().isoformat(), post_id)
    )
    conn.commit()
    conn.close()


def update_post_content(post_id: int, content: str):
    conn = get_conn()
    conn.execute(
        "UPDATE posts SET content = ?, updated_at = ? WHERE id = ?",
        (content, datetime.now().isoformat(), post_id)
    )
    conn.commit()
    conn.close()


def delete_post(post_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()


def save_brand(brand: dict):
    conn = get_conn()
    now  = datetime.now().isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO brands "
        "(name, industry, audience, tone, brand_values, tagline, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            brand.get("name", ""),
            brand.get("industry", ""),
            brand.get("audience", ""),
            brand.get("tone", ""),
            brand.get("values", ""),   # key in dict stays "values"
            brand.get("tagline", ""),
            now
        )
    )
    conn.commit()
    conn.close()


def get_brands() -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM brands ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_posts_csv(status: str = "approved") -> str:
    """Export posts to CSV."""
    import csv
    posts    = get_posts(status=status)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = EXPORT_DIR / f"posts_{status}_{ts}.csv"

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        if posts:
            writer = csv.DictWriter(f, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)

    return str(filepath)