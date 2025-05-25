from youtube import get_last_videos
from database import DatabaseService
from config import config
from models import YTConfig

ytconfig = YTConfig.from_yaml(config.yt_config_file)
dbservice = DatabaseService()

for channel_title, channel_id in ytconfig.channels.items():
    videos = get_last_videos(channel_id, max_results=ytconfig.results)
    dbservice.save_videos(videos)