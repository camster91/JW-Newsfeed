"""
Folder Creator for JW.ORG Downloads

Creates folder structure based on URLs in the urls_and_titles.txt file.
"""

import os
import re

# Configuration - use environment variables or defaults
DATA_DIR = os.environ.get('JW_DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
URLS_FILE = os.environ.get('JW_URLS_FILE', os.path.join(DATA_DIR, 'urls_and_titles.txt'))
TARGET_DIRECTORY = os.environ.get('JW_DOWNLOAD_DIR', os.path.join(os.path.expanduser('~'), 'JW.ORG'))


def sanitize_folder_name(name):
    """Remove invalid characters from folder names."""
    return re.sub(r'[\/:*?"<>|]', '_', name)


def create_folders_from_urls(urls_file, target_directory):
    """Create folders for each URL in the file."""
    try:
        with open(urls_file, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: URLs file not found: {urls_file}")
        return

    if not urls:
        print("No URLs found in the file. Exiting...")
        return

    for url in urls:
        folder_name = sanitize_folder_name(url.split('/')[-1] or url.split('/')[-2])
        target_folder = os.path.join(target_directory, folder_name)
        try:
            os.makedirs(target_folder, exist_ok=True)
            print(f"Created folder: {target_folder}")
        except PermissionError:
            print(f"Error: Permission denied creating folder: {target_folder}")
        except OSError as e:
            print(f"Error creating folder {target_folder}: {e}")


if __name__ == "__main__":
    create_folders_from_urls(URLS_FILE, TARGET_DIRECTORY)
