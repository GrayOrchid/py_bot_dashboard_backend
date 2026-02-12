import secrets
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
import httpx
from dotenv import load_dotenv
import os
from sqlalchemy import Column, Integer, String, Boolean
import logging
from sqlalchemy.ext.declarative import declarative_base
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

router = APIRouter(prefix="/auth", tags=["Discord Auth"])


DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI") or "http://localhost:8000/auth/callback"
DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"

states: Dict[str, bool] = {}  # In-memory для state (замени на Redis если нужно)

Base = declarative_base()

# Правильная модель
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String(50), unique=True, nullable=True, index=True)
    discord_username = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<User discord_id={self.discord_id}>"
# Зависимость для текущего пользователя (из сессии)
async def get_current_user(request: Request):
    access_token = request.session.get("discord_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = await client.get(DISCORD_USER_URL, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        return resp.json()

@router.get("/login")
async def login_discord(request: Request):
    state = secrets.token_hex(16)
    states[state] = True
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify",
        "state": state
    }
    auth_url = f"{DISCORD_AUTH_URL}?{httpx.URL(params=params).query.decode()}"
    return RedirectResponse(auth_url)

@router.get("/callback")
async def discord_callback(code: str, state: str, request: Request):
    """
    Callback от Discord после авторизации.
    Обменивает code на токен, получает данные пользователя и связывает аккаунт.
    """
    # 1. Проверка state (защита от CSRF)
    if state not in states:
        logger.warning(f"Invalid state received: {state}. Expected states: {list(states.keys())}")
        raise HTTPException(
            status_code=400,
            detail="Неверный state. Возможно, сессия устарела или произошёл перезапуск сервера."
        )

    # Удаляем использованный state
    del states[state]
    logger.info(f"State validated and removed: {state}")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # 2. Обмен code на access_token
            token_data = {
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": DISCORD_REDIRECT_URI,
            }

            logger.info("Отправка запроса на получение токена...")
            token_resp = await client.post(DISCORD_TOKEN_URL, data=token_data)

            if token_resp.status_code != 200:
                error_text = token_resp.text
                logger.error(f"Ошибка обмена code на token: {token_resp.status_code} - {error_text}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Не удалось получить токен от Discord: {error_text}"
                )

            token_json = token_resp.json()
            access_token = token_json.get("access_token")

            if not access_token:
                raise HTTPException(500, detail="Токен не получен в ответе Discord")

            # 3. Получение информации о пользователе
            headers = {"Authorization": f"Bearer {access_token}"}
            user_resp = await client.get(DISCORD_USER_URL, headers=headers)

            if user_resp.status_code != 200:
                error_text = user_resp.text
                logger.error(f"Ошибка получения данных пользователя: {user_resp.status_code} - {error_text}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Не удалось получить данные пользователя: {error_text}"
                )

            user = user_resp.json()

            # Обработка username (Discord изменил систему имён)
            # В новых аккаунтах discriminator часто отсутствует, лучше использовать global_name
            discord_id = user["id"]
            discord_username = user.get("global_name") or user["username"]
            if "discriminator" in user and user["discriminator"] != "0":
                discord_username += "#" + user["discriminator"]

            logger.info(f"Успешно авторизован Discord пользователь: {discord_username} ({discord_id})")

            # 4. Работа с базой данных
            from database import SessionLocal
            db = SessionLocal()
            try:
                # Ищем существующего пользователя по discord_id
                system_user = db.query(User).filter(User.discord_id == discord_id).first()

                if system_user:
                    # Обновляем никнейм (на случай изменения)
                    if system_user.discord_username != discord_username:
                        system_user.discord_username = discord_username
                        logger.info(f"Обновлён никнейм для пользователя {discord_id}")
                else:
                    # Создаём нового пользователя
                    system_user = User(
                        discord_id=discord_id,
                        discord_username=discord_username,
                        # username=...,  # можно сгенерировать случайный или оставить None
                        # email=None,
                        # is_active=True,
                    )
                    db.add(system_user)
                    logger.info(f"Создан новый пользователь с Discord ID {discord_id}")

                db.commit()
                db.refresh(system_user)

                # Сохраняем ID пользователя в сессию (удобно для дальнейшей авторизации)
                request.session["user_id"] = system_user.id

            except Exception as db_error:
                db.rollback()
                logger.exception("Ошибка при работе с базой данных в callback")
                raise HTTPException(500, detail="Ошибка сохранения пользователя в базу данных")

            finally:
                db.close()

            # 5. Сохраняем access_token в сессию
            request.session["discord_token"] = access_token
            # Опционально: request.session["discord_refresh_token"] = token_json.get("refresh_token")

            logger.info("Авторизация завершена успешно, редирект на главную")

            # 6. Редирект на главную страницу / дашборд
            return RedirectResponse(url="/", status_code=303)

    except httpx.TimeoutException:
        logger.error("Таймаут при запросе к Discord API")
        raise HTTPException(504, detail="Таймаут соединения с Discord")

    except httpx.RequestError as e:
        logger.error(f"Ошибка сети при обращении к Discord: {str(e)}")
        raise HTTPException(502, detail="Проблема с сетевым соединением к Discord")

    except Exception as e:
        logger.exception("Неожиданная ошибка в discord_callback")
        raise HTTPException(500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.get("/linked-accounts/{user_id}")
async def get_linked_accounts(user_id: str, user: Dict = Depends(get_current_user)):
    # Пример: получи из БД
    from database import SessionLocal
    db = SessionLocal()
    system_user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if system_user and system_user.discord_id:
        return {"discord_id": system_user.discord_id, "discord_username": system_user.discord_username}
    raise HTTPException(status_code=404, detail="No linked accounts")

@router.get("get_all_linked_accounts")
async def get_all_linked_accounts():
    from database import SessionLocal
    db = SessionLocal()
    return db.query(User).all()
