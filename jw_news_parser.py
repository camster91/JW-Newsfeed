"""
JW.ORG RSS Feed Generator

Scrapes JW.ORG "What's New" page for the latest content using Selenium,
then generates an RSS 2.0 feed that can be consumed by feed readers.

All content is scraped directly from the What's New page in release order.
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

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False


def send_notification(title, message, error=False):
    """Send a Windows toast notification."""
    if not TOAST_AVAILABLE:
        return
    try:
        toaster = ToastNotifier()
        toaster.show_toast(
            title,
            message,
            duration=10,
            threaded=True
        )
    except Exception:
        pass


# Configuration
DATA_DIR = os.environ.get('JW_DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.environ.get('JW_OUTPUT_DIR', os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'jw_feed.xml')
FEED_URL = os.environ.get('JW_FEED_URL', 'https://camster91.github.io/JW-Newsfeed/jw_feed.xml')


def load_history():
    """Load previously processed items from history file."""
    try:
        with open(HISTORY_FILE) as f:
            data = json.load(f)
            if isinstance(data, list):
                return set(data)
            elif isinstance(data, dict):
                return set(data.keys())
            return set()
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_history(history):
    """Save processed items to history file."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(history), f, ensure_ascii=False, indent=4)


def parse_date(date_str):
    """Parse date string like '2026-01-30' to RFC 822 format."""
    try:
        dt = datetime.datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return dt.strftime('%a, %d %b %Y 12:00:00 +0000')
    except ValueError:
        return datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S +0000')


def scrape_whats_new(driver, history):
    """Scrape the What's New page from JW.ORG. Returns items in release order."""
    items_list = []
    new_count = 0

    driver.get('https://www.jw.org/en/whats-new/')
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
            if not href:
                continue
            if not href.startswith('http'):
                href = 'https://www.jw.org' + href

            # Skip duplicates within this scrape
            if href in [item['link'] for item in items_list]:
                continue

            # Get title
            title_elem = article.find('h3')
            if not title_elem:
                title_elem = article.find('h2')
            title = title_elem.text.strip() if title_elem else ''
            if not title:
                continue

            # Get image
            img_elem = article.find('img')
            image = ''
            if img_elem:
                image = img_elem.get('src', '') or img_elem.get('data-src', '')

            # Get date from contextTtl
            date_elem = article.find('p', class_='contextTtl')
            date_str = date_elem.text.strip() if date_elem else ''
            pub_date = parse_date(date_str) if date_str else None

            # Detect if it's a video (has hasDuration class)
            classes = article.get('class', [])
            is_video = 'hasDuration' in classes
            category = 'Video' if is_video else 'Article'

            # Generate description
            if is_video:
                # Get duration if available
                duration_elem = article.find('span', class_='syn-img-overlay-text')
                duration = duration_elem.text.strip() if duration_elem else ''
                description = f"Video{' (' + duration + ')' if duration else ''}: {title}"
            else:
                description = title

            is_new = href not in history
            if is_new:
                history.add(href)
                new_count += 1

            items_list.append({
                'title': title,
                'link': href,
                'image': image,
                'category': category,
                'description': description,
                'pub_date': pub_date,
                'is_new': is_new
            })
        except (KeyError, AttributeError):
            continue

    return items_list, new_count


def generate_rss_feed(items):
    """Generate RSS 2.0 feed from scraped content."""
    rss = ET.Element('rss', version='2.0')
    rss.set('xmlns:media', 'http://search.yahoo.com/mrss/')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

    channel = ET.SubElement(rss, 'channel')

    ET.SubElement(channel, 'title').text = "JW.ORG What's New"
    ET.SubElement(channel, 'link').text = 'https://www.jw.org/en/whats-new/'
    ET.SubElement(channel, 'description').text = 'Latest updates from JW.ORG'
    ET.SubElement(channel, 'language').text = 'en'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S +0000')

    atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
    atom_link.set('href', FEED_URL)
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    for item_data in items:
        item = ET.SubElement(channel, 'item')

        ET.SubElement(item, 'title').text = item_data.get('title', '')
        ET.SubElement(item, 'link').text = item_data.get('link', '')
        ET.SubElement(item, 'guid', isPermaLink='true').text = item_data.get('link', '')
        ET.SubElement(item, 'category').text = item_data.get('category', 'Update')
        ET.SubElement(item, 'description').text = item_data.get('description', '')

        pub_date = item_data.get('pub_date') or datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S +0000')
        ET.SubElement(item, 'pubDate').text = pub_date

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

    history = load_history()
    print(f"Loaded {len(history)} previously processed items")

    driver = None
    try:
        if USE_WEBDRIVER_MANAGER:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        else:
            driver = webdriver.Chrome()
        driver.minimize_window()
    except WebDriverException as e:
        print(f"Error initializing browser: {e}")
        send_notification("JW-Newsfeed Error", f"Browser error: {str(e)[:100]}", error=True)
        return

    try:
        print("Scraping What's New page...")
        items, new_count = scrape_whats_new(driver, history)
        print(f"Found {len(items)} items ({new_count} new)")

    except Exception as e:
        print(f"ERROR: Scraping failed: {e}")
        send_notification("JW-Newsfeed Error", f"Scraping failed: {str(e)[:100]}", error=True)
        if driver:
            driver.quit()
        return

    finally:
        if driver:
            driver.quit()

    if not items:
        print("ERROR: No items found! Feed not updated.")
        send_notification("JW-Newsfeed Error", "No items found! Feed not updated.", error=True)
        return

    save_history(history)

    print("Generating RSS feed...")
    rss = generate_rss_feed(items)

    xml_content = prettify_xml(rss)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"RSS feed saved to: {OUTPUT_FILE}")
    print(f"Total items in feed: {len(items)}")
    print(f"New items: {new_count}")


if __name__ == '__main__':
    main()
