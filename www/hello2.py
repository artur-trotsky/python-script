import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Load channels from a text file
with open('channels.txt', 'r') as f:
    channels = [line.strip() for line in f.readlines()]

# Set up Selenium
options = Options()
options.add_argument('--headless')  # Run Chrome in headless mode
driver = webdriver.Chrome(options=options)

# Scrape videos for each channel
for channel in channels:
    url = f'https://www.youtube.com/channel/{channel}/videos'
    driver.get(url)

    # Scroll to the bottom of the page to trigger automatic loading of more videos
    last_height = driver.execute_script('return document.documentElement.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
        time.sleep(2)  # Wait for new videos to load
        new_height = driver.execute_script('return document.documentElement.scrollHeight')
        print(new_height)
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    video_ids = []
    pattern = re.compile(r'"videoIds":\[(.*?)\]')
    matches = pattern.findall(str(soup))

    # Преобразуем результаты в список уникальных значений
    unique_video_ids = list(set([id.strip('"') for match in matches for id in match.split(',')]))

    # Выводим результаты
    print(unique_video_ids)
    print(len(unique_video_ids))

# Close the browser
driver.quit()