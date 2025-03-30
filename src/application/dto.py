# application/dto.py
from pydantic import BaseModel

class CreatePostDTO(BaseModel):
    user_id: int
    image_url: str
    caption: str = ""

class CreatePostResultDTO(BaseModel):
    message: str
    post_id: int
    type: str = "post"

class CreateStoryDTO(BaseModel):
    user_id: int
    image_url: str

class CreateStoryResultDTO(BaseModel):
    message: str
    story_id: int
    type: str = "story"
