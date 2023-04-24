import time
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Load channels from a text file
with open('channels.txt', 'r') as f:
    channels = [line.strip() for line in f.readlines()]

# Set up virtual driver
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

# Scrape videos for each channel
for channel in channels:
    url = f'https://www.youtube.com/channel/{channel}/videos'
    driver.get(url)

    # Scroll down to load more videos
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        print(new_height)
        if new_height == last_height:
            break
        last_height = new_height

    # Get HTML source and parse with BeautifulSoup
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    video_ids = []

    pattern = re.compile(r'href="/watch\?v=([^"]+)')
    matches = pattern.findall(str(soup))

    # Преобразуем результаты в список уникальных значений
    unique_video_ids = list(set([id.strip('"') for match in matches for id in match.split(',')]))

    # Выводим результаты
    print(unique_video_ids)
    print(len(unique_video_ids))

# Close the virtual driver
driver.quit()
