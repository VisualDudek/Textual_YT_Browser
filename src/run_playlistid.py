from config import config
from youtube import load_youtube_config, save_youtube_config
from googleapiclient.discovery import build


# Build the YouTube API service object
youtube = build(
    config.youtube_api_service_name, 
    config.youtube_api_version, 
    developerKey=config.youtube_api_key
    )

yaml_file = load_youtube_config(config.yt_config_file)

channel_ids = [channel for channel in yaml_file['channels'].values()]

for channel in channel_ids:

    channel_request = youtube.channels().list(
        id=channel,  # Tutaj jest możliwość podania kilku ID kanału
        part='snippet,contentDetails',
    )
    channel_response = channel_request.execute()

    uploads = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    youtube = build(
        config.youtube_api_service_name, 
        config.youtube_api_version, 
        developerKey=config.youtube_api_key
        )

    playlist_request = youtube.playlistItems().list(
        playlistId=uploads,
        part='snippet',
        maxResults=5,
    )
    playlist_response = playlist_request.execute()
    items = playlist_response['items']
    for item in items:
        video_id = item['snippet']['resourceId']['videoId']
        video_title = item['snippet']['title']
        published_at_str = item['snippet']['publishedAt']
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['channelTitle']

        print(f"Video ID: {video_id}, Title: {video_title}, Published At: {published_at_str}, Channel ID: {channel_id}, Channel Title: {channel_title}")
    pass

pass