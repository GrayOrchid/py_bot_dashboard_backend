from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from database import Base, engine
from routes import main_api_router
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Mini String API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Разрешить любой сайт
    allow_credentials=False,
    allow_methods=["*"], # Разрешить GET, POST, OPTIONS и т.д.
    allow_headers=["*"], # Разрешить любые заголовки
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "h256")
)

# 4. Подключаем роутеры и БД
Base.metadata.create_all(bind=engine)
app.include_router(main_api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Дашборд. Авторизация через Discord прошла успешно."}