# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# === Define global date range ===
DATE_RANGE_END = datetime.now()
DATE_RANGE_START = DATE_RANGE_END - timedelta(weeks=2)

# === Session State Init ===
if "saved_articles" not in st.session_state:
    st.session_state.saved_articles = []
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"
if "all_articles" not in st.session_state:
    st.session_state.all_articles = []

# === Streamlit Config ===
st.set_page_config(page_title="🌍 Environmental News Aggregator", layout="wide")

# === Header ===
st.markdown("""
    <h1 style='font-size: 36px; font-weight: 600; margin-bottom: 10px;'>🌍 Environmental News Aggregator</h1>
    <p style='font-size: 18px; color: #555;'>Curated articles from top environmental organizations</p>
""", unsafe_allow_html=True)

# === Select Sources ===
st.markdown("### 🔍 Select News Sources")
source_box = st.container()
with source_box:
    col1, col2 = st.columns(2)
    with col1:
        select_all = st.checkbox("✅ Select All")
        show_cspi = st.checkbox("Center for Science in the Public Interest", value=select_all)
        show_mighty = st.checkbox("Mighty Earth", value=select_all)
    with col2:
        show_cfs = st.checkbox("Center for Food Safety", value=select_all)
        show_ewg = st.checkbox("Environmental Working Group", value=select_all)

# === Scrapers ===
def scrape_cspi():
    url = "https://www.cspi.org/page/media"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.find_all("div", class_="teaser-inner")
    data = []
    for a in articles:
        title = a.find("a").text.strip()
        link = a.find("a")["href"]
        date_str = a.find("time").text.strip()
        try:
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
        except:
            continue
        if date_obj >= DATE_RANGE_START:
            data.append({
                "title": title,
                "topic": a.find("span", class_="source").text.strip() if a.find("span", class_="source") else "Not specified",
                "date": date_obj.strftime("%b %d, %Y"),
                "date_obj": date_obj,
                "link": link,
                "source": "Center for Science in the Public Interest",
                "image": a.find("img")["src"] if a.find("img") else None
            })
    return data

def scrape_mighty_earth():
    url = "https://mightyearth.org/news/"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.find_all("div", class_="card card-article uk-transition-toggle reveal")
    data = []
    for a in articles:
        title = a.find("h5").text.strip()
        link = a.find("a", class_="card-link")["href"]
        date_str = a.find("span", class_="date").text.strip()
        try:
            date_obj = datetime.strptime(date_str, "%d/%b/%Y")
        except:
            continue
        if date_obj >= DATE_RANGE_START:
            data.append({
                "title": title,
                "topic": a.find("label").text.strip() if a.find("label") else "Not specified",
                "date": date_obj.strftime("%b %d, %Y"),
                "date_obj": date_obj,
                "link": link,
                "source": "Mighty Earth",
                "image": a.find("img")["src"] if a.find("img") else None
            })
    return data

def scrape_cfs():
    url = "https://www.centerforfoodsafety.org/press-releases"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.find_all("div", class_="no_a_color padB2")
    data = []
    for a in articles:
        title = a.find(class_="padB1").text.strip()
        link = "https://www.centerforfoodsafety.org" + a.find("a")["href"]
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', a.find(class_="txt_12").text.strip())
        try:
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
        except:
            continue
        if date_obj >= DATE_RANGE_START:
            data.append({
                "title": title,
                "topic": "Not specified",
                "date": date_obj.strftime("%b %d, %Y"),
                "date_obj": date_obj,
                "link": link,
                "source": "Center for Food Safety",
                "image": "https://www.centerforfoodsafety.org" + a.find("img")["src"] if a.find("img") else None
            })
    return data

