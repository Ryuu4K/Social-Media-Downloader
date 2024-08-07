import os
import time
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Function to download image from a URL and check resolution
def download_image(url, folder_path, image_name, min_width, min_height):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            if image.width >= min_width and image.height >= min_height:
                with open(os.path.join(folder_path, image_name), 'wb') as file:
                    file.write(response.content)
                return True
            else:
                print(f"Image {url} does not meet resolution requirements.")
                return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless Chrome
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")

# Setup WebDriver
webdriver_service = Service('./chromedriver.exe')  # Update with your WebDriver path
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# List of search keywords
search_keys = "WRITE SEARCH KEY HERE" #["", ""]

# Create a folder to save images
folder_path = "WRITE FOLDER PATH HERE"
os.makedirs(folder_path, exist_ok=True)

# Maximum number of images to download per keyword
max_images_per_keyword = 50

# Minimum resolution requirements
min_width = 800
min_height = 600

# Function to download images for a given search key
def download_images_for_search_key(search_key):
    url = f"https://www.instagram.com/explore/tags/{search_key.replace(' ', '')}/"
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load

    # Scroll down to load more images
    image_urls = set()
    scroll_count = 0
    while len(image_urls) < max_images_per_keyword and scroll_count < 10:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)
        scroll_count += 1
        
        # Parse page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find image elements and extract URLs
        image_elements = soup.find_all('img', {'src': True})
        for img in image_elements:
            if len(image_urls) >= max_images_per_keyword:
                break
            image_urls.add(img['src'])
        print(f"Found {len(image_urls)} images so far for search key '{search_key}'.")

    # Download images
    downloaded_images = set()
    for idx, image_url in enumerate(image_urls):
        if idx >= max_images_per_keyword:
            break
        if image_url not in downloaded_images:
            image_name = f"{search_key.replace(' ', '_')}_{idx + 1}.jpg"
            if download_image(image_url, folder_path, image_name, min_width, min_height):
                downloaded_images.add(image_url)

    print(f"Downloaded {len(downloaded_images)} images for search key '{search_key}'.")

# Download images for each search key
for search_key in search_keys:
    download_images_for_search_key(search_key)

# Close the WebDriver
driver.quit()
