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


def get_comment_message():
    """
    Generates a random comment message from a list of options using spintax syntax.
    """
    comment_messages = [
        "{Hey|Hello|Hi}, {great video!|nice content!|awesome work!}",
        "{Keep up the good work!|You're doing great!|Excellent content!}",
        "{I really enjoyed this video!|This video was so informative!|Thanks for sharing your knowledge!}",
        "{Can't wait for your next video!|Looking forward to seeing more!|Excited for what's next!}",
        "{You have a new subscriber!|Just subscribed!|Subscribed and hit the notification bell!}",
        "{This video deserves more views!|Underrated content!|Why isn't this more popular?}",
        "{Thanks for making my day better!|Your videos always brighten my day!|Your positive energy is infectious!}",
        "{Great job on the production quality!|Love the editing!|You have some serious skills behind the camera!}",
        "{I learned something new today!|I never knew that before!|Thanks for teaching me something new!}",
        "{You're a natural on camera!|So comfortable in front of the camera!|Love your personality on camera!}",
        "{This|That} is {amazing|fantastic|incredible}! {Great job|Well done|Kudos}!",
        "{Keep it up|Keep up the good work}! {I love|I really like} this video.",
        "{This is|That was} {so helpful|so informative|a great tutorial}. {Thank you|Thanks} for sharing!",
        "{I'm|I am} {impressed|blown away} by your {skills|talent}. {You are|You're} amazing!",
        "{Awesome video|Great video|Excellent content}! {Thanks for sharing|Thanks for posting}.",
        "{I've|I have} {learned so much|picked up so many great tips} from this video. {Thanks|Thank you}!",
        "{This video|Your content} {deserves|merits} {more views|more attention}. {Keep up|Keep it up} the great work!",
        "{Your|This} {channel|content} {is|has been} {a great resource|so helpful} to me. {Thanks|Thank you}!",
        "{This|That} {was|is} {so interesting|fascinating}. {I can't wait|Looking forward} to {seeing|watching} more from you.",
        "{You|Your channel} {is|are} {an inspiration|awesome}. {Keep it up|Keep up the good work}!",
        "{Amazing|Awesome|Fantastic} video! {I loved it|It was great|Keep it up}.",
        "{This|That} {was|is} {exactly what I needed|so helpful|very informative}. {Thanks|Thank you} for sharing.",
        "{This video|Your content} {is|has been} {so helpful|a great help} to me. {Thanks|Thank you} for {sharing|posting}.",
        "{I'm|I am} {a new subscriber|subscribed}! {I can't wait|Looking forward} to {seeing|watching} more from you.",
        "{You|Your channel} {deserve|deserves} {more subscribers|more views}. {Keep up|Keep it up} the great work!",
        "{Excellent|Fantastic|Great} video! {Thanks for sharing|Thanks for posting}.",
        "{You|Your channel} {are|is} {a great inspiration|so talented}. {Thanks|Thank you} for {sharing|posting}.",
        "{This|That} {was|is} {so helpful|very informative}. {Thanks|Thank you} for {sharing|posting}.",
        "{I|We} {love|enjoy} {your content|watching your videos}. {Keep it up|Keep up the good work}!",
        "{This|That} {was|is} {exactly what I was looking for|so helpful}. {Thanks|Thank you} for sharing.",
        "{Your|This} {channel|content} {has|is} {been so helpful|a great help} to me. {Thanks|Thank you}!",
        "{Great video|Awesome video|Amazing content}! {Thanks for sharing|Thanks for posting}.",
        "{I|We} {can't wait|are looking forward} to {seeing|watching} more from you. {Keep up|Keep it up} the great work!",
        "{This video|Your content} {has|is} {given me|proven to be} {so much value|a great resource}. {Thanks|Thank you} for {sharing|posting}.",
        "{Great video!|Awesome content!|Fantastic work!}",
        "{Wow, this is impressive!|I'm blown away by this!|This is incredible!}",
        "{I love this!|This is amazing!|This is so cool!}",
        "{You're killing it!|Keep up the great work!|You're doing an awesome job!}",
        "{This is exactly what I needed today!|Thanks for sharing this!|You're making my day with this video!}",
        "{I can't stop watching this!|I'm hooked on your content!|This is so addicting!}",
        "{Your videos always inspire me!|You're such a motivator!|I look up to you so much!}",
        "{You have a gift for this!|Your talent is shining through!|You're a natural at this!}",
        "{This video just made my day!|I'm so grateful for this content!|Thank you for sharing this with us!}",
        "{You're a true expert in your field!|I'm learning so much from you!|You're a wealth of knowledge!}",
        "{Your enthusiasm is contagious!|I love your energy!|You're so passionate about what you do!}",
        "{You have a unique perspective on things!|I always learn something new from you!|You bring a fresh take to everything you do!}",
        "{Your creativity is inspiring!|You have such a creative mind!|I'm always amazed by your ideas!}",
        "{I can't wait to see what you do next!|I'm eagerly anticipating your next video!|You're always surprising me with your content!}",
        "{This is such a helpful video!|I'm taking notes on everything you're saying!|You're making things so clear for me!}",
        "{You have a real talent for teaching!|You explain things so well!|You're making this so easy for me to understand!}",
        "{Your positive attitude is infectious!|I love your optimism!|You always find the silver lining!}",
        "{This video is a game-changer!|You're revolutionizing the way we think about this!|You're taking things to the next level!}",
        "{You have a great sense of humor!|Your videos always make me laugh!|You're so funny and entertaining!}",
        "{I can't believe how much value you're providing!|You're so generous with your knowledge!|You're giving so much back to your audience!}",
        "{You're such a natural on camera!|You have a great presence!|You're so comfortable in front of the camera!}",
        "{I'm always excited to see what you're up to!|You're always up to something exciting!|You never cease to amaze me with your content!}",
        "{You're changing lives with your videos!|You're making a real difference in the world!|You're helping so many people with your content!}",
        "{You have a gift for storytelling!|You're a great storyteller!|You have a real knack for narrative!}",
        "{Your videos are so well-produced!|You have a great eye for detail!|You're a true professional!}",
        "{You're a master of your craft!|You've really honed your skills!|You're at the top of your game!}",
        "{I'm always recommending your videos to others!|You're my go-to source for this topic!|You're so reliable and trustworthy!}"
    ]

    message = random.choice(comment_messages)
    pattern = re.compile(r'\{([^}]+)\}')

    return pattern.sub(lambda x: random.choice(x.group(1).split("|")), message)


