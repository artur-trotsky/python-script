import googleapiclient.discovery
import os

# Define API key
API_KEY = "AIzaSyC9kNuNOk_ERm8Gj1-XxcP3RmfofQTqOcM"

# Define YouTube API client
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

# Load channels from text file
with open("channels.txt", "r") as file:
    channels = [line.strip() for line in file.readlines()[:100]]

# Request channel data from YouTube API
results = youtube.channels().list(part="snippet,contentDetails,statistics", id=",".join(channels)).execute()

# Print channel data
for item in results["items"]:
    print("Title: " + item["snippet"]["title"])
    print("ID: " + item["id"])
    print("Views: " + item["statistics"]["viewCount"])
    print("Subscribers: " + item["statistics"]["subscriberCount"])
    print("Videos: " + item["statistics"]["videoCount"])
    print("\n")
