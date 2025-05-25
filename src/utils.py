import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from config import config
from models import Video

def is_within_last_two_days(dt: datetime) -> bool:
    """Check if datetime is within the last two days"""
    now = datetime.now()
    two_days_ago = now - timedelta(days=2)
    return two_days_ago.date() <= dt.date()

def count_new_videos(videos: List[Any]) -> int:
    """Count videos published within the last two days"""
    return sum(1 for video in videos if is_within_last_two_days(video.published_at))

def pickle_data(data: Dict[str, List[Any]]):
    """Save data to pickle file"""
    with open(config.default_pickle_file, "wb") as f:
        pickle.dump(data, f)

def load_pickle_data() -> Dict[str, List[Any]]:
    """Load data from pickle file"""
    with open(config.default_pickle_file, "rb") as f:
        return pickle.load(f)

def get_initial_data() -> Dict[str, List[Any]]:
    """Get initial data from pickle file or database"""
    from database import DatabaseService
    
    file_path = Path(config.default_pickle_file)
    if file_path.exists():
        return load_pickle_data()
    else:
        db_service = DatabaseService()
        return db_service.load_videos()