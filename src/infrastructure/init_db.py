# infrastructure/db/init_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.models import Base
from src.infrastructure.database import DATABASE_URL

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
