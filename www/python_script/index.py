import time
from collections import OrderedDict
import re
import random
import spintax
import concurrent.futures
import mysql.connector
from database_config import config
import threading
import logging

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


commented_video_ids = set()


# Define a function to load channels from a file or database
def load_channels(source, max_channels=100):
    channels = []
    if source == 'file':
        with open('youtube_channels.txt', 'r') as f:
            channel_lines = [line.strip() for line in f.readlines()]
        channels = channel_lines[:max_channels]
    elif source == 'database':
        # Connect to the database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Load channels from the database
        query = "SELECT channel_url FROM channels LIMIT %s"
        cursor.execute(query, (max_channels,))
        rows = cursor.fetchall()
        for row in rows:
            channels.append(row[0])

        # Close the database connection
        conn.close()
    return channels


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
            commented_video_ids |= set(new_video_id)
            # Break out of the inner for loop so that we don't try the other URL variant
            print(channel)
            print(new_video_id)
            break


# Create a lock for accessing the commented_video_ids set
commented_video_ids_lock = threading.Lock()

# Create a logger for logging exceptions in the threads
logger = logging.getLogger(__name__)


def scrape_videos_for_channel_with_lock(channel_url, commented_video_ids):
    """
    Scrape videos for a single channel, using a lock to ensure
    safe access to the commented_video_ids set.
    """
    try:
        # Scrape the videos for the channel
        new_video_ids = scrape_videos_for_channel(channel_url, commented_video_ids)
        # Add any new video IDs to the set, using the lock to ensure safe access
        with commented_video_ids_lock:
            if new_video_ids is not None:
                commented_video_ids.update(new_video_ids)
    except Exception as e:
        # Log any exceptions that occur
        logger.exception(f"Error scraping videos for channel {channel_url}: {e}")


# Scrape videos for each channel using multiple threads
while True:
    channels = load_channels('database', 100)
    if not channels:
        print("No channels found. Waiting for 1 hour before checking again.")
        time.sleep(3600)
        continue
    # Define the number of threads to use
    num_threads = 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for channel in channels:
            future = executor.submit(scrape_videos_for_channel_with_lock, channel, commented_video_ids)
            futures.append(future)
        # Wait for all the threads to finish
        for future in concurrent.futures.as_completed(futures):
            # Catch and log any exceptions that occur within the threads
            try:
                result = future.result()
            except Exception as e:
                logger.exception(f"Error in thread: {e}")
    # Pause before checking again
    time.sleep(30)
