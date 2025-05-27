from textual.widgets import DataTable
from textual.binding import Binding
from textual import on
from rich.text import Text
from datetime import date, timedelta
from typing import List
from models import Video
from database import DatabaseService
from config import config
from utils import is_today, is_within_last_two_days
from youtube import get_video_duration
from widgets.summary_modalscreen import SummaryScreen
from google_ai import get_summary_url
from textual.worker import Worker, WorkerState
from database import DatabaseService


class CustomDataTable(DataTable):
    BINDINGS = [
        Binding("k", "cursor_up", "Cursor up", show=True),
        Binding("j", "cursor_down", "Cursor down", show=True),
        Binding("t", "style_row", "Toggle row", show=True),
        Binding("i", "get_video_info", "Get video info", show=True),
        Binding("s", "display_summary", "Display summary", show=True),
        Binding("a", "get_ai_summary", "Get AI summary", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.videos: List[Video] = []
        self.key = ""


    async def action_get_ai_summary(self):
        """Get detailed information about the current row's video"""
        if not self.videos:
            return
            
        row = self.cursor_row
        if row >= len(self.videos):
            return
            
        video = self.videos[row]
        # summary = await get_summary_url(video.url)
        self.worker = self.run_worker(get_summary_url(video.url, video), exclusive=False)

        # ----
        # video.summary = summary
        # video.has_summary = True

        # # Refresh the table with updated duration
        # self.update_cell(
        #     row_key=video.video_id,
        #     column_key="has_summary",
        #     value=video.has_summary)

    @on(Worker.StateChanged)
    def worker_state_changed(self, event: Worker.StateChanged):
        if event.state == WorkerState.SUCCESS:
            summary, video = event.worker.result
            self.app.notify(f"AI summary fetched successfully!\n{video.title}", title="Success")

            # ----
            # video = self.worker_video
            # video.summary = summary
            # video.has_summary = True
            # # Refresh the table with updated summary
            # self.update_cell(
            #     row_key=video.video_id,
            #     column_key="has_summary",
            #     value=video.has_summary)
            
            db_service = DatabaseService()
            db_service.update_video_summary(video.video_id, summary)

        elif event.state == WorkerState.ERROR:
            self.app.notify("Failed to fetch AI summary.", title="Error")


    def action_display_summary(self):
        """Display a summary of the current video"""
        if not self.videos:
            return
            
        row = self.cursor_row
        if row >= len(self.videos):
            return
            
        video = self.videos[row]

        self.app.push_screen(
            SummaryScreen(
                text=video.summary if video.has_summary else "No summary available.",
            )
        )

    def on_mount(self) -> None:
        self.cursor_type = "row"
        # self.add_columns(*config.column_headers)
        self.add_column("Published At", key="published_at")
        self.add_column("Title", key="title")
        self.add_column("Duration", key="duration")
        self.add_column("Has summary", key="has_summary")
        self.cursor_foreground_priority = 'renderable'

    def update_table(self, key: str, videos: List[Video]):
        """Update the table with videos for a specific channel"""
        self.clear()
        self.videos = videos
        self.key = key

        for video in videos:
            # Color coding based on publish date
            if is_today(video.published_at):
                title = Text(video.title, style="bold red")
            elif is_within_last_two_days(video.published_at):
                title = Text(video.title, style="bold green")
            else:
                title = video.title

            # Dim if already seen
            if video.seen:
                title = Text(video.title, style="dim")
            row = (video.published_at, title, video.duration, video.has_summary)
            self.add_row(*row, key=video.video_id)

    def action_get_video_info(self):
        """Get detailed information about the current row's video"""
        if not self.videos:
            return
            
        row = self.cursor_row
        if row >= len(self.videos):
            return
            
        video = self.videos[row]
        video.duration = get_video_duration(video)

        info = f"Title: {video.title}\nPublished At: {video.published_at}\nDuration: {video.duration}\nSeen: {'Yes' if video.seen else 'No'}"
        
        self.app.notify(info, title="Video Information")

        # Refresh the table with updated duration
        self.update_cell(
            row_key=video.video_id,
            column_key="duration",
            value=video.duration)

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
        db_service.update_video_seen_status(video.video_id, video.seen)

        # Refresh the table
        self.update_table(self.key, self.videos)

    @on(DataTable.RowSelected)
    def open_url_in_browser(self, event: DataTable.RowSelected):
        """Open the selected video in browser"""
        video_id = event.row_key.value
        self.app.open_url(f"https://www.youtube.com/watch?v={video_id}")