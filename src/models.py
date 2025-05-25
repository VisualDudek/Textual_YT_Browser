from dataclasses import dataclass, field
from datetime import datetime
from bson import ObjectId
from typing import Dict
import yaml

@dataclass
class Video:
    _id: ObjectId
    title: str
    video_id: str
    published_at: datetime
    url: str = field(default="N/A")
    duration: str = field(default="N/A")
    seen: bool = field(default=False)

@dataclass
class YTConfig:
    channels: Dict[str, str]
    results: int
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'YTConfig':
        """Load configuration from YAML file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return cls(**data)