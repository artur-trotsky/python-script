from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

CLIENT_ID = '256038866299-s1c8mdtua2e1ck7m013t1amokoltqvil.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REFRESH_TOKEN = "1//04fxp9K8zqEmICgYIARAAGAQSNwF-L9Ire6sXjDqOAtOWGQxZ-vnMZn62QJtbdMj93IUPwgTXwqo7LEy0xzd6TZxmdAqbyurlTs8"
TOKEN_URI = 'https://oauth2.googleapis.com/token'
CHANNEL_ID = 'UC_x5XG1OV2P6uZZ5FSM9Ttw'
VIDEO_ID = 'your_video_id'
COMMENT_TEXT = '-q1SYXdRXkU'

# Создание объекта Credentials
creds = Credentials.from_authorized_user_info(info={'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
                                                    'refresh_token': REFRESH_TOKEN})
# Создание объекта YouTube API
youtube = build('youtube', 'v3', credentials=creds)

try:
    # Получение информации о текущем пользователе
    channels_response = youtube.channels().list(part='snippet', mine=True).execute()

    # Вывод информации о текущем пользователе
    for channel in channels_response['items']:
        print('You are logged in as {}.'.format(channel['snippet']['title']))
except HttpError as error:
    print('An error occurred: {}'.format(error))