commented_video_ids = []


# Define a function to load channels from a file or database
def load_channels(src, max_channels=100):
    chnls = []
    if src == 'file':
        try:
            with open('youtube_channelsv.txt', 'r') as f:
                channel_lines = [line.strip() for line in f.readlines()]
            chnls = channel_lines[:max_channels]
        except FileNotFoundError:
            print("File 'youtube_channels.txt' not found!")
    elif src == 'database':
        try:
            # Connect to the database
            conn = mysql.connector.connect(**config)
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
            print("Error connecting to database:", e)
    return chnls


# Define a function to scrape videos for a single channel
def scrape_videos_for_channel(channel_id, commented_video_ids):
    # Try both URL variants
    urls = [f'https://www.youtube.com/{channel_id}/videos', f'https://www.youtube.com/channel/{channel_id}/videos']
    for url in urls:
        new_video_id = scrape_videos(url, commented_video_ids)
        # Если найден новый уникальный идентификатор, то оставляем комментарий и добавляем его в список commented_video_ids
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


def scrape_videos_for_channel_with_lock(channel_url, commented_video_ids):
    """
    Scrape videos for a single channel, using a lock to ensure
    safe access to the commented_video_ids set.
    """
    try:
        # Scrape the videos for the channel
        scrape_videos_for_channel(channel_url, commented_video_ids)
    except Exception as e:
        # Log any exceptions that occur
        logger.exception(f"Error scraping videos for channel {channel_url}: {e}")


# Scrape videos for each channel using multiple threads
while True:
    source = 'database'
    channels = load_channels(source, 100)
    if not channels:
        print("No channels found. Waiting for 1 hour before checking again.")
        time.sleep(3600)
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
    time.sleep(30)
