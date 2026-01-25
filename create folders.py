import os
import re

# Constants
URLS_FILE = "C:\\Python JW News\\urls_and_titles.txt"
TARGET_DIRECTORY = "D:\\JW.ORG"

# Helper function to sanitize folder names
def sanitize_folder_name(name):
    return re.sub(r'[\/:*?"<>|]', '_', name)

def create_folders_from_urls(urls_file, target_directory):
    with open(urls_file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    if not urls:
        print("No URLs found in the file. Exiting...")
        return

    for url in urls:
        folder_name = sanitize_folder_name(url.split('/')[-1] or url.split('/')[-2])
        target_folder = os.path.join(target_directory, folder_name)
        os.makedirs(target_folder, exist_ok=True)
        print(f"Created folder: {target_folder}")

if __name__ == "__main__":
    create_folders_from_urls(URLS_FILE, TARGET_DIRECTORY)