def scrape_ewg():
    url = "https://www.ewg.org/news-insights/news-release"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.find_all("div", class_="wrapper")
    data = []
    for a in articles:
        link_el = a.find("a", href=re.compile("/news-release/"))
        if not link_el: continue
        title = link_el.text.strip()
        link = "https://www.ewg.org" + link_el["href"]
        date_str = a.find("time").text.strip()
        try:
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
        except:
            continue
        topics = [x.text for x in a.find_all("a", href=re.compile("/areas-focus/"))]
        topic = ", ".join(topics) if topics else "Not specified"
        img_el = a.find("img")
        image_url = "https://www.ewg.org" + img_el["src"] if img_el and img_el.get("src", "").startswith("/") else img_el["src"] if img_el else None
        if date_obj >= DATE_RANGE_START:
            data.append({
                "title": title,
                "topic": topic,
                "date": date_obj.strftime("%b %d, %Y"),
                "date_obj": date_obj,
                "link": link,
                "source": "Environmental Working Group",
                "image": image_url
            })
    return data

# === Action Buttons ===
st.markdown("---")
top_cols = st.columns([0.85, 0.15])
with top_cols[1]:
    if st.button(f"📁 Saved ({len(st.session_state.saved_articles)})"):
        st.session_state.view_mode = "saved"

# === Search Button ===
if st.button("🔎 Search Now"):
    st.session_state.all_articles = []
    if show_cspi:
        st.session_state.all_articles += scrape_cspi()
    if show_mighty:
        st.session_state.all_articles += scrape_mighty_earth()
    if show_cfs:
        st.session_state.all_articles += scrape_cfs()
    if show_ewg:
        st.session_state.all_articles += scrape_ewg()
    st.session_state.all_articles.sort(key=lambda x: x["date_obj"], reverse=True)

# === Main Card Renderer ===
def render_article(article, idx):
    is_saved = any(saved["link"] == article["link"] for saved in st.session_state.saved_articles)
    card_width = 500
    card_height = int(card_width / 1.618)
    image_width = int(card_width * 0.382)

    st.markdown(f"""
        <div style='display:flex;margin-bottom:30px;'>
            <div style='width:{card_width}px;height:{card_height}px;background:#f7f7f7;padding:20px;border-radius:12px;box-shadow:0 4px 8px rgba(0,0,0,0.06);display:flex;flex-direction:column;justify-content:center;'>
                <h3 style='margin:0;font-size:20px;line-height:1.3;'>
                    <a href="{article['link']}" target="_blank" style="text-decoration:none;color:#1a73e8;">{article['title']}</a>
                </h3>
                <p style='margin-top:10px;font-size:14px;'><strong>Topic:</strong> {article['topic']}</p>
                <p style='font-size:14px;'><strong>Date:</strong> {article['date']}</p>
                <p style='font-size:14px;'><strong>Source:</strong> {article['source']}</p>
            </div>
            <div style='width:{image_width}px;height:{card_height}px;margin-left:20px;display:flex;align-items:center;justify-content:center;'>
                {"<img src='" + article['image'] + "' style='max-height:100%; max-width:100%; border-radius:10px;'/>" if article.get("image") else ""}
            </div>
        </div>
    """, unsafe_allow_html=True)

    icon = "★" if is_saved else "☆"
    if st.button(icon, key=f"save_{idx}"):
        if is_saved:
            st.session_state.saved_articles = [a for a in st.session_state.saved_articles if a['link'] != article['link']]
        else:
            st.session_state.saved_articles.append(article)

# === Main or Saved View ===
if st.session_state.view_mode == "main":
    if st.session_state.all_articles:
        for idx, article in enumerate(st.session_state.all_articles):
            render_article(article, idx)
    else:
        st.info("Click 'Search Now' to load articles.")

elif st.session_state.view_mode == "saved":
    st.markdown("## 📁 Saved Articles")
    if st.button("⬅️ Back to Articles"):
        st.session_state.view_mode = "main"
    elif st.session_state.saved_articles:
        for idx, article in enumerate(st.session_state.saved_articles):
            render_article(article, idx)
    else:
        st.info("You haven’t saved any articles yet. Click ☆ to add some!")
