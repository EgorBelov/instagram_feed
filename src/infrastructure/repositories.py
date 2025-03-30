# infrastructure/repositories.py
from src.models.models import Post, Story, User
from src.domain.commands import CreatePostCommand, CreateStoryCommand
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

class PostRepository:
    def __init__(self, db):
        self.db = db

    async def create_post(self, command: CreatePostCommand) -> Post:
        post = Post(
            user_id=command.user_id,
            image_url=command.image_url,
            caption=command.caption,
            created_at=command.created_at
        )
        self.db.add(post)
        await self.db.flush()  # Получаем сгенерированный id
        await self.db.commit()
        return post

class StoryRepository:
    def __init__(self, db):
        self.db = db

    async def create_story(self, command: CreateStoryCommand) -> Story:
        story = Story(
            user_id=command.user_id,
            image_url=command.image_url,
            created_at=command.created_at
        )
        self.db.add(story)
        await self.db.flush()
        await self.db.commit()
        return story

class UserRepository:
    def __init__(self, db):
        self.db = db

    async def get_feed(self, user_id: int) -> list:
        # Получаем пользователя с его подписками (friends)
        result = await self.db.execute(
            select(User).options(selectinload(User.followed)).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return []
        followed_ids = [u.id for u in user.followed]
        followed_ids.append(user_id)
        # Запрос постов друзей
        result = await self.db.execute(
            select(Post).where(Post.user_id.in_(followed_ids)).order_by(Post.created_at.desc())
        )
        posts = result.scalars().all()
        # Приведение к списку dict
        feed = [{
            "id": p.id,
            "user_id": p.user_id,
            "image_url": p.image_url,
            "caption": p.caption,
            "created_at": p.created_at.isoformat()
        } for p in posts]
        return feed

    async def get_stories(self, user_id: int) -> list:
        result = await self.db.execute(
            select(User).options(selectinload(User.followed)).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return []
        friend_ids = [u.id for u in user.followed]
        friend_ids.append(user_id)
        result = await self.db.execute(
            select(Story).where(Story.user_id.in_(friend_ids)).order_by(Story.created_at.desc())
        )
        stories = result.scalars().all()
        return [{
            "id": s.id,
            "user_id": s.user_id,
            "image_url": s.image_url,
            "created_at": s.created_at.isoformat()
        } for s in stories]
