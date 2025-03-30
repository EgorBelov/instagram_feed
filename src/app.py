# app/main.py
import sys

from sqlalchemy import select
from sqlalchemy.orm import selectinload
sys.path.append("E:/HSE_HERNYA/python_4_course/instagram_feed/")
from src.infrastructure.repositories import NotificationRepository
from src.models.models import User
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
import os
from src.application import services, dto
from src.infrastructure.database import get_db
from src.util.logger import logger

app = FastAPI()

# Роутер для отдачи HTML-файла
@app.get("/", response_class=HTMLResponse)
async def get_index():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "E:\\HSE_HERNYA\\python_4_course\\instagram_feed\\src\\templates", "index.html")
    return FileResponse(index_path)

# Пример эндпоинта для создания поста (принимает DTO и возвращает DTO)
@app.post("/posts")
async def create_post_endpoint(user_id: int, image_url: str, caption: str = "", db=Depends(get_db)):
    # Формируем DTO-команду для создания поста
    command = dto.CreatePostDTO(user_id=user_id, image_url=image_url, caption=caption)
    try:
        result = await services.create_post(command, db)
    except Exception as e:
        logger.error(f"Ошибка создания поста: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания поста")
    return result

# Эндпоинт для получения ленты
@app.get("/feed")
async def get_feed_endpoint(user_id: int, db=Depends(get_db)):
    try:
        feed = await services.get_feed(user_id, db)
    except Exception as e:
        logger.error(f"Ошибка получения ленты: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения ленты")
    return feed

# Эндпоинты для историй аналогичным образом...
@app.post("/stories")
async def create_story_endpoint(user_id: int, image_url: str, db=Depends(get_db)):
    command = dto.CreateStoryDTO(user_id=user_id, image_url=image_url)
    try:
        result = await services.create_story(command, db)
    except Exception as e:
        logger.error(f"Ошибка создания истории: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания истории")
    
    return result

@app.get("/stories")
async def get_stories_endpoint(user_id: int, db=Depends(get_db)):
    try:
        stories = await services.get_stories(user_id, db)
    except Exception as e:
        logger.error(f"Ошибка получения историй: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения историй")
    return stories



@app.websocket("/ws/feed/{user_id}")
async def feed_websocket(websocket: WebSocket, user_id: int):
    await websocket.accept()
    services.active_connections[int(user_id)] = websocket
    try:
        while True:
            # Здесь можно обрабатывать входящие сообщения от клиента, если нужно.
            await websocket.receive_text()
    except WebSocketDisconnect:
        services.active_connections.pop(int(user_id), None)
        logger.info(f"WebSocket для пользователя {user_id} отключён")

