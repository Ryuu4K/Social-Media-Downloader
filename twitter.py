import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_service = Service('./chromedriver.exe')

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def download_media(url, folder='media'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    response = requests.get(url)
    if response.status_code == 200:
        file_name = os.path.join(folder, url.split('/')[-1])
        with open(file_name, 'wb') as file:
            file.write(response.content)

def get_media_links(account):
    base_url = f"https://x.com/{account}"
    driver.get(base_url)
    media_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        images = driver.find_elements(By.XPATH, '//img[contains(@src, "twimg.com/media/")]')
        videos = driver.find_elements(By.XPATH, '//video')

        for img in images:
            media_links.add(img.get_attribute('src'))
        for video in videos:
            video_src = video.get_attribute('src')
            if video_src:
                media_links.add(video_src)

        scroll_to_bottom(driver)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return media_links

if __name__ == "__main__":
    account = "WRITE ACCOUNT TWITTER HERE (WITHOUT @) "
    media_links = get_media_links(account)
    print(f"Found {len(media_links)} media files. Downloading...")

    for link in media_links:
        download_media(link)

    driver.quit()
    print("Download complete.")
