from collections import OrderedDict
from bs4 import BeautifulSoup
from selenium import webdriver
import logging
import mysql.connector
import random
import re
import threading
import time
import json

# Loading a config from a file
with open('config.json') as f:
    config = json.load(f)


def scrape_videos(youtube_url, video_ids):
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

        # Converting the results to a list of unique values and preserving the order of the elements
        unique_video_ids = list(OrderedDict.fromkeys([id.strip('"') for match in matches for id in match.split(',')]))

        # Get the first unique video id
        new_video_id = next((vid for vid in unique_video_ids if vid not in video_ids), None)
        if new_video_id is not None:
            break
        if new_height == last_height:
            break
        last_height = new_height

    # Close the virtual driver
    driver.quit()

    return new_video_id


def get_comment_message():
    """
    Generates a random comment message from a list of options using spintax syntax.
    """
    message = random.choice(config['spintax_comment_messages'])
    pattern = re.compile(r'\{([^}]+)\}')

    return pattern.sub(lambda x: random.choice(x.group(1).split("|")), message)


commented_video_ids = []


# Define a function to load channels from a file or database
def load_channels(src, max_channels=100):
    chnls = []
    if src == 'file':
        try:
            with open(config['youtube_channels_file'], 'r') as f:
                channel_lines = [line.strip() for line in f.readlines()]
            chnls = channel_lines[:max_channels]
        except FileNotFoundError:
            print('File ' + config['youtube_channels_file'] + ' not found!')
    elif src == 'database':
        try:
            # Connect to the database
            conn = mysql.connector.connect(**config['database_config'])
            cursor = conn.cursor()

            # Load channels from the database
            query = "SELECT channel_url FROM channels LIMIT %s"
            cursor.execute(query, (max_channels,))
            rows = cursor.fetchall()
            for row in rows:
                chnls.append(row[0])

            # Close the database connection
            conn.close()
        except mysql.connector.Error as e:
            print('Error connecting to database:', e)
    return chnls


# Define a function to scrape videos for a single channel
def scrape_videos_for_channel(channel_id, video_ids):
    # Try both URL variants
    urls = [f'https://www.youtube.com/{channel_id}/videos', f'https://www.youtube.com/channel/{channel_id}/videos']
    for url in urls:
        new_video_id = scrape_videos(url, video_ids)
        # If a new unique identifier is found, then leave a comment and add it to the list commented_video_ids
        if new_video_id is not None:
            comment_text = get_comment_message()
            print(comment_text)
            # comment_on_video(new_video_id, comment_text)
            commented_video_ids.append(new_video_id)
            # Break out of the inner for loop so that we don't try the other URL variant
            print(channel_id)
            print(new_video_id)
            break


# Create a lock for accessing the commented_video_ids set
commented_video_ids_lock = threading.Lock()

# Create a logger for logging exceptions in the threads
logger = logging.getLogger(__name__)


def scrape_videos_for_channel_with_lock(channel_url, video_ids):
    """
    Scrape videos for a single channel, using a lock to ensure
    safe access to the video_ids set.
    """
    try:
        # Scrape the videos for the channel
        scrape_videos_for_channel(channel_url, video_ids)
    except Exception as e:
        # Log any exceptions that occur
        logger.exception(f"Error scraping videos for channel {channel_url}: {e}")


# Scrape videos for each channel using multiple threads
while True:
    channels = load_channels(config['source'], config['max_channels'])
    if not channels:
        print('No channels found. Waiting for ' + config['wait_interval_no_channels'] + ' sec before checking again.')
        time.sleep(config['wait_interval_no_channels'])
        continue
    threads = []
    for channel in channels:
        thread = threading.Thread(target=scrape_videos_for_channel_with_lock, args=(channel, commented_video_ids))
        threads.append(thread)
        thread.start()
    # Wait for all the threads to finish
    for thread in threads:
        # Catch and log any exceptions that occur within the threads
        try:
            thread.join()
        except Exception as e:
            logger.exception(f"Error in thread: {e}")
    # Pause before checking again
    print('Pause before checking again')
    print(commented_video_ids)
    time.sleep(config['wait_interval_after_scrape'])
