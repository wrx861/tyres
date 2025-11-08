from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import List, Optional
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

# Новые модели для гибкой наценки
class MarkupTier(BaseModel):
    min_price: float
    max_price: float
    markup_percentage: float
    label: str  # Название диапазона (например, "Бюджетные")

class MarkupSettingsUpdate(BaseModel):
    type: str  # "fixed" или "tiered"
    markup_percentage: Optional[float] = None  # Для fixed
    tiers: Optional[List[MarkupTier]] = None  # Для tiered

class MarkupSettingsResponse(BaseModel):
    type: str
    markup_percentage: Optional[float] = None
    tiers: Optional[List[MarkupTier]] = None
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

@router.get("/users")
async def get_all_users(
    telegram_id: str = Query(..., description="Telegram ID админа"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить список всех пользователей (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one({"telegram_id": telegram_id})
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Получаем пользователей
        users_cursor = db.users.find({}, {"_id": 0}).skip(skip).limit(limit).sort("created_at", -1)
        users = await users_cursor.to_list(length=limit)
        
        # Конвертируем даты из ISO строк
        for u in users:
            if isinstance(u.get('created_at'), str):
                u['created_at'] = u['created_at']
            if isinstance(u.get('last_activity'), str):
                u['last_activity'] = u['last_activity']
        
        total_count = await db.users.count_documents({})
        
        return {
            "success": True,
            "users": users,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@router.post("/users/{user_telegram_id}/block")
async def block_user(
    user_telegram_id: str,
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Заблокировать пользователя (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        admin = await db.users.find_one({"telegram_id": telegram_id})
        
        if not admin or not admin.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Проверяем что пользователь существует
        target_user = await db.users.find_one({"telegram_id": user_telegram_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Нельзя заблокировать админа
        if target_user.get('is_admin'):
            raise HTTPException(status_code=400, detail="Cannot block admin user")
        
        # Блокируем пользователя
        await db.users.update_one(
            {"telegram_id": user_telegram_id},
            {"$set": {"is_blocked": True}}
        )
        
        logger.info(f"User {user_telegram_id} blocked by admin {telegram_id}")
        
        return {"success": True, "message": "Пользователь заблокирован"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error blocking user: {e}")
        raise HTTPException(status_code=500, detail="Failed to block user")

@router.post("/users/{user_telegram_id}/unblock")
async def unblock_user(
    user_telegram_id: str,
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Разблокировать пользователя (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        admin = await db.users.find_one({"telegram_id": telegram_id})
        
        if not admin or not admin.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Проверяем что пользователь существует
        target_user = await db.users.find_one({"telegram_id": user_telegram_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Разблокируем пользователя
        await db.users.update_one(
            {"telegram_id": user_telegram_id},
            {"$set": {"is_blocked": False}}
        )
        
        logger.info(f"User {user_telegram_id} unblocked by admin {telegram_id}")
        
        return {"success": True, "message": "Пользователь разблокирован"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unblocking user: {e}")
        raise HTTPException(status_code=500, detail="Failed to unblock user")

@router.get("/activity")
async def get_user_activity(
    telegram_id: str = Query(..., description="Telegram ID админа"),
    user_telegram_id: Optional[str] = Query(None, description="Telegram ID пользователя для фильтра"),
    activity_type: Optional[str] = Query(None, description="Тип активности для фильтра"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить логи активности пользователей (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one({"telegram_id": telegram_id})
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Формируем фильтр
        filter_query = {}
        if user_telegram_id:
            filter_query["telegram_id"] = user_telegram_id
        if activity_type:
            filter_query["activity_type"] = activity_type
        
        # Получаем логи активности
        logs_cursor = db.activity_logs.find(filter_query, {"_id": 0}).skip(skip).limit(limit).sort("timestamp", -1)
        logs = await logs_cursor.to_list(length=limit)
        
        # Конвертируем даты
        for log in logs:
            if isinstance(log.get('timestamp'), str):
                log['timestamp'] = log['timestamp']
        
        total_count = await db.activity_logs.count_documents(filter_query)
        
        return {
            "success": True,
            "logs": logs,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting activity logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get activity logs")

@router.delete("/activity/reset")
async def reset_activity_logs(
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Сбросить всю активность (удалить все логи активности) - только для админа
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one({"telegram_id": telegram_id})
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Удаляем все логи активности
        result = await db.activity_logs.delete_many({})
        
        logger.info(f"Activity logs reset by admin {telegram_id}. Deleted {result.deleted_count} logs")
        
        return {
            "success": True,
            "message": f"Удалено {result.deleted_count} записей активности",
            "deleted_count": result.deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting activity logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset activity logs")

@router.delete("/stats/reset")
async def reset_statistics(
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Сбросить всю статистику (удалить все заказы и активность) - только для админа
    ВНИМАНИЕ: Это удалит ВСЕ заказы из базы данных!
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one({"telegram_id": telegram_id})
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Удаляем все заказы
        orders_result = await db.orders.delete_many({})
        
        # Удаляем все логи активности
        activity_result = await db.activity_logs.delete_many({})
        
        # Сбрасываем last_activity у всех пользователей
        await db.users.update_many({}, {"$set": {"last_activity": None}})
        
        logger.warning(
            f"STATISTICS RESET by admin {telegram_id}. "
            f"Deleted {orders_result.deleted_count} orders, "
            f"Deleted {activity_result.deleted_count} activity logs"
        )
        
        return {
            "success": True,
            "message": "Вся статистика сброшена",
            "deleted_orders": orders_result.deleted_count,
            "deleted_activity_logs": activity_result.deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset statistics")


class SendMessageRequest(BaseModel):
    client_telegram_id: str
    message_text: str


@router.post("/send-message")
async def send_message_to_client(
    message_data: SendMessageRequest,
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Отправить сообщение клиенту через Telegram бота (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one({"telegram_id": telegram_id})
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Проверяем что клиент существует
        client = await db.users.find_one({"telegram_id": message_data.client_telegram_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Отправляем сообщение через бота
        from services.telegram_bot import get_telegram_notifier
        notifier = get_telegram_notifier()
        
        success = await notifier.send_admin_message_to_client(
            client_telegram_id=message_data.client_telegram_id,
            message_text=message_data.message_text,
            admin_name="Администратор"
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send message")
        
        logger.info(f"Admin {telegram_id} sent message to client {message_data.client_telegram_id}")
        
        return {
            "success": True,
            "message": "Сообщение отправлено клиенту"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message to client: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

