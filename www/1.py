import requests
import re
from bs4 import BeautifulSoup

# Load channels from a text file
with open('channels.txt', 'r') as f:
    channels = [line.strip() for line in f.readlines()]

# Scrape videos for each channel
for channel in channels:
    url = f'https://www.youtube.com/channel/{channel}/videos'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(str(soup))
    video_ids = []
    pattern = re.compile(r'"videoIds":\[(.*?)\]')
    matches = pattern.findall(str(soup))

    # Преобразуем результаты в список уникальных значений
    unique_video_ids = list(set([id.strip('"') for match in matches for id in match.split(',')]))

    # Выводим результаты
    print(unique_video_ids)
    print(len(unique_video_ids))
