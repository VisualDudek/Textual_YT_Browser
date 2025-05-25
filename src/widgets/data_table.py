from textual.widgets import DataTable
from textual.binding import Binding
from textual import on
from rich.text import Text
from datetime import date, timedelta
from typing import List
from models import Video
from database import DatabaseService
from config import config

class CustomDataTable(DataTable):
    BINDINGS = [
        Binding("k", "cursor_up", "Cursor up", show=True),
        Binding("j", "cursor_down", "Cursor down", show=True),
        Binding("t", "style_row", "Toggle row", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.videos: List[Video] = []
        self.key = ""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns(*config.column_headers)
        self.cursor_foreground_priority = 'renderable'

    def update_table(self, key: str, videos: List[Video]):
        """Update the table with videos for a specific channel"""
        self.clear()
        self.videos = videos
        self.key = key

        for video in videos:
            # Color coding based on publish date
            if video.published_at.date() == date.today():
                title = Text(video.title, style="bold red")
            elif video.published_at.date() >= date.today() - timedelta(days=2):
                title = Text(video.title, style="bold green")
            else:
                title = video.title

            # Dim if already seen
            if video.seen:
                title = Text(video.title, style="dim")
            
            row = (video.published_at, title, video.duration)
            self.add_row(*row, key=video.video_id)

    def action_style_row(self):
        """Toggle the seen status of the current row's video"""
        if not self.videos:
            return
            
        row = self.cursor_row
        if row >= len(self.videos):
            return
            
        video = self.videos[row]
        video.seen = not video.seen

        # Update in database
        db_service = DatabaseService()
        db_service.update_video_seen_status(video._id, video.seen)

        # Refresh the table
        self.update_table(self.key, self.videos)

    @on(DataTable.RowSelected)
    def open_url_in_browser(self, event: DataTable.RowSelected):
        """Open the selected video in browser"""
        video_id = event.row_key.value
        self.app.open_url(f"https://www.youtube.com/watch?v={video_id}")