# -*- coding: utf-8 -*-
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# === Define global date range ===
DATE_RANGE_END = datetime.now()
DATE_RANGE_START = DATE_RANGE_END - timedelta(weeks=2)

# === Set up Streamlit page ===
st.set_page_config(page_title="🌍 Environmental News Aggregator", layout="wide")
st.markdown("""
    <style>
        .checkbox-row {
            display: flex;
            gap: 2em;
            flex-wrap: wrap;
        }
        .checkbox-row label {
            font-size: 16px;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='font-size: 40px; font-weight: 700; color: #2c3e50;'>🌍 Environmental News Aggregator</h1>
    <p style='font-size: 18px; color: #555;'>Discover the latest articles from trusted environmental sources, updated every 2 weeks.</p>
""", unsafe_allow_html=True)

# === Initialize session state ===
if "saved_articles" not in st.session_state:
    st.session_state.saved_articles = []
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"
if "all_articles" not in st.session_state:
    st.session_state.all_articles = []

# === Scraper for EWG ===
def scrape_ewg():
    URL = "https://www.ewg.org/news-insights/news-release"
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(URL, headers=headers)
    articles_data = []

    if page.status_code != 403:
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('div', class_='wrapper')

        for a in articles:
            date_element = a.find("time")
            link_element = a.find("a", href=re.compile("/news-release/"))
            img_element = a.find("img")
            image_url = f"https://www.ewg.org{img_element['src']}" if img_element and img_element.get("src", "").startswith("/") else (img_element['src'] if img_element else None)
            title = link_element.text.strip() if link_element else "Title not found"
            link = f"https://www.ewg.org{link_element['href']}" if link_element else "Link not found"

            all_links = a.find_all("a")
            topic_links = [link for link in all_links if "/areas-focus/" in link.get("href", "")]
            topics = [link.text.strip() for link in topic_links]
            topic_text = ", ".join(topics) if topics else "Topic not found"

            if date_element:
                try:
                    article_date = datetime.strptime(date_element.text.strip(), "%B %d, %Y")
                except:
                    continue
                if article_date >= DATE_RANGE_START:
                    formatted_date = article_date.strftime("%b %d, %Y")
                    articles_data.append({
                        "title": title,
                        "topic": topic_text,
                        "date": formatted_date,
                        "date_obj": article_date,
                        "link": link,
                        "source": "Environmental Working Group",
                        "image": image_url
                    })
    return articles_data

# === UI ===
st.markdown(f"<p style='font-size:16px;'>Showing articles from <strong>{DATE_RANGE_START.strftime('%b %d, %Y')}</strong> to <strong>{DATE_RANGE_END.strftime('%b %d, %Y')}</strong>.</p>", unsafe_allow_html=True)

col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.button(f"📁 Saved ({len(st.session_state.saved_articles)})"):
        st.session_state.view_mode = "saved"

if st.session_state.view_mode == "main":
    with st.container():
        st.markdown("<div class='checkbox-row'>", unsafe_allow_html=True)
        select_all = st.checkbox("Select All")
        show_ewg = st.checkbox("🌿 Environmental Working Group", value=select_all)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔍 Search"):
        st.session_state.all_articles = []
        if show_ewg:
            st.session_state.all_articles += scrape_ewg()
        st.session_state.all_articles.sort(key=lambda x: x['date_obj'], reverse=True)

    golden_ratio = 1.618
    card_height = 250
    card_width = int(card_height * golden_ratio)
    image_width = int(card_width * 0.618)

    for idx, article in enumerate(st.session_state.all_articles):
        is_saved = any(saved['link'] == article['link'] for saved in st.session_state.saved_articles)
        with st.container():
            col_main, col_save = st.columns([0.95, 0.05])
            with col_main:
                st.markdown(f"""
                <div style='display: flex; align-items: center; justify-content: space-between; background-color: #f8f8f8; border-radius: 10px; padding: 20px; margin-bottom: 20px; height: {card_height}px;'>
                    <div style='flex: 1; padding-right: 20px;'>
                        <h3 style='font-size: 20px; margin: 0; color: #2c3e50;'>
                            <a href='{article['link']}' target='_blank' style='text-decoration: none; color: #1a73e8;'>{article['title']}</a>
                        </h3>
                        <p style='font-size: 14px; margin: 8px 0 0;'><strong>Topic:</strong> {article['topic']}</p>
                        <p style='font-size: 14px; margin: 4px 0 0;'><strong>Date:</strong> {article['date']}</p>
                        <p style='font-size: 14px; margin: 4px 0 0;'><strong>Source:</strong> {article['source']}</p>
                    </div>
                    <div style='flex-shrink: 0; width: {image_width}px; height: {card_height}px; display: flex; align-items: center; justify-content: center;'>
                        {f"<img src='{article['image']}' style='max-height: 100%; max-width: 100%; border-radius: 10px; object-fit: cover;'/>" if article.get("image") else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_save:
                key = f"save_{idx}"
                icon = "★" if is_saved else "☆"
                if st.button(icon, key=key):
                    if is_saved:
                        st.session_state.saved_articles = [a for a in st.session_state.saved_articles if a['link'] != article['link']]
                    else:
                        st.session_state.saved_articles.append(article)

elif st.session_state.view_mode == "saved":
    st.markdown("<h2>📁 Saved Articles</h2>", unsafe_allow_html=True)
    if st.button("⬅️ Back"):
        st.session_state.view_mode = "main"

    for article in st.session_state.saved_articles:
        st.markdown(f"""
        <div style='display: flex; align-items: center; justify-content: space-between; background-color: #f0fff0; border-radius: 10px; padding: 20px; margin-bottom: 20px; height: {card_height}px;'>
            <div style='flex: 1; padding-right: 20px;'>
                <h3 style='font-size: 20px; margin: 0; color: #2c3e50;'>
                    <a href='{article['link']}' target='_blank' style='text-decoration: none; color: #1a73e8;'>{article['title']}</a>
                </h3>
                <p style='font-size: 14px; margin: 8px 0 0;'><strong>Topic:</strong> {article['topic']}</p>
                <p style='font-size: 14px; margin: 4px 0 0;'><strong>Date:</strong> {article['date']}</p>
                <p style='font-size: 14px; margin: 4px 0 0;'><strong>Source:</strong> {article['source']}</p>
            </div>
            <div style='flex-shrink: 0; width: {image_width}px; height: {card_height}px; display: flex; align-items: center; justify-content: center;'>
                {f"<img src='{article['image']}' style='max-height: 100%; max-width: 100%; border-radius: 10px; object-fit: cover;'/>" if article.get("image") else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
    if not st.session_state.saved_articles:
        st.info("You haven’t saved any articles yet. ⭐ them from the main view!")
