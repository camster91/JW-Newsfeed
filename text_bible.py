"""
Daily Text Scraper

Scrapes the daily text from wol.jw.org (Watchtower Online Library).
"""

import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False


def get_daily_text():
    """Scrape the daily text from wol.jw.org."""
    driver = None
    text_list = []

    try:
        # Initialize Chrome driver
        if USE_WEBDRIVER_MANAGER:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        else:
            driver = webdriver.Chrome()

        driver.get('https://wol.jw.org')

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        for link in soup.find_all("div", {"class": "tabContent active"}):
            try:
                header = link.h2.text.strip() if link.h2 else ""
                scripture = link.p.text.strip() if link.p else ""

                # Get notes (next sibling paragraph)
                notes = ""
                if link.p and link.p.next_sibling:
                    next_elem = link.p.next_sibling.next_sibling
                    if next_elem and hasattr(next_elem, 'text'):
                        notes = next_elem.text.strip()

                text_dict = {
                    'Date': header,
                    'Script': scripture,
                    'Notes': notes
                }
                text_list.append(text_dict)
            except AttributeError:
                # Skip items that don't have expected structure
                continue

    except WebDriverException as e:
        print(f"Error initializing browser: {e}")
        return []
    finally:
        if driver:
            driver.quit()

    return text_list


if __name__ == '__main__':
    texts = get_daily_text()
    if texts:
        print(json.dumps(texts, indent=2))
    else:
        print("No daily text found.")
