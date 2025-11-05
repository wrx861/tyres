from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    from server import db
    return db

class MarkupUpdate(BaseModel):
    markup_percentage: float

class MarkupResponse(BaseModel):
    markup_percentage: float
    updated_at: str
    updated_by_admin: str

@router.get("/markup", response_model=MarkupResponse)
async def get_markup(
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить текущий процент наценки (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        settings = await db.settings.find_one({}, {"_id": 0})
        
        if not settings:
            # Создаем настройки по умолчанию
            default_settings = {
                'markup_percentage': 15.0,
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'updated_by_admin': telegram_id
            }
            await db.settings.insert_one(default_settings)
            return MarkupResponse(**default_settings)
        
        return MarkupResponse(**settings)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting markup: {e}")
        raise HTTPException(status_code=500, detail="Failed to get markup")

@router.put("/markup", response_model=MarkupResponse)
async def update_markup(
    markup_data: MarkupUpdate,
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Изменить процент наценки (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Валидация
        if markup_data.markup_percentage < 0 or markup_data.markup_percentage > 100:
            raise HTTPException(
                status_code=400, 
                detail="Markup percentage must be between 0 and 100"
            )
        
        new_settings = {
            'markup_percentage': markup_data.markup_percentage,
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'updated_by_admin': telegram_id
        }
        
        # Обновляем или создаем настройки
        await db.settings.update_one(
            {},
            {"$set": new_settings},
            upsert=True
        )
        
        logger.info(
            f"Markup updated to {markup_data.markup_percentage}% by {telegram_id}"
        )
        
        return MarkupResponse(**new_settings)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating markup: {e}")
        raise HTTPException(status_code=500, detail="Failed to update markup")

@router.get("/stats")
async def get_admin_stats(
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить статистику для админа
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Подсчитываем статистику
        total_orders = await db.orders.count_documents({})
        pending_orders = await db.orders.count_documents(
            {"status": "pending_confirmation"}
        )
        confirmed_orders = await db.orders.count_documents(
            {"status": "sent_to_supplier"}
        )
        completed_orders = await db.orders.count_documents(
            {"status": "completed"}
        )
        cancelled_orders = await db.orders.count_documents(
            {"status": "cancelled"}
        )
        total_users = await db.users.count_documents({})
        
        # Подсчитываем общую сумму заказов
        pipeline = [
            {"$match": {"status": {"$ne": "cancelled"}}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        result = await db.orders.aggregate(pipeline).to_list(1)
        total_revenue = result[0]['total'] if result else 0
        
        return {
            "success": True,
            "stats": {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "confirmed_orders": confirmed_orders,
                "completed_orders": completed_orders,
                "cancelled_orders": cancelled_orders,
                "total_users": total_users,
                "total_revenue": round(total_revenue, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")
