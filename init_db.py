import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models import Base  # Файл models.py должен содержать определения моделей и Base

# Замените DATABASE_URL на URL подключения к вашей базе данных
DATABASE_URL = "postgresql+asyncpg://postgres:123321@localhost/inst_feed"

async def init_db():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        print("Удаление существующих таблиц (если есть)...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Создание таблиц...")
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Инициализация базы данных завершена.")

if __name__ == '__main__':
    asyncio.run(init_db())
