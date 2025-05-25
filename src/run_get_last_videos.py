from config import config
from youtube import get_last_videos


# videos = get_last_videos(
#         channel_id="UCSHZKyawb77ixDdsGog4iWA", 
#         max_results=25,
#     )

# for video in videos:
#     print(video)

from googleapiclient.discovery import build
# Build the YouTube API service object
# youtube = build(
#     config.youtube_api_service_name, 
#     config.youtube_api_version, 
#     developerKey=config.youtube_api_key
#     )

# activity_request = youtube.channels().list(
#     id="UCSHZKyawb77ixDdsGog4iWA", 
#     part='snippet,contentDetails',
# )
# activity_response = activity_request.execute()


uploads = 'UUSHZKyawb77ixDdsGog4iWA'
youtube = build(
    config.youtube_api_service_name, 
    config.youtube_api_version, 
    developerKey=config.youtube_api_key
    )

activity_request = youtube.playlistItems().list(
    playlistId=uploads,
    part='snippet,contentDetails',
    maxResults=25,
)
activity_response = activity_request.execute()

pass