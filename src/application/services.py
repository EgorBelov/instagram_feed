# application/services.py
from src.application.dto import CreatePostDTO, CreatePostResultDTO, CreateStoryDTO, CreateStoryResultDTO
from src.infrastructure.repositories import PostRepository, StoryRepository, UserRepository
from src.domain.commands import CreatePostCommand, CreateStoryCommand
from src.domain.events import PostCreatedEvent, StoryCreatedEvent
import datetime

# Пример сервиса для создания поста
async def create_post(command_dto: CreatePostDTO, db) -> CreatePostResultDTO:
    # Можно преобразовать DTO в команду доменного слоя (если требуется)
    command = CreatePostCommand(
        user_id=command_dto.user_id,
        image_url=command_dto.image_url,
        caption=command_dto.caption,
        created_at=datetime.datetime.utcnow()
    )
    repo = PostRepository(db)
    post = await repo.create_post(command)
    # После успешного создания можно сформировать событие (например, уведомление)
    event = PostCreatedEvent(post_id=post.id, user_id=post.user_id)
    # Здесь можно вызвать механизм публикации события, например, notify_friends(...)
    return CreatePostResultDTO(message="Пост успешно создан", post_id=post.id)

async def get_feed(user_id: int, db) -> list:
    user_repo = UserRepository(db)
    return await user_repo.get_feed(user_id)

async def create_story(command_dto: CreateStoryDTO, db) -> CreateStoryResultDTO:
    command = CreateStoryCommand(
        user_id=command_dto.user_id,
        image_url=command_dto.image_url,
        created_at=datetime.datetime.utcnow()
    )
    repo = StoryRepository(db)
    story = await repo.create_story(command)
    event = StoryCreatedEvent(story_id=story.id, user_id=story.user_id)
    return CreateStoryResultDTO(message="История успешно создана", story_id=story.id)

async def get_stories(user_id: int, db) -> list:
    user_repo = UserRepository(db)
    return await user_repo.get_stories(user_id)
