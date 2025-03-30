# domain/events.py
class PostCreatedEvent:
    def __init__(self, post_id: int, user_id: int):
        self.post_id = post_id
        self.user_id = user_id

class StoryCreatedEvent:
    def __init__(self, story_id: int, user_id: int):
        self.story_id = story_id
        self.user_id = user_id
