from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import os
import logging

from models.user import User, UserCreate
from services.telegram_bot import get_telegram_notifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    from server import db
    return db

@router.post("/telegram", response_model=User)
async def authenticate_telegram_user(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Аутентификация пользователя через Telegram
    Создает нового пользователя если не существует
    """
    try:
        admin_id = os.environ.get('ADMIN_TELEGRAM_ID')
        
        # Проверяем, существует ли пользователь
        existing_user = await db.users.find_one(
            {"telegram_id": user_data.telegram_id},
            {"_id": 0}
        )
        
        if existing_user:
            # Конвертируем timestamp обратно в datetime
            if isinstance(existing_user.get('created_at'), str):
                existing_user['created_at'] = datetime.fromisoformat(existing_user['created_at'])
            return User(**existing_user)
        
        # Создаем нового пользователя
        is_admin = user_data.telegram_id == admin_id
        
        new_user = User(
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_admin=is_admin
        )
        
        # Сохраняем в базу
        user_dict = new_user.model_dump()
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        
        await db.users.insert_one(user_dict)
        
        logger.info(f"New user created: {user_data.telegram_id}, admin: {is_admin}")
        
        return new_user
        
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.get("/me", response_model=User)
async def get_current_user(
    telegram_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Получить информацию о текущем пользователе"""
    try:
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        
        return User(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")
