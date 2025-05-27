from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError
from dataclasses import fields
from typing import Dict, List
from models import Video, VideoYT
from config import config
import logging

logging.basicConfig(level=logging.INFO)

class DatabaseService:
    def __init__(self):
        self.client = None
        
    def connect(self) -> MongoClient:
        """Establish MongoDB connection"""
        logging.info(f"Connecting to MongoDB at {config.mongo_uri}...")
        self.client = MongoClient(
            config.mongo_uri, 
            serverSelectionTimeoutMS=config.connection_timeout_ms, 
            server_api=ServerApi('1')
        )
        self.client.admin.command('ping')
        logging.info("Successfully connected to MongoDB.")
        return self.client
        
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed.")
            
    def load_videos(self) -> Dict[str, List[VideoYT]]:
        """Load video data from MongoDB"""
        self.connect()
        
        db = self.client[config.mongo_database_name]
        loaded_data = list(db.latest_20.find())

        data: dict[str, List[VideoYT]] = {}
        field_names = {f.name for f in fields(VideoYT)}

        for item in loaded_data:
            channel_name: str = item["_id"]
            videos: List[VideoYT] = []

            for video in item["latest_videos"]:
                filtered_data = {k: v for k, v in video.items() if k in field_names}
                videos.append(VideoYT(**filtered_data))

            data[channel_name] = videos
            
        self.disconnect()
        return data
        
    def update_video_seen_status(self, video_id, seen_status: bool):
        """Update the seen status of a video"""
        self.connect()
        
        db = self.client[config.mongo_database_name]
        video_collection = db[config.mongo_collection_name]
        
        video_collection.update_one(
            {"_id": video_id},
            {"$set": {"seen": seen_status}},
        )
        
        self.disconnect()

    def save_videos(self, videos: list[VideoYT]):
        """Save video data to MongoDB"""
        self.connect()

        db = self.client[config.mongo_database_name]
        video_collection = db[config.mongo_collection_name]

        for video in videos:
            try:
                video_collection.insert_one(video.to_dict())
                print(f"Successfully saved video to MongoDB: {video.title} (ID: {video.video_id})")
            except DuplicateKeyError:
                print(f"Video already exists in MongoDB (ID: {video.video_id}). Skipping.")
            except Exception as e:
                print(f"An error occurred while saving video {video.title} to MongoDB: {e}")

        self.disconnect()