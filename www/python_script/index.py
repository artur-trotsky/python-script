import time
from collections import OrderedDict
import re
import random
import spintax

from bs4 import BeautifulSoup
from selenium import webdriver


def scrape_videos(youtube_url, commented_video_ids):
    # Set up virtual driver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.get(youtube_url)

    # Scroll down to load more videos
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        # Get HTML source and parse with BeautifulSoup
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        pattern = re.compile(r'href="/watch\?v=([^"]+)')
        matches = pattern.findall(str(soup))

        # Преобразуем результаты в список уникальных значений и сохраняем порядок элементов
        unique_video_ids = list(OrderedDict.fromkeys([id.strip('"') for match in matches for id in match.split(',')]))

        # Получить первый уникальный идентификатор видео
        new_video_id = next((vid for vid in unique_video_ids if vid not in commented_video_ids), None)
        if new_video_id is not None:
            break
        if new_height == last_height:
            break
        last_height = new_height

    # Close the virtual driver
    driver.quit()

    return new_video_id


def get_comment_message(s):
    """
    Replaces spintax syntax ({text1|text2|text3}) in a string with a random choice of the provided texts.
    """
    def repl(match):
        options = match.group(1).split('|')
        return random.choice(options)

    pattern = re.compile(r'\{([^}]+)\}')
    return pattern.sub(repl, s)


commented_video_ids = []


def load_channels():
    with open('youtube_channels.txt', 'r') as f:
        channel_line = [line.strip() for line in f.readlines()]
    return channel_line


# Scrape videos for each channel
while True:
    channels = load_channels()
    for i, channel in enumerate(channels):
        # Try both URL variants
        new_video_id = None
        urls = [f'https://www.youtube.com/{channel}/videos', f'https://www.youtube.com/channel/{channel}/videos']
        for url in urls:
            new_video_id = scrape_videos(url, commented_video_ids)
            # Если найден новый уникальный идентификатор, то оставляем комментарий и добавляем его в список commented_video_ids
            if new_video_id is not None:
                COMMENT_TEXT = get_comment_message("{Hey|Hello|Hi}, {great video!|nice content!|awesome work!}")
                # comment_on_video(new_video_id, COMMENT_TEXT)
                commented_video_ids.append(new_video_id)
                # Break out of the inner for loop so that we don't try the other URL variant
                print(channel)
                print(new_video_id)
                break
        if new_video_id is None:
            time.sleep(30)
        # If this is the last channel in the list, update the list of channels
        if i == len(channels) - 1:
            break
