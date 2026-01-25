import os
import re
import requests
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
    SessionNotCreatedException
)

# Configuration - use environment variables or defaults
DATA_DIR = os.environ.get('JW_DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
URLS_FILE = os.environ.get('JW_URLS_FILE', os.path.join(DATA_DIR, 'urls_and_titles.txt'))
TARGET_DIRECTORY = os.environ.get('JW_DOWNLOAD_DIR', os.path.join(os.path.expanduser('~'), 'JW.ORG'))
MAX_RETRIES = 3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper function to sanitize folder names
def sanitize_folder_name(name):
    return re.sub(r'[\/:*?"<>|]', '_', name)

# Helper function to get a unique identifier for a URL
def get_unique_identifier_for_url(url):
    return sanitize_folder_name(url.split("/")[-1] or url.split("/")[-2])

def setup_driver(url, max_retries=3):
    driver = None
    retries = 0
    while retries < max_retries:
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get(url)
            try:
                cookie_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "lnc-acceptCookiesButton"))
                )
                cookie_button.click()
            except Exception as e:
                logging.error("Error clicking the cookie bar button: %s", e)
            return driver  # Return the driver if successful
        except SessionNotCreatedException as e:
            retries += 1
            logging.warning("Chrome session not created. Retrying... (%d/%d)", retries, max_retries)
            time.sleep(2)  # Wait before retrying
            if driver:
                driver.quit()  # Close the driver if partially opened
        except Exception as e:
            logging.error("An unexpected error occurred while setting up the driver: %s", e)
            if driver:
                driver.quit()
            break  # Break the loop on unexpected errors

    logging.error("Failed to create a Chrome session after %d attempts. Exiting...", max_retries)
    return None  # Return None if all retries fail

def scrape_video_titles(driver, url):
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return [link.text.strip() for link in soup.find_all("div", {"class": "syn-body lss"})]

def get_page_title(driver):
    try:
        h1_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        return h1_element.text.strip()
    except Exception as e:
        logging.error("Error getting page title: %s", e)
        return "UnknownTitle"

def process_video(driver, title, target_folder, session, max_retries):
    try:
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, title)))
    except (NoSuchElementException, TimeoutException):
        logging.warning("Element with title '%s' not found on the page. Skipping...", title)
        return  # Skip to the next URL after logging the warning

    driver.execute_script("arguments[0].scrollIntoView();", element)
    click_element_with_retry(driver, element, title, max_retries)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    file = soup.find('a', {'class': 'secondaryButton'})
    if file is None:
        logging.warning("Video file link not found for '%s'. Skipping...", title)
        return  # Skip to the next URL after logging the warning

    file_link = file["href"]
    file_name = file_link.split("/")[-1]
    
    complete_file_path = os.path.join(target_folder, file_name)
    if not os.path.isfile(complete_file_path):
        download_file_with_retry(session, file_link, complete_file_path, file_name, max_retries)
    else:
        logging.info("%s already exists. Skipping download...", file_name)

def click_element_with_retry(driver, element, title, max_retries):
    success = False
    retries = 0
    while not success and retries < max_retries:
        try:
            element.click()
            success = True
        except ElementClickInterceptedException:
            retries += 1
            logging.warning("Click intercepted for title '%s'. Retrying (%d/%d)...", title, retries, max_retries)
            driver.execute_script("window.scrollBy(0, 100);")  # Scroll to try again
            time.sleep(2)

    if not success:
        logging.error("Max retries reached for video '%s'. Skipping this video.", title)

def download_file_with_retry(session, file_link, complete_file_path, file_name, max_retries):
    success = False
    retries = 0
    while not success and retries < max_retries:
        try:
            r = session.get(file_link, allow_redirects=True)
            r.raise_for_status()
            with open(complete_file_path, 'wb') as f:
                f.write(r.content)
            logging.info("Successfully downloaded %s", file_name)
            success = True
        except requests.exceptions.RequestException:
            retries += 1
            if retries < max_retries:
                logging.warning("Download failed for %s. Retrying (%d/%d)...", file_name, retries, max_retries)
            else:
                logging.error("Download failed for %s. Skipping after %d retries.", file_name, max_retries)

def main():
    session = requests.Session()

    with open(URLS_FILE, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    if not urls:
        logging.error("No URLs found in the file. Exiting...")
        return

    for url in urls:
        driver = setup_driver(url)
        if not driver:
            logging.error("Skipping URL due to failure to initialize Chrome session: %s", url)
            continue

        video_titles = scrape_video_titles(driver, url)
        if not video_titles:
            logging.warning("No video titles found at URL: %s", url)
            driver.quit()
            continue

        page_title = sanitize_folder_name(url.split('/')[-1])
        target_folder = os.path.join(TARGET_DIRECTORY, page_title)
        os.makedirs(target_folder, exist_ok=True)

        for title in video_titles:
            complete_file_path = os.path.join(target_folder, title + ".mp4")  # Assuming .mp4 extension
            if os.path.exists(complete_file_path):
                logging.info("%s already exists. Skipping this video...", title)
                continue  # Skip to the next video

            process_video(driver, title, target_folder, session, MAX_RETRIES)

        driver.quit()  # Ensure the driver quits after processing videos for each URL

    logging.info("Done!")

if __name__ == "__main__":
    main()
