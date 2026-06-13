# social_app.py
# streamlit run social_app.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas    as pd
from pathlib     import Path
from post_store  import init_db, save_post, get_posts, update_post_status, update_post_content, delete_post, save_brand, get_brands, export_posts_csv
from content_ai  import generate_posts, repurpose_content, generate_content_calendar, generate_hashtags, improve_post, generate_week_of_posts
from brand_config import PLATFORM_SPECS, TONE_OPTIONS, INDUSTRY_OPTIONS, POST_TYPES

init_db()

st.set_page_config(
    page_title="AI Social Media Manager",
    page_icon="📱",
    layout="wide"
)

# ── Session state ─────────────────────────────────────────────────────────────
if "brand" not in st.session_state:
    st.session_state.brand = {
        "name":     "TechCorp India",
        "industry": "Technology / AI / Software",
        "audience": "Tech professionals and business leaders",
        "tone":     "Professional",
        "values":   "Innovation, Quality, Trust",
        "tagline":  "Building the future with AI"
    }

# ── Sidebar — brand setup ─────────────────────────────────────────────────────
with st.sidebar:
    st.title("📱 AI Social Media Manager")
    st.caption("Generate · Schedule · Publish")

    st.divider()
    st.markdown("**Your brand**")

    with st.expander("Edit brand profile", expanded=False):
        brand = st.session_state.brand
        brand["name"]     = st.text_input("Brand name:",     value=brand["name"])
        brand["industry"] = st.selectbox("Industry:",        INDUSTRY_OPTIONS,
                                          index=INDUSTRY_OPTIONS.index(brand["industry"])
                                          if brand["industry"] in INDUSTRY_OPTIONS else 0)
        brand["audience"] = st.text_input("Target audience:", value=brand["audience"])
        brand["tone"]     = st.selectbox("Brand tone:",      list(TONE_OPTIONS.keys()),
                                          index=list(TONE_OPTIONS.keys()).index(brand["tone"])
                                          if brand["tone"] in TONE_OPTIONS else 0)
        brand["values"]   = st.text_input("Brand values:",   value=brand["values"])
        brand["tagline"]  = st.text_input("Tagline / USP:",  value=brand["tagline"])

        if st.button("Save brand", use_container_width=True):
            save_brand(brand)
            st.session_state.brand = brand
            st.success("Brand saved!")

    st.divider()

    # Stats
    all_posts     = get_posts()
    draft_posts   = get_posts(status="draft")
    approved_posts = get_posts(status="approved")

    col1, col2 = st.columns(2)
    col1.metric("Total posts",   len(all_posts))
    col2.metric("Approved",      len(approved_posts))

    if approved_posts:
        if st.button("Export approved as CSV", use_container_width=True):
            csv_path = export_posts_csv("approved")
            st.success(f"Exported: {Path(csv_path).name}")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("📱 AI Social Media Manager")
st.caption("Generate on-brand content for every platform instantly")

brand = st.session_state.brand

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "✍️ Generate",
    "♻️ Repurpose",
    "📅 Calendar",
    "#️⃣ Hashtags",
    "📚 Post Library",
    "📊 Analytics"
])

# ── Tab 1: Generate posts ─────────────────────────────────────────────────────
with tab1:
    st.subheader("Generate posts for all platforms")

    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_area(
            "What do you want to post about?",
            height=100,
            placeholder="e.g. We just launched a new AI feature that reduces customer support time by 60%"
        )
    with col2:
        post_type = st.selectbox("Post type:", POST_TYPES, key="gen_type")
        platforms = st.multiselect(
            "Platforms:",
            list(PLATFORM_SPECS.keys()),
            default=["LinkedIn", "Twitter/X"]
        )

    if st.button("Generate posts", type="primary") and topic and platforms:
        with st.spinner("Generating posts..."):
            posts = generate_posts(topic, brand, platforms, post_type)

        for platform, content in posts.items():
            spec = PLATFORM_SPECS[platform]
            st.markdown(f"### {spec['icon']} {platform}")

            char_count = len(content)
            max_chars  = spec["max_chars"]
            color      = "green" if char_count <= max_chars else "red"

            edited = st.text_area(
                f"Edit {platform} post:",
                value  = content,
                height = 150,
                key    = f"edit_{platform}"
            )
            st.caption(f"{char_count}/{max_chars} characters")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"✅ Save to library", key=f"save_{platform}"):
                    save_post({
                        "platform":  platform,
                        "topic":     topic,
                        "post_type": post_type,
                        "content":   edited,
                        "status":    "draft",
                        "brand_name": brand["name"]
                    })
                    st.success("Saved!")
            with col2:
                if st.button(f"✨ Improve", key=f"improve_{platform}"):
                    with st.spinner("Improving..."):
                        improved = improve_post(edited, platform, brand, "more engaging")
                    st.text_area(f"Improved:", improved, height=150, key=f"imp_{platform}")
            with col3:
                if st.button(f"✅ Approve & save", key=f"approve_{platform}"):
                    save_post({
                        "platform":  platform,
                        "topic":     topic,
                        "post_type": post_type,
                        "content":   edited,
                        "status":    "approved",
                        "brand_name": brand["name"]
                    })
                    st.success("Approved!")

            st.divider()

