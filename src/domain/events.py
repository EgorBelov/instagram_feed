# domain/events.py
import datetime


class PostCreatedEvent:
    def __init__(self, post_id: int, user_id: int, created_at: datetime.datetime):
        self.post_id = post_id
        self.user_id = user_id
        self.created_at = created_at

class StoryCreatedEvent:
    def __init__(self, story_id: int, user_id: int, created_at: datetime.datetime):
        self.story_id = story_id
        self.user_id = user_id
        self.created_at = created_at
