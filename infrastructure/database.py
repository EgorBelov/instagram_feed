import asyncio
import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, User, Post, Story, Comment, Reaction  # модели должны быть в файле models.py

# Задайте URL подключения к вашей базе данных
DATABASE_URL = "postgresql+asyncpg://postgres:123321@localhost/inst_feed"

async def create_sample_data():
    # Создание асинхронного движка и пересоздание таблиц (drop_all и create_all)
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Создание сессии для работы с базой данных
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        # Создаем тестовых пользователей
        user1 = User(username="alice")
        user2 = User(username="bob")
        user3 = User(username="charlie")
        session.add_all([user1, user2, user3])
        await session.commit()
        # Обновляем объекты, чтобы получить их ID
        await session.refresh(user1)
        await session.refresh(user2)
        await session.refresh(user3)
        
        # Устанавливаем отношения подписки:
        # Пусть alice подписана на bob, bob подписан на charlie, а charlie подписан на alice
        user1.followed.append(user2)
        user2.followed.append(user3)
        user3.followed.append(user1)
        await session.commit()
        
        # Создаем тестовые посты
        post1 = Post(user_id=user1.id, image_url="http://example.com/alice1.jpg",
                     caption="Пост от Alice", created_at=datetime.datetime.utcnow())
        post2 = Post(user_id=user2.id, image_url="http://example.com/bob1.jpg",
                     caption="Пост от Bob", created_at=datetime.datetime.utcnow())
        post3 = Post(user_id=user3.id, image_url="http://example.com/charlie1.jpg",
                     caption="Пост от Charlie", created_at=datetime.datetime.utcnow())
        session.add_all([post1, post2, post3])
        await session.commit()
        
        # Создаем тестовые истории (stories)
        story1 = Story(user_id=user1.id, image_url="http://example.com/alice_story.jpg",
                       created_at=datetime.datetime.utcnow())
        story2 = Story(user_id=user2.id, image_url="http://example.com/bob_story.jpg",
                       created_at=datetime.datetime.utcnow())
        session.add_all([story1, story2])
        await session.commit()
        
        # Добавляем тестовые комментарии
        comment1 = Comment(post_id=post2.id, user_id=user1.id,
                           text="Отличный пост, Bob!", created_at=datetime.datetime.utcnow())
        comment2 = Comment(post_id=post3.id, user_id=user2.id,
                           text="Красивое фото, Charlie!", created_at=datetime.datetime.utcnow())
        session.add_all([comment1, comment2])
        await session.commit()
        
        # Добавляем тестовые реакции
        reaction1 = Reaction(post_id=post1.id, user_id=user2.id, type="like",
                             created_at=datetime.datetime.utcnow())
        reaction2 = Reaction(post_id=post2.id, user_id=user3.id, type="heart",
                             created_at=datetime.datetime.utcnow())
        session.add_all([reaction1, reaction2])
        await session.commit()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
