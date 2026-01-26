"""
JW.ORG RSS Feed Generator

Scrapes JW.ORG for latest videos, books, and news articles using Selenium,
then generates an RSS 2.0 feed that can be consumed by feed readers.

All content is scraped directly from web pages - no external RSS feeds are used.
"""

import os
import json
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from selenium import webdriver

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

# Configuration - use environment variables or defaults
DATA_DIR = os.environ.get('JW_DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.environ.get('JW_OUTPUT_DIR', os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'jw_feed.xml')
FEED_URL = os.environ.get('JW_FEED_URL', 'https://example.com/jw_feed.xml')


def load_history():
    """Load previously processed items from history file."""
    try:
        with open(HISTORY_FILE) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_history(history):
    """Save processed items to history file."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(history), f, ensure_ascii=False, indent=4)


def scrape_videos(driver, history):
    """Scrape latest videos from JW.ORG. Returns all videos and count of new ones."""
    videos_list = []
    new_count = 0

    driver.get('https://www.jw.org/en/library/videos/#en/categories/LatestVideos')
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "contentArea"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    for link in soup.find_all("div", {"class": "synopsis lss desc showImgOverlay hasDuration jsLanguageAttributes dir-ltr lang-en ml-E ms-ROMAN"}):
        try:
            href = link.a['href']
            if not href.startswith('http'):
                href = 'https://www.jw.org' + href

            text = link.find_all('a', {'class': 'jsNoScroll'})[1].text
            image = link.img['src']

            is_new = href not in history
            if is_new:
                history.add(href)
                new_count += 1

            videos_list.append({
                'title': text,
                'link': href,
                'image': image,
                'category': 'video',
                'is_new': is_new
            })
        except (KeyError, IndexError, AttributeError):
            continue

    return videos_list, new_count


def scrape_books(driver, history):
    """Scrape latest books from JW.ORG. Returns all books and count of new ones."""
    book_list = []
    pics_list = []
    new_count = 0

    driver.get('https://www.jw.org/en/library/books')
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "pubsViewResults"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Get book cover images first
    for pic in soup.find_all("div", {"class": "cvr-wrapper"}):
        try:
            pics_list.append(pic.img['src'])
        except (KeyError, AttributeError):
            continue

    for idx, link in enumerate(soup.find_all("div", {"class": "publicationDesc"})):
        try:
            href = "https://www.jw.org" + link.a['href']
            title = link.text.strip()

            is_new = href not in history
            if is_new:
                history.add(href)
                new_count += 1

            book_list.append({
                'title': title,
                'link': href,
                'image': pics_list[idx] if idx < len(pics_list) else '',
                'category': 'book',
                'is_new': is_new
            })
        except (KeyError, AttributeError):
            continue

    return book_list, new_count


def scrape_news(driver, history):
    """Scrape latest news from JW.ORG news page. Returns all news and count of new ones."""
    news_list = []
    new_count = 0

    driver.get('https://www.jw.org/en/news/')
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "synopsis"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    for article in soup.find_all("div", {"class": "synopsis"}):
        try:
            link_elem = article.find('a')
            if not link_elem:
                continue

            href = link_elem.get('href', '')
            if not href.startswith('http'):
                href = 'https://www.jw.org' + href

            title_elem = article.find(['h3', 'h2', 'span'])
            title = title_elem.text.strip() if title_elem else ''

            img_elem = article.find('img')
            image = img_elem.get('src', '') if img_elem else ''

            desc_elem = article.find('p')
            description = desc_elem.text.strip() if desc_elem else ''

            is_new = href not in history
            if is_new:
                history.add(href)
                new_count += 1

            news_list.append({
                'title': title,
                'link': href,
                'image': image,
                'category': 'news',
                'description': description,
                'pub_date': '',
                'is_new': is_new
            })
        except (KeyError, AttributeError):
            continue

    return news_list, new_count


def generate_rss_feed(videos, books, news):
    """Generate RSS 2.0 feed from scraped content."""

    # Create root RSS element
    rss = ET.Element('rss', version='2.0')
    rss.set('xmlns:media', 'http://search.yahoo.com/mrss/')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

    channel = ET.SubElement(rss, 'channel')

    # Channel metadata
    ET.SubElement(channel, 'title').text = 'JW.ORG Updates'
    ET.SubElement(channel, 'link').text = 'https://www.jw.org'
    ET.SubElement(channel, 'description').text = 'Latest videos, books, and news from JW.ORG'
    ET.SubElement(channel, 'language').text = 'en'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S +0000')

    # Add atom:link for feed URL (self-reference)
    atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
    atom_link.set('href', FEED_URL)
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    # Add all items
    all_items = []

    for video in videos:
        all_items.append(('video', video))

    for book in books:
        all_items.append(('book', book))

    for article in news:
        all_items.append(('news', article))

    for item_type, item_data in all_items:
        item = ET.SubElement(channel, 'item')

        ET.SubElement(item, 'title').text = item_data.get('title', '')
        ET.SubElement(item, 'link').text = item_data.get('link', '')
        ET.SubElement(item, 'guid', isPermaLink='true').text = item_data.get('link', '')
        ET.SubElement(item, 'category').text = item_type.capitalize()

        # Add description
        description = item_data.get('description', '')
        if not description:
            description = f"New {item_type}: {item_data.get('title', '')}"
        ET.SubElement(item, 'description').text = description

        # Add publication date
        pub_date = item_data.get('pub_date', '')
        if not pub_date:
            pub_date = datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S +0000')
        ET.SubElement(item, 'pubDate').text = pub_date

        # Add media thumbnail if image exists
        if item_data.get('image'):
            media_thumb = ET.SubElement(item, '{http://search.yahoo.com/mrss/}thumbnail')
            media_thumb.set('url', item_data['image'])

    return rss


def prettify_xml(elem):
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')


def main():
    """Main function to scrape JW.ORG and generate RSS feed."""
    print("Starting JW.ORG RSS Feed Generator...")

    # Load history
    history = load_history()
    print(f"Loaded {len(history)} previously processed items")

    # Initialize browser
    driver = None
    try:
        if USE_WEBDRIVER_MANAGER:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        else:
            driver = webdriver.Chrome()
        driver.minimize_window()
    except WebDriverException as e:
        print(f"Error initializing browser: {e}")
        print("Make sure Chrome and ChromeDriver are installed.")
        return

    try:
        # Scrape content
        print("Scraping latest videos...")
        videos, new_videos = scrape_videos(driver, history)
        print(f"Found {len(videos)} videos ({new_videos} new)")

        print("Scraping latest books...")
        books, new_books = scrape_books(driver, history)
        print(f"Found {len(books)} books ({new_books} new)")

        print("Scraping latest news...")
        news, new_news = scrape_news(driver, history)
        print(f"Found {len(news)} articles ({new_news} new)")

    finally:
        if driver:
            driver.quit()

    # Save updated history
    save_history(history)

    # Generate RSS feed with ALL items (not just new ones)
    print("Generating RSS feed...")
    rss = generate_rss_feed(videos, books, news)

    # Write to file
    xml_content = prettify_xml(rss)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"RSS feed saved to: {OUTPUT_FILE}")
    print(f"Total items in feed: {len(videos) + len(books) + len(news)}")
    print(f"New items: {new_videos + new_books + new_news}")


if __name__ == '__main__':
    main()
