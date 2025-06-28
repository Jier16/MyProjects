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
def scrape_cspi():
    URL = "https://www.cspi.org/page/media"
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(URL, headers=headers)
    articles_data = []

    if page.status_code != 403:
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('div', class_='teaser-inner')

        for a in articles:
            title_element = a.find("a")
            date_element = a.find("time")
            link_element = a.find("a", class_="js-link-event-link")
            label_element = a.find("span", class_="source")
            img_element = a.find("img")
            image_url = img_element['src'] if img_element else None

            if date_element:
                try:
                    article_date = datetime.strptime(date_element.text.strip(), "%B %d, %Y")
                except:
                    continue
                if article_date >= DATE_RANGE_START:
                    articles_data.append({
                        "title": title_element.text.strip() if title_element else "Title not found",
                        "topic": label_element.text.strip() if label_element else "Label not found",
                        "date": date_element.text.strip(),
                        "date_obj": article_date,
                        "link": link_element['href'] if link_element else "Link not found",
                        "source": "Center for Science in the Public Interest",
                        "image": image_url
                    })
    return articles_data

def scrape_mighty_earth():
    URL = "https://mightyearth.org/news/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(URL, headers=headers)
    articles_data = []

    if page.status_code != 403:
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('div', class_='card card-article uk-transition-toggle reveal')

        for a in articles:
            title_element = a.find("h5")
            topic_element = a.find("label")
            date_element = a.find("span", class_="date")
            link_element = a.find("a", class_="card-link")
            img_element = a.find("img")
            image_url = img_element['src'] if img_element else None

            if date_element:
                try:
                    article_date = datetime.strptime(date_element.text.strip(), "%d/%b/%Y")
                except:
                    continue
                if article_date >= DATE_RANGE_START:
                    formatted_date = article_date.strftime("%b %d, %Y")
                    articles_data.append({
                        "title": title_element.text.strip() if title_element else "Title not found",
                        "topic": topic_element.text.strip() if topic_element else "Topic not found",
                        "date": formatted_date,
                        "date_obj": article_date,
                        "link": link_element['href'] if link_element else "Link not found",
                        "source": "Mighty Earth",
                        "image": image_url
                    })
    return articles_data

def scrape_cfs():
    URL = "https://www.centerforfoodsafety.org/press-releases"
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(URL, headers=headers)
    articles_data = []

    if page.status_code != 403:
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('div', class_='no_a_color padB2')

        for a in articles:
            title_element = a.find(class_="padB1 txt_17 normal txt_red")
            date_element = a.find(class_="txt_12 iblock padB0")
            link_element = a.find("a")
            img_element = a.find("img")
            image_url = "https://www.centerforfoodsafety.org/" + img_element['src'] if img_element else None

            if date_element:
                try:
                    clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_element.text)
                    article_date = datetime.strptime(clean_date, "%B %d, %Y")
                except:
                    continue
                if article_date >= DATE_RANGE_START:
                    formatted_date = article_date.strftime("%b %d, %Y")
                    articles_data.append({
                        "title": title_element.text.strip() if title_element else "Title not found",
                        "topic": "Topic not found",
                        "date": formatted_date,
                        "date_obj": article_date,
                        "link": "https://www.centerforfoodsafety.org" + link_element['href'] if link_element else "Link not found",
                        "source": "Center for Food Safety",
                        "image": image_url
                    })
    return articles_data

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
st.set_page_config(page_title="Environmental News Aggregator", layout="wide")
st.markdown("<h1 style='font-size: 36px;'>🌍 Latest Articles from Selected Websites</h1>", unsafe_allow_html=True)

# Top-right folder icon
with st.container():
    cols = st.columns([0.9, 0.1])
    with cols[1]:
        if st.button("📁 Saved ({})".format(len(st.session_state.saved_articles))):
            st.session_state.view_mode = "saved"

# Main view
if st.session_state.view_mode == "main":
    st.markdown(f"<p style='font-size:16px;'>Showing articles published between <strong>{DATE_RANGE_START.strftime('%b %d, %Y')}</strong> and <strong>{DATE_RANGE_END.strftime('%b %d, %Y')}</strong>.</p>", unsafe_allow_html=True)
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
        for i in range(0, len(st.session_state.all_articles), 3):
            row_articles = st.session_state.all_articles[i:i+3]
            row = st.columns(3)
            for idx, article in enumerate(row_articles):
                article_key = f"article_{i+idx}"
                is_saved = any(saved['link'] == article['link'] for saved in st.session_state.saved_articles)
                icon_key = f"save_{article_key}"
                with row[idx]:
                    if st.button("★" if is_saved else "☆", key=icon_key):
                        if is_saved:
                            st.session_state.saved_articles = [a for a in st.session_state.saved_articles if a['link'] != article['link']]
                        else:
                            st.session_state.saved_articles.append(article)

                    st.markdown("""
                        <div style='background-color:#f9f9f9;padding:0;border-radius:10px;margin-bottom:20px;box-shadow:0 4px 8px rgba(0, 0, 0, 0.05); overflow: hidden;'>
                            {img}
                            <div style='padding: 15px;'>
                                <h4 style='font-size:18px;margin:0 0 10px;'><a href='{link}' target='_blank' style='text-decoration:none;color:#1a73e8;'>{title}</a></h4>
                                <p style='font-size:14px;margin:4px 0;'><strong>Topic:</strong> {topic}</p>
                                <p style='font-size:14px;margin:4px 0;'><strong>Date:</strong> {date}</p>
                                <p style='font-size:14px;margin:4px 0;'><strong>Source:</strong> {source}</p>
                            </div>
                        </div>
                    """.format(
                        img=f"<img src='{article['image']}' style='width:100%;height:200px;object-fit:cover;'>" if article.get("image") else "",
                        title=article['title'],
                        topic=article['topic'],
                        date=article['date'],
                        source=article['source'],
                        link=article['link']
                    ), unsafe_allow_html=True)
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
        for i in range(0, len(st.session_state.saved_articles), 3):
            row_articles = st.session_state.saved_articles[i:i+3]
            row = st.columns(3)
            for idx, article in enumerate(row_articles):
                with row[idx]:
                    st.markdown("""
                        <div style='background-color:#f0fff0;padding:0;border-radius:10px;margin-bottom:20px;box-shadow:0 4px 8px rgba(0, 0, 0, 0.05); overflow: hidden;'>
                            {img}
                            <div style='padding: 15px;'>
                                <h4 style='font-size:18px;margin:0 0 10px;'><a href='{link}' target='_blank' style='text-decoration:none;color:#1a73e8;'>{title}</a></h4>
                                <p style='font-size:14px;margin:4px 0;'><strong>Topic:</strong> {topic}</p>
                                <p style='font-size:14px;margin:4px 0;'><strong>Date:</strong> {date}</p>
                                <p style='font-size:14px;margin:4px 0;'><strong>Source:</strong> {source}</p>
                            </div>
                        </div>
                    """.format(
                        img=f"<img src='{article['image']}' style='width:100%;height:200px;object-fit:cover;'>" if article.get("image") else "",
                        title=article['title'],
                        topic=article['topic'],
                        date=article['date'],
                        source=article['source'],
                        link=article['link']
                    ), unsafe_allow_html=True)
    else:
        st.info("You haven’t saved any articles yet. ⭐ them from the main view!")

