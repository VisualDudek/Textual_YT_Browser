import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    # MongoDB settings
    mongo_uri: str = os.getenv("MONGO_URI")
    mongo_database_name: str = "youtube_data"
    mongo_collection_name: str = "videos"
    
    # UI settings
    column_headers: tuple = ("Time", "Title", "Duration")
    
    # Data settings
    default_pickle_file: str = "data.pkl"
    connection_timeout_ms: int = 5000

# Create a global config instance
config = Config()