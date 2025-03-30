# application/services.py
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.application.dto import CreatePostDTO, CreatePostResultDTO, CreateStoryDTO, CreateStoryResultDTO
from src.infrastructure.database import get_db
from src.infrastructure.repositories import NotificationRepository, PostRepository, StoryRepository, UserRepository
from src.domain.commands import CreatePostCommand, CreateStoryCommand
from src.domain.events import PostCreatedEvent, StoryCreatedEvent
import datetime

from src.models.models import User


# WebSocket для уведомлений (упрощённый пример)
active_connections: dict = {} 


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
    event = PostCreatedEvent(post_id=post.id, user_id=post.user_id, created_at=post.created_at)

    post_data = {
        "post_id": event.post_id,
        "user_id": event.user_id,
        "created_at": event.created_at.isoformat(),
        "type": "post"
    }
    await notify_friends(event.user_id, post_data, db)
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
    event = StoryCreatedEvent(story_id=story.id, user_id=story.user_id, created_at=story.created_at)
    story_data = {
        "story_id": event.story_id,
        "user_id": event.user_id,
        "created_at": event.created_at.isoformat(),
        "type": "story"
    }
    await notify_friends(event.user_id, story_data, db)
    return CreateStoryResultDTO(message="История успешно создана", story_id=story.id)

async def get_stories(user_id: int, db) -> list:
    user_repo = UserRepository(db)
    return await user_repo.get_stories(user_id)


async def notify_friends(author_id: int, post_data: dict, db=Depends(get_db)):
    # Загружаем автора с подписчиками
    result = await db.execute(
        select(User).options(selectinload(User.followers)).where(User.id == author_id)
    )
    author = result.scalar_one_or_none()
    if not author:
        return
    
    # Для каждого подписчика отправляем уведомление через WebSocket и сохраняем уведомление в базе
    for follower in author.followers:
        ws = active_connections.get(follower.id)
        if ws:
            try:
                await ws.send_json(post_data)
            except Exception as e:
                # Если отправка не удалась, можно залогировать ошибку
                print(f"Ошибка отправки WebSocket уведомления для пользователя {follower.id}: {e}")
        
