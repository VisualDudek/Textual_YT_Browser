import os
import pickle

from textual.app import App
from textual.widgets import ListView, ListItem, Footer, Label, DataTable
from textual.binding import Binding
from textual.containers import Horizontal
from textual import on
from rich.text import Text
from dataclasses import dataclass, field, fields
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from pathlib import Path


DATA = None
COLUMN_HEADERS = ("Time", "Title", "Duration")


# nice trick with self.data and super() init Label
class MyListItem(ListItem):
    def __init__(self, channel_name):
        self.data = channel_name
        label = channel_name
        number = count_new_videos(channel_name)
        if number > 0:
            label = f"{channel_name} ({number})"
        super().__init__(Label(label))

class CustomListView(ListView):

    BINDINGS = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
        Binding("r", "load_data_from_db", "Load data from DB", show=True),
    ]

    def action_load_data_from_db(self):
        global DATA
        DATA = load_data_from_db()
        self.update_data()

    def on_mount(self):
        self.update_data()

    def update_data(self):
        self.clear()
        for channel_name in DATA.keys():
            self.append(MyListItem(channel_name))


    
def count_new_videos(key) -> int:
    counter = 0
    for video in DATA[key]:
        if is_within_last_two_days(video.published_at):
            counter += 1
    return counter
 

class CustomDataTable(DataTable):

    BINDINGS = [
    # Binding("enter", "select_cursor", "Select", show=True),
    Binding("k", "cursor_up", "Cursor up", show=True),
    Binding("j", "cursor_down", "Cursor down", show=True),
    Binding("t", "style_row", "Toggle row", show=True),
    ]

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns(*COLUMN_HEADERS)
        # self.add_rows(ROWS)
        self.log(self.columns)
        self.cursor_foreground_priority = 'renderable'

    def update_table(self, key):
        self.clear()
        self.videos = DATA[key]
        self.key = key

        for video in DATA[key]:
            # if date is today, change color
            if video.published_at.date() == date.today():
                title = Text(video.title, style="bold red")
            elif video.published_at.date() >= date.today() - timedelta(days=2):
                title = Text(video.title, style="bold green")
            else:
                title = video.title

            if video.seen:
                title = Text(video.title, style="dim")
            
            row = (video.published_at, title, video.duration)
            self.add_row(*row, key=video.video_id)


    def action_style_row(self):
        row, col = self.cursor_row, self.cursor_column
        # self.log(self.get_cell_at((row, col)))
        # value = self.get_cell_at((row, col))
        # self.update_cell_at((row, col), Text(str(value), style="bold red"))
        id = self.videos[row]._id

        self.videos[row].seen = not self.videos[row].seen

        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, server_api= ServerApi('1')) # Timeout for connection
        db = mongo_client[MONGO_DATABASE_NAME]
        video_collection = db[MONGO_COLLECTION_NAME]

        video_collection.update_one(
            {"_id": id},
            {"$set": {"seen": self.videos[row].seen}},
        )

        if mongo_client:
            mongo_client.close()

        self.update_table(self.key)

    # def action_select_cursor(self):
    #     row, col = self.cursor_row, self.cursor_column
    #     value = self.get_cell_at((row, 1))
    #     self.log(value)

    @on(DataTable.RowSelected)
    def open_url_in_browser(self, event: DataTable.RowSelected):
        video_id = event.row_key.value
        self.app.open_url(f"https://www.youtube.com/watch?v={video_id}")
        

class MyApp(App):

    CSS = """
    CustomListView {
        width: 2fr;
    }
    CustomDataTable {
        width: 9fr;
    }
    """

    BINDINGS = [
        Binding("q", "exit", "Exit"),
        Binding("l", "focus_datatable", show=False)
        ]
    
    def compose(self):
        yield Footer()
        with Horizontal():
            yield CustomListView()
            yield CustomDataTable()

    def action_exit(self):
        self.exit()

    def action_focus_datatable(self):
        if self.query_one(CustomListView).has_focus:
            self.query_one(CustomDataTable).focus()
        else:
            self.query_one(CustomListView).focus()

    @on(ListView.Highlighted)
    def update_data_table(self, event: ListView.Highlighted):
        self.log(event.item)
        if event.item is not None:
            self.log(event.item.data)
            self.query_one(CustomDataTable).update_table(event.item.data)

def is_within_last_two_days(dt: datetime) -> bool:
    now = datetime.now()
    two_days_ago =  now - timedelta(days=2)
    return two_days_ago.date() <= dt.date() 
    

def load_data_from_db():
    # with open("data.pkl", "rb") as f:
    #     loaded_data = pickle.load(f)

    print(f"Connecting to MongoDB at {MONGO_URI}...")
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, server_api= ServerApi('1')) # Timeout for connection
    # Ping to confirm connection
    mongo_client.admin.command('ping') 
    print("Successfully connected to MongoDB.")

    db = mongo_client[MONGO_DATABASE_NAME]
    video_collection = db[MONGO_COLLECTION_NAME]

    # loaded_data = list(db.latest_ten.find())
    loaded_data = list(db.latest_20.find())

    data = dict()
    field_names = {f.name for f in fields(Video)}

    for item in loaded_data:
        channel_name = item["_id"]
        videos = []

        for video in item["latest_videos"]:
            filtered_data = {k:v for k,v in video.items() if k in field_names}
            videos.append(Video(**filtered_data))

        data[channel_name] = videos

    if mongo_client:
        mongo_client.close()
        print("\nMongoDB connection closed.")

    return data


@dataclass
class Video:
    _id: ObjectId
    title: str
    video_id: str
    published_at: datetime
    url: str = field(default="N/A")
    duration: str = field(default="N/A")
    seen: bool = field(default=False)

def pickle_data(data):
    with open("data.pkl", "wb") as f:
        pickle.dump(data, f)

def load_pickle_data():
    with open("data.pkl", "rb") as f:
        loaded_data = pickle.load(f)

    return loaded_data
    

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()  

    # --- MongoDB Configuration ---
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DATABASE_NAME = "youtube_data"
    MONGO_COLLECTION_NAME = "videos"     

    # --- Get init data logic ---
    file_path = Path("data.pkl")
    if file_path.exists():
        DATA = load_pickle_data()
    else:
        DATA = load_data_from_db()

    # --- Run TUI ---
    app = MyApp()
    app.run()

    # --- Save data ---
    pickle_data(DATA)