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

data_output = []

for channel in channel_ids:

    channel_request = youtube.channels().list(
        id=channel,  # Tutaj jest możliwość podania kilku ID kanału
        part='snippet,contentDetails',
    )
    channel_response = channel_request.execute()

    uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    channel_title = channel_response['items'][0]['snippet']['title']

    data_output.append({
        'channel_id': channel,
        'channel_title': channel_title,
        'uploads_id': uploads_id
    })

# Save the updated config back to the YAML file
save_youtube_config(config.yt_config_file, {'channels': data_output})
