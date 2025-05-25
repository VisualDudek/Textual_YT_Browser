from dataclasses import dataclass, field
from datetime import datetime
from bson import ObjectId

@dataclass
class Video:
    _id: ObjectId
    title: str
    video_id: str
    published_at: datetime
    url: str = field(default="N/A")
    duration: str = field(default="N/A")
    seen: bool = field(default=False)