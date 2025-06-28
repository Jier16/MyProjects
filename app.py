# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Initialize session state for saved articles and view mode
if "saved_articles" not in st.session_state:
    st.session_state.saved_articles = []
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"

# Helper functions for each website
def scrape_cspi():
    URL = "https://www.cspi.org/page/media"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    page = requests.get(URL, headers=headers)
    articles_data = []

    if page.status_code != 403:
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('div', class_='teaser-inner')
        two_weeks_ago = datetime.now() - timedelta(weeks=2)

        for a in articles:
            title_element = a.find("a")
            date_element = a.find("time")
            link_element = a.find("a", class_="js-link-event-link")
            label_element = a.find("span", class_ = "source")

            if date_element:
                try:
                    article_date = datetime.strptime(date_element.text.strip(), "%B %d, %Y")
                except:
                    continue
                if article_date >= two_weeks_ago:
                    articles_data.append({
                        "title": title_element.text.strip() if title_element else "Title not found",
                        "topic": label_element.text.strip() if label_element else "Label not found",
                        "date": date_element.text.strip(),
                        "date_obj": article_date,
                        "link": link_element['href'] if link_element else "Link not found",
                        "source": "Center for Science in the Public Interest"
                    })
    return articles_data

def scrape_mighty_earth():
    URL = "https://mightyearth.org/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    page = requests.get(URL, headers=headers)
    articles_data = []

    if page.status_code != 403:
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('div', class_='card card-article uk-transition-toggle reveal')
        two_weeks_ago = datetime.now() - timedelta(weeks=2)

        for a in articles:
            title_element = a.find("h5")
            topic_element = a.find("label")
            date_element = a.find("span", class_="date")
            link_element = a.find("a", class_="card-link")

            if date_element:
                try:
                    article_date = datetime.strptime(date_element.text.strip(), "%d/%b/%Y")
                except:
                    continue
                if article_date >= two_weeks_ago:
                    formatted_date = article_date.strftime("%b %d, %Y")
                    articles_data.append({
                        "title": title_element.text.strip() if title_element else "Title not found",
                        "topic": topic_element.text.strip() if topic_element else "Topic not found",
                        "date": formatted_date,
                        "date_obj": article_date,
                        "link": link_element['href'] if link_element else "Link not found",
                        "source": "Mighty Earth"
                    })
    return articles_data

# Streamlit UI
st.set_page_config(page_title="Environmental News Aggregator", layout="wide")
st.markdown("<h1 style='font-size: 36px;'>📅 Latest Articles from Selected Websites</h1>", unsafe_allow_html=True)

# Top-right folder icon with badge
with st.container():
    cols = st.columns([0.9, 0.1])
    with cols[1]:
        if st.button("📁 Saved ({})".format(len(st.session_state.saved_articles))):
            st.session_state.view_mode = "saved"

if st.session_state.view_mode == "main":
    st.markdown("<p style='font-size: 18px;'>Select the sources you want to search:</p>", unsafe_allow_html=True)
    show_cspi = st.checkbox("Center for Science in the Public Interest")
    show_mighty = st.checkbox("Mighty Earth")

    if st.button("Search"):
        all_articles = []
        if show_cspi:
            all_articles += scrape_cspi()
        if show_mighty:
            all_articles += scrape_mighty_earth()

        all_articles.sort(key=lambda x: x['date_obj'], reverse=True)

        if all_articles:
            for idx, article in enumerate(all_articles):
                is_saved = article in st.session_state.saved_articles
                with st.container():
                    col1, col2 = st.columns([0.95, 0.05])
                    with col1:
                        st.markdown(f"""
                            <div style='background-color:#f9f9f9;padding:20px;border-radius:10px;margin-bottom:20px;box-shadow:0 4px 8px rgba(0, 0, 0, 0.05);'>
                                <h3 style='font-size:22px;margin-bottom:10px;'>
                                    <a href='{article['link']}' target='_blank' style='text-decoration:none;color:#1a73e8;'>{article['title']}</a>
                                </h3>
                                <p style='font-size:16px;margin:0;'><strong>Topic:</strong> {article['topic']}</p>
                                <p style='font-size:16px;margin:0;'><strong>Date:</strong> {article['date']}</p>
                                <p style='font-size:16px;margin:0;'><strong>Source:</strong> {article['source']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        key = f"star_{idx}"
                        icon = "★" if is_saved else "☆"
                        if st.button(icon, key=key):
                            if is_saved:
                                st.session_state.saved_articles.remove(article)
                            else:
                                st.session_state.saved_articles.append(article)
        else:
            st.info("No articles found in the past two weeks from the selected sources.")

elif st.session_state.view_mode == "saved":
    st.markdown("<h2>📁 Saved Articles</h2>", unsafe_allow_html=True)
    if st.button("⬅️ Back to All Articles"):
        st.session_state.view_mode = "main"

    if st.session_state.saved_articles:
        for idx, article in enumerate(st.session_state.saved_articles):
            with st.container():
                st.markdown(f"""
                    <div style='background-color:#f0fff0;padding:20px;border-radius:10px;margin-bottom:20px;box-shadow:0 4px 8px rgba(0, 0, 0, 0.05);'>
                        <h3 style='font-size:22px;margin-bottom:10px;'>
                            <a href='{article['link']}' target='_blank' style='text-decoration:none;color:#1a73e8;'>{article['title']}</a>
                        </h3>
                        <p style='font-size:16px;margin:0;'><strong>Topic:</strong> {article['topic']}</p>
                        <p style='font-size:16px;margin:0;'><strong>Date:</strong> {article['date']}</p>
                        <p style='font-size:16px;margin:0;'><strong>Source:</strong> {article['source']}</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("You haven’t saved any articles yet. ⭐ them from the main view!")