# ── Tab 2: Repurpose content ──────────────────────────────────────────────────
with tab2:
    st.subheader("Turn long content into social posts")
    st.caption("Upload or paste a blog post, article, or meeting summary")

    long_content = st.text_area(
        "Paste your long-form content:",
        height=250,
        placeholder="Paste a blog post, article, report, or any long text..."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        rep_platforms = st.multiselect(
            "Platforms:",
            list(PLATFORM_SPECS.keys()),
            default=["LinkedIn", "Twitter/X", "Instagram"],
            key="rep_plat"
        )
    with col2:
        num_posts = st.slider("Number of posts:", 3, 10, 5)
    with col3:
        rep_btn = st.button("Repurpose", type="primary")

    if rep_btn and long_content and rep_platforms:
        with st.spinner(f"Creating {num_posts} posts from your content..."):
            repurposed = repurpose_content(long_content, brand, rep_platforms, num_posts)

        for i, post in enumerate(repurposed):
            with st.expander(
                f"{PLATFORM_SPECS.get(post.get('platform','LinkedIn'), {}).get('icon', '📝')} "
                f"Post {i+1}: {post.get('angle', '')}",
                expanded=(i == 0)
            ):
                st.markdown(f"**Platform:** {post.get('platform', '')}")
                edited = st.text_area(
                    "Content:",
                    value  = post.get("content", ""),
                    height = 150,
                    key    = f"rep_{i}"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save draft", key=f"rep_save_{i}"):
                        save_post({
                            "platform":   post.get("platform", ""),
                            "topic":      post.get("angle", "Repurposed content"),
                            "content":    edited,
                            "status":     "draft",
                            "brand_name": brand["name"]
                        })
                        st.success("Saved!")
                with col2:
                    if st.button("Approve", key=f"rep_approve_{i}"):
                        save_post({
                            "platform":   post.get("platform", ""),
                            "topic":      post.get("angle", "Repurposed content"),
                            "content":    edited,
                            "status":     "approved",
                            "brand_name": brand["name"]
                        })
                        st.success("Approved!")

# ── Tab 3: Content calendar ───────────────────────────────────────────────────
with tab3:
    st.subheader("30-day content calendar")

    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox("Calendar length:", [7, 14, 30], index=2)
    with col2:
        ppw = st.slider("Posts per week:", 3, 7, 5)

    if st.button("Generate calendar", type="primary"):
        with st.spinner("Building your content calendar..."):
            calendar = generate_content_calendar(brand, days, ppw)

        if calendar:
            df = pd.DataFrame(calendar)
            st.dataframe(df, use_container_width=True)

            # Download calendar as CSV
            csv_content = df.to_csv(index=False)
            st.download_button(
                "Download calendar as CSV",
                csv_content,
                file_name   = f"content_calendar_{days}days.csv",
                mime        = "text/csv",
                use_container_width = True
            )

            # Generate all posts from calendar
            st.divider()
            if st.button("Generate all posts from calendar"):
                progress = st.progress(0)
                for i, item in enumerate(calendar):
                    platform = item.get("platform", "LinkedIn")
                    topic    = item.get("topic", "")
                    ptype    = item.get("post_type", "Educational")

                    posts = generate_posts(topic, brand, [platform], ptype)
                    save_post({
                        "platform":     platform,
                        "topic":        topic,
                        "post_type":    ptype,
                        "content":      posts.get(platform, ""),
                        "scheduled_for": item.get("date", ""),
                        "status":       "draft",
                        "brand_name":   brand["name"]
                    })
                    progress.progress((i + 1) / len(calendar))

                st.success(f"Generated {len(calendar)} posts! View in Post Library tab.")
        else:
            st.warning("Could not generate calendar. Try again.")

# ── Tab 4: Hashtag optimiser ──────────────────────────────────────────────────
with tab4:
    st.subheader("Hashtag and emoji optimiser")

    col1, col2 = st.columns(2)
    with col1:
        hash_topic    = st.text_input("Topic or post content:", placeholder="AI in healthcare")
    with col2:
        hash_platform = st.selectbox("Platform:", list(PLATFORM_SPECS.keys()), key="hash_plat")

    if st.button("Generate hashtags", type="primary") and hash_topic:
        with st.spinner("Optimising hashtags..."):
            result = generate_hashtags(hash_topic, hash_platform, brand)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Hashtags**")
            hashtags_text = " ".join(result.get("hashtags", []))
            st.text_area("Copy these:", hashtags_text, height=120)

        with col2:
            st.markdown("**Emojis**")
            emojis_text = " ".join(result.get("emojis", []))
            st.markdown(f"## {emojis_text}")

        with col3:
            st.markdown("**Platform tip**")
            st.info(result.get("caption_tip", ""))

# ── Tab 5: Post library ───────────────────────────────────────────────────────
with tab5:
    st.subheader("Post library")

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status   = st.selectbox("Status:", ["all", "draft", "approved", "published"])
    with col2:
        filter_platform = st.selectbox("Platform:", ["all"] + list(PLATFORM_SPECS.keys()))
    with col3:
        st.metric("Showing", len(get_posts(
            status   = None if filter_status == "all"   else filter_status,
            platform = None if filter_platform == "all" else filter_platform
        )))

    posts = get_posts(
        status   = None if filter_status == "all"   else filter_status,
        platform = None if filter_platform == "all" else filter_platform
    )

    if not posts:
        st.info("No posts yet. Generate some in the other tabs.")
    else:
        for post in posts:
            platform = post.get("platform", "")
            icon     = PLATFORM_SPECS.get(platform, {}).get("icon", "📝")
            status   = post.get("status", "draft")
            status_icon = {"draft": "📝", "approved": "✅", "published": "🚀"}.get(status, "📝")

            with st.expander(
                f"{icon} {platform} · {status_icon} {status.upper()} · {post.get('topic', '')[:40]}",
                expanded=False
            ):
                edited = st.text_area(
                    "Content:",
                    value  = post.get("content", ""),
                    height = 150,
                    key    = f"lib_{post['id']}"
                )

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("✅ Approve", key=f"lib_approve_{post['id']}"):
                        update_post_status(post["id"], "approved")
                        st.rerun()
                with col2:
                    if st.button("🚀 Publish", key=f"lib_publish_{post['id']}"):
                        update_post_status(post["id"], "published")
                        st.rerun()
                with col3:
                    if st.button("💾 Save edits", key=f"lib_save_{post['id']}"):
                        update_post_content(post["id"], edited)
                        st.success("Saved!")
                with col4:
                    if st.button("🗑️ Delete", key=f"lib_delete_{post['id']}"):
                        delete_post(post["id"])
                        st.rerun()

                if post.get("scheduled_for"):
                    st.caption(f"Scheduled: {post['scheduled_for']}")

# ── Tab 6: Analytics ──────────────────────────────────────────────────────────
with tab6:
    st.subheader("Content analytics")

    all_posts = get_posts()
    if not all_posts:
        st.info("Generate some posts to see analytics.")
    else:
        df = pd.DataFrame(all_posts)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total posts",     len(df))
        col2.metric("Drafts",          len(df[df["status"] == "draft"]))
        col3.metric("Approved",        len(df[df["status"] == "approved"]))
        col4.metric("Published",       len(df[df["status"] == "published"]))

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Posts by platform**")
            platform_counts = df["platform"].value_counts()
            st.bar_chart(platform_counts)

        with col2:
            st.markdown("**Posts by status**")
            status_counts = df["status"].value_counts()
            st.bar_chart(status_counts)

        st.divider()

        # Export
        if st.button("Export all approved posts as CSV", type="primary"):
            csv_path = export_posts_csv("approved")
            with open(csv_path) as f:
                st.download_button(
                    "Download CSV",
                    f.read(),
                    file_name           = Path(csv_path).name,
                    mime                = "text/csv",
                    use_container_width = True,
                    key                 = "analytics_export"
                )