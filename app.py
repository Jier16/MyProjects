# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# === Define global date range ===
DATE_RANGE_END = datetime.now()
DATE_RANGE_START = DATE_RANGE_END - timedelta(weeks=2)

# Initialize session state
if "saved_articles" not in st.session_state:
    st.session_state.saved_articles = []
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"
if "all_articles" not in st.session_state:
    st.session_state.all_articles = []

# === Scraper Functions ===
# (Assume all your scraping functions like scrape_cspi, scrape_mighty_earth, scrape_cfs, scrape_ewg are defined here)

# === UI ===
st.set_page_config(page_title="Environmental News Aggregator", layout="wide")
st.markdown("""
<h1 style='font-size: 36px;'>
    <img src='https://twemoji.maxcdn.com/v/latest/svg/1f4c5.svg' width='36' style='vertical-align: middle;'/>
    Latest Articles from Selected Websites
</h1>
""", unsafe_allow_html=True)

# Top-right folder icon
with st.container():
    cols = st.columns([0.9, 0.1])
    with cols[1]:
        if st.button("📁 Saved ({})".format(len(st.session_state.saved_articles))):
            st.session_state.view_mode = "saved"

# Main view
if st.session_state.view_mode == "main":
    st.markdown(
        f"<p style='font-size:16px;'>Showing articles published between <strong>{DATE_RANGE_START.strftime('%b %d, %Y')}</strong> and <strong>{DATE_RANGE_END.strftime('%b %d, %Y')}</strong>.</p>",
        unsafe_allow_html=True
    )
    st.markdown("### Website Selection")
    select_all = st.checkbox("🔢 Select All Websites")
    show_cspi = st.checkbox("1️⃣ Center for Science in the Public Interest", value=select_all)
    show_mighty = st.checkbox("2️⃣ Mighty Earth", value=select_all)
    show_cfs = st.checkbox("3️⃣ Center for Food Safety", value=select_all)
    show_ewg = st.checkbox("4️⃣ Environmental Working Group", value=select_all)

    if st.button("Search"):
        st.session_state.all_articles = []
        if show_cspi:
            st.session_state.all_articles += scrape_cspi()
        if show_mighty:
            st.session_state.all_articles += scrape_mighty_earth()
        if show_cfs:
            st.session_state.all_articles += scrape_cfs()
        if show_ewg:
            st.session_state.all_articles += scrape_ewg()
        st.session_state.all_articles.sort(key=lambda x: x['date_obj'], reverse=True)

    if st.session_state.all_articles:
        for idx, article in enumerate(st.session_state.all_articles):
            is_saved = any(saved['link'] == article['link'] for saved in st.session_state.saved_articles)
            with st.container():
                col1, col2 = st.columns([0.95, 0.05])
                with col1:
                    st.markdown(f"""
                        <div style='display:flex;gap:20px;align-items:center;background-color:#f9f9f9;padding:20px;border-radius:10px;margin-bottom:20px;box-shadow:0 4px 8px rgba(0, 0, 0, 0.05);height:160px;'>
                            <div style='flex:2;'>
                                <h3 style='font-size:20px;margin:0;'>
                                    <a href='{article['link']}' target='_blank' style='text-decoration:none;color:#1a73e8;'>{article['title']}</a>
                                </h3>
                                <p style='font-size:14px;margin:5px 0 0;'><strong>Topic:</strong> {article['topic']}</p>
                                <p style='font-size:14px;margin:5px 0 0;'><strong>Date:</strong> {article['date']}</p>
                                <p style='font-size:14px;margin:5px 0 0;'><strong>Source:</strong> {article['source']}</p>
                            </div>
                            <div style='flex:1;text-align:right;'>
                                {"<img src='" + article['image'] + "' style='max-height:150px; max-width:100%; border-radius:10px;'/>" if article.get("image") else ""}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    key = f"star_{idx}"
                    icon = "★" if is_saved else "☆"
                    if st.button(icon, key=key):
                        if is_saved:
                            st.session_state.saved_articles = [a for a in st.session_state.saved_articles if a['link'] != article['link']]
                        else:
                            st.session_state.saved_articles.append(article)
    else:
        st.info("Click 'Search' to load articles from the selected sources.")

# Saved view
elif st.session_state.view_mode == "saved":
    st.markdown("<h2>📁 Saved Articles</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        if st.button("⬅️ Back to All Articles"):
            st.session_state.view_mode = "main"

    if st.session_state.saved_articles:
        for article in st.session_state.saved_articles:
            with st.container():
                st.markdown(f"""
                    <div style='display:flex;gap:20px;align-items:center;background-color:#f0fff0;padding:20px;border-radius:10px;margin-bottom:20px;box-shadow:0 4px 8px rgba(0, 0, 0, 0.05);height:160px;'>
                        <div style='flex:2;'>
                            <h3 style='font-size:20px;margin:0;'>
                                <a href='{article['link']}' target='_blank' style='text-decoration:none;color:#1a73e8;'>{article['title']}</a>
                            </h3>
                            <p style='font-size:14px;margin:5px 0 0;'><strong>Topic:</strong> {article['topic']}</p>
                            <p style='font-size:14px;margin:5px 0 0;'><strong>Date:</strong> {article['date']}</p>
                            <p style='font-size:14px;margin:5px 0 0;'><strong>Source:</strong> {article['source']}</p>
                        </div>
                        <div style='flex:1;text-align:right;'>
                            {"<img src='" + article['image'] + "' style='max-height:120px; max-width:100%; border-radius:10px;'/>" if article.get("image") else ""}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("You haven’t saved any articles yet. ⭐ them from the main view!")
