import time
from collections import OrderedDict
import re
import random
import spintax
import concurrent.futures

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


# Define the number of threads to use
NUM_THREADS = 5


# Define a function to scrape videos for a single channel
def scrape_videos_for_channel(channel, commented_video_ids):
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


# Scrape videos for each channel using multiple threads
while True:
    channels = load_channels()
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for channel in channels:
            future = executor.submit(scrape_videos_for_channel, channel, commented_video_ids)
            futures.append(future)
        # Wait for all the threads to finish
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
    # Check if any new videos were found for any of the channels
    new_videos_found = False
    for channel in channels:
        # Try both URL variants
        new_video_id = None
        urls = [f'https://www.youtube.com/{channel}/videos', f'https://www.youtube.com/channel/{channel}/videos']
        for url in urls:
            new_video_id = scrape_videos(url, commented_video_ids)
            if new_video_id is not None:
                new_videos_found = True
                break
        if new_videos_found:
            break
    if not new_videos_found:
        # Pause before checking again
        time.sleep(30)
