import os
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy.future import select
from models.models import Base, Story, User, Post, Comment, Reaction  # Предполагается, что модели в файле models.py
import datetime
from fastapi.responses import FileResponse, HTMLResponse


html_router = APIRouter()

@html_router.get("/", response_class=HTMLResponse)
async def get_index():
    # Определяем путь к файлу index.html
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "index.html")
    return FileResponse(index_path)


app = FastAPI()



DATABASE_URL = "postgresql+asyncpg://postgres:123321@localhost/inst_feed"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Зависимость для получения сессии базы данных
async def get_db():
    async with async_session() as session:
        yield session

# Эндпоинт для получения ленты пользователя
@app.get("/feed")
async def get_feed(user_id: int, db: AsyncSession = Depends(get_db)):
    # Выполняем запрос и извлекаем объект пользователя
    result = await db.execute(
        select(User).options(selectinload(User.followed)).where(User.id == user_id)
    )
    user_obj = result.scalar_one_or_none()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    followed_ids = [u.id for u in user_obj.followed]
    # Добавляем самого пользователя
    followed_ids.append(user_id)
    
    # Запрос постов от подписанных пользователей, отсортированных по дате (новейшие первыми)
    posts_result = await db.execute(
        Post.__table__.select().where(Post.user_id.in_(followed_ids)).order_by(Post.created_at.desc())
    )
    posts = posts_result.fetchall()
    
    feed = [{
        "id": post.id,
        "user_id": post.user_id,
        "image_url": post.image_url,
        "caption": post.caption,
        "created_at": post.created_at.isoformat()
    } for post in posts]
    
    return feed

# Эндпоинт для создания нового поста
@app.post("/posts")
async def create_post(user_id: int, image_url: str, caption: str = "", db: AsyncSession = Depends(get_db)):
    post = Post(user_id=user_id, image_url=image_url, caption=caption, created_at=datetime.datetime.utcnow())
    db.add(post)
    await db.commit()
   # Отправляем изменения в базу, но не коммитим транзакцию
    await db.refresh(post)  
   
    
    # Формируем данные уведомления (их можно расширить по необходимости)
    post_data = {
        "id": post.id,
        "user_id": post.user_id,
        "image_url": post.image_url,
        "caption": post.caption,
        "created_at": post.created_at.isoformat(),
        "type": "post"
    }
    
    # Отправляем уведомление только подписчикам (друзьям) автора поста
    await notify_friends(user_id, post_data, db)

    return {"message": "Пост успешно создан", "post_id": post.id}

# Эндпоинт для добавления комментария к посту
@app.post("/posts/{post_id}/comments")
async def add_comment(post_id: int, user_id: int, text: str, db: AsyncSession = Depends(get_db)):
    # Проверка существования поста
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    comment = Comment(post_id=post_id, user_id=user_id, text=text, created_at=datetime.datetime.utcnow())
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return {"message": "Комментарий добавлен", "comment_id": comment.id}

# Эндпоинт для добавления реакции к посту
@app.post("/posts/{post_id}/reactions")
async def add_reaction(post_id: int, user_id: int, reaction_type: str, db: AsyncSession = Depends(get_db)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    reaction = Reaction(post_id=post_id, user_id=user_id, type=reaction_type, created_at=datetime.datetime.utcnow())
    db.add(reaction)
    await db.commit()
    await db.refresh(reaction)
    return {"message": "Реакция добавлена", "reaction_id": reaction.id}


# Эндпоинт для создания истории
@app.post("/stories")
async def create_story(user_id: int, image_url: str, db: AsyncSession = Depends(get_db)):
    story = Story(
        user_id=user_id,
        image_url=image_url,
        created_at=datetime.datetime.utcnow()
    )
    db.add(story)
    await db.commit()
    # Отправляем изменения в базу, но не коммитим транзакцию
    await db.refresh(story)  
   
    
    # Формируем данные уведомления (их можно расширить по необходимости)
    story_data = {
        "id": story.id,
        "user_id": story.user_id,
        "image_url": story.image_url,
        "created_at": story.created_at.isoformat(),
        "type": "story"
    }
    
    # Отправляем уведомление только подписчикам (друзьям) автора поста
    await notify_friends(user_id, story_data, db)
    return {"message": "История успешно создана", "story_id": story.id}

# Эндпоинт для просмотра историй
@app.get("/stories")
async def get_stories(user_id: int, db: AsyncSession = Depends(get_db)):
    # Выполняем запрос и извлекаем объект пользователя
    result = await db.execute(
        select(User).options(selectinload(User.followed)).where(User.id == user_id)
    )
    user_obj = result.scalar_one_or_none()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Формируем список ID: истории самого пользователя + его друзей (на которых он подписан)
    friend_ids = [friend.id for friend in user_obj.followed]
    friend_ids.append(user_id)
    
    # Запрашиваем истории, сортируем от новых к старым
    result = await db.execute(
        select(Story).where(Story.user_id.in_(friend_ids)).order_by(Story.created_at.desc())
    )
    stories = result.scalars().all()
    
    # Форматируем вывод
    return [
        {
            "id": story.id,
            "user_id": story.user_id,
            "image_url": story.image_url,
            "created_at": story.created_at.isoformat()
        } for story in stories
    ]


# Глобальное хранилище для активных соединений
active_connections = {}

@app.websocket("/ws/feed/{user_id}")
async def feed_websocket(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[int(user_id)] = websocket
    try:
        while True:
            # Здесь можно обрабатывать входящие сообщения от клиента, если нужно.
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.pop(int(user_id), None)
        print(f"WebSocket для пользователя {user_id} отключён")
        

async def notify_friends(author_id: int, post_data: dict, db: AsyncSession):
    # Явно загружаем автора вместе с подписчиками
    result = await db.execute(
        select(User).options(selectinload(User.followers)).where(User.id == author_id)
    )
    author = result.scalar_one_or_none()
    if not author:
        return

    for follower in author.followers:
        ws = active_connections.get(follower.id)
        if ws:
            await ws.send_json(post_data)
            

app.include_router(html_router)