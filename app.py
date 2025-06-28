# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import io
from fpdf import FPDF

# Initialize session state for saved articles, view mode, and search results
if "saved_articles" not in st.session_state:
    st.session_state.saved_articles = []
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"
if "all_articles" not in st.session_state:
    st.session_state.all_articles = []

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

def scrape_cfs():
    URL = "https://www.centerforfoodsafety.org/press-releases"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    page = requests.get(URL, headers=headers)
    articles_data = []

    if page.status_code != 403:
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('div', class_='no_a_color padB2')
        two_weeks_ago = datetime.now() - timedelta(weeks=2)

        for a in articles:
            title_element = a.find(class_ = "padB1 txt_17 normal txt_red")
            date_element = a.find(class_="txt_12 iblock padB0")
            link_element = a.find("a")

            if date_element:
                try:
                    clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_element.text)
                    article_date = datetime.strptime(clean_date, "%B %d, %Y")
                except:
                    continue
                if article_date >= two_weeks_ago:
                    formatted_date = article_date.strftime("%b %d, %Y")
                    articles_data.append({
                        "title": title_element.text.strip() if title_element else "Title not found",
                        "topic": "Topic not found",
                        "date": formatted_date,
                        "date_obj": article_date,
                        "link": "https://www.centerforfoodsafety.org" + link_element['href'] if link_element else "Link not found",
                        "source": "Center for Food Safety"
                    })
    return articles_data

def generate_pdf(articles):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Saved Articles Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)
    for art in articles:
        pdf.multi_cell(0, 10, txt=f"Title: {art['title']}\nDate: {art['date']}\nTopic: {art['topic']}\nSource: {art['source']}\nLink: {art['link']}\n", border=1)
        pdf.ln(2)
    buffer = io.BytesIO()
    pdf.output(buffer, dest='F')  # Change here: use 'F' to write to a file-like object
    buffer.seek(0)
    return buffer

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
    show_cfs = st.checkbox("Center for Food Safety")

    if st.button("Search"):
        st.session_state.all_articles = []
        if show_cspi:
            st.session_state.all_articles += scrape_cspi()
        if show_mighty:
            st.session_state.all_articles += scrape_mighty_earth()
        if show_cfs:
            st.session_state.all_articles += scrape_cfs()
        st.session_state.all_articles.sort(key=lambda x: x['date_obj'], reverse=True)

    if st.session_state.all_articles:
        for idx, article in enumerate(st.session_state.all_articles):
            is_saved = any(saved['link'] == article['link'] for saved in st.session_state.saved_articles)
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
                            st.session_state.saved_articles = [a for a in st.session_state.saved_articles if a['link'] != article['link']]
                        else:
                            st.session_state.saved_articles.append(article)
    else:
        st.info("Click 'Search' to load articles from the selected sources.")

elif st.session_state.view_mode == "saved":
    st.markdown("<h2>📁 Saved Articles</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        if st.button("⬅️ Back to All Articles"):
            st.session_state.view_mode = "main"
    with col2:
        if st.session_state.saved_articles:
            if st.button("🖨️ Print as Report"):
                pdf_file = generate_pdf(st.session_state.saved_articles)
                st.download_button(label="📄 Download PDF", data=pdf_file, file_name="saved_articles_report.pdf")

    if st.session_state.saved_articles:
        for article in st.session_state.saved_articles:
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
