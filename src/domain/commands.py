# domain/commands.py
import datetime

class CreatePostCommand:
    def __init__(self, user_id: int, image_url: str, caption: str, created_at: datetime.datetime):
        self.user_id = user_id
        self.image_url = image_url
        self.caption = caption
        self.created_at = created_at

class CreateStoryCommand:
    def __init__(self, user_id: int, image_url: str, created_at: datetime.datetime):
        self.user_id = user_id
        self.image_url = image_url
        self.created_at = created_at
