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

# === Scraper Function Example (one site only, for brevity) ===
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
            image_url = f"https://www.ewg.org{img_element['src']}" if img_element and img_element.get("src", "").startswith("/") else img_element['src'] if img_element else None
            title_element = link_element.text.strip() if link_element else "Title not found"

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
                        "title": title_element,
                        "topic": topic_text,
                        "date": formatted_date,
                        "date_obj": article_date,
                        "link": f"https://www.ewg.org{link_element['href']}" if link_element else "Link not found",
                        "source": "Environmental Working Group",
                        "image": image_url
                    })
    return articles_data

# === UI ===
st.set_page_config(page_title="🌍 Environmental News Aggregator", layout="wide")
st.markdown("""
    <h1 style='font-size: 40px; text-align: center; margin-bottom: 10px;'>🌱 Environmental News Aggregator</h1>
    <p style='text-align: center; color: gray; font-size: 18px;'>Curated updates from trusted environmental sources, refreshed every 2 weeks.</p>
    <hr style='margin-top: 10px; margin-bottom: 20px;'>
""", unsafe_allow_html=True)

# Top-right folder icon
cols = st.columns([0.9, 0.1])
with cols[1]:
    if st.button(f"📁 Saved ({len(st.session_state.saved_articles)})"):
        st.session_state.view_mode = "saved"

# === Main View ===
if st.session_state.view_mode == "main":
    st.markdown(f"""
        <p style='font-size:16px;'>Showing articles from <strong>{DATE_RANGE_START.strftime('%b %d, %Y')}</strong> to <strong>{DATE_RANGE_END.strftime('%b %d, %Y')}</strong></p>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""<h4 style='margin-bottom: 5px;'>Choose Sources:</h4>""", unsafe_allow_html=True)
        select_all = st.checkbox("Select All", key="select_all")
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                show_cspi = st.checkbox("Center for Science in the Public Interest", value=select_all)
                show_mighty = st.checkbox("Mighty Earth", value=select_all)
            with col2:
                show_cfs = st.checkbox("Center for Food Safety", value=select_all)
                show_ewg = st.checkbox("Environmental Working Group", value=select_all)

    if st.button("🔍 Search Articles"):
        st.session_state.all_articles = []
        if show_ewg:
            st.session_state.all_articles += scrape_ewg()
        st.session_state.all_articles.sort(key=lambda x: x['date_obj'], reverse=True)

    if st.session_state.all_articles:
        for idx, article in enumerate(st.session_state.all_articles):
            is_saved = any(saved['link'] == article['link'] for saved in st.session_state.saved_articles)
            with st.container():
                st.markdown(f"""
                    <div style='display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 30px;'>
                        <div style='width: 618px; height: 236px; background-color: #f9f9f9; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); display: flex; flex-direction: column; justify-content: center;'>
                            <h3 style='font-size: 20px; margin: 0 0 12px; line-height: 1.3;'>
                                <a href="{article['link']}" target="_blank" style="text-decoration: none; color: #1a73e8;">{article['title']}</a>
                            </h3>
                            <p style='font-size: 14px; margin: 4px 0;'><strong>Topic:</strong> {article['topic']}</p>
                            <p style='font-size: 14px; margin: 4px 0;'><strong>Date:</strong> {article['date']}</p>
                            <p style='font-size: 14px; margin: 4px 0;'><strong>Source:</strong> {article['source']}</p>
                        </div>
                        <div style='width: 382px; height: 236px; display: flex; align-items: center; justify-content: center;'>
                            {"<img src='" + article['image'] + "' style='height: 100%; width: auto; border-radius: 12px; object-fit: cover;'/>" if article.get("image") else ""}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                star_key = f"star_{idx}"
                if st.button("★" if is_saved else "☆", key=star_key):
                    if is_saved:
                        st.session_state.saved_articles = [a for a in st.session_state.saved_articles if a['link'] != article['link']]
                    else:
                        st.session_state.saved_articles.append(article)
    else:
        st.info("Click 'Search Articles' to load the latest news from selected sources.")

# === Saved Articles View ===
elif st.session_state.view_mode == "saved":
    st.markdown("<h2 style='margin-top:0;'>📁 Saved Articles</h2>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Articles"):
        st.session_state.view_mode = "main"

    if st.session_state.saved_articles:
        for article in st.session_state.saved_articles:
            st.markdown(f"""
                <div style='display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 30px;'>
                    <div style='width: 618px; height: 236px; background-color: #f0fff0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); display: flex; flex-direction: column; justify-content: center;'>
                        <h3 style='font-size: 20px; margin: 0 0 12px; line-height: 1.3;'>
                            <a href="{article['link']}" target="_blank" style="text-decoration: none; color: #1a73e8;">{article['title']}</a>
                        </h3>
                        <p style='font-size: 14px; margin: 4px 0;'><strong>Topic:</strong> {article['topic']}</p>
                        <p style='font-size: 14px; margin: 4px 0;'><strong>Date:</strong> {article['date']}</p>
                        <p style='font-size: 14px; margin: 4px 0;'><strong>Source:</strong> {article['source']}</p>
                    </div>
                    <div style='width: 382px; height: 236px; display: flex; align-items: center; justify-content: center;'>
                        {"<img src='" + article['image'] + "' style='height: 100%; width: auto; border-radius: 12px; object-fit: cover;'/>" if article.get("image") else ""}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("You haven’t saved any articles yet. Use the ☆ icon to save articles.")
