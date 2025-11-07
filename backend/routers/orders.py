from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone
import os
import logging

from models.order import (
    Order, OrderCreate, OrderStatus, OrderConfirm, OrderReject
)
from services.fourthchki_client import get_fourthchki_client
from services.telegram_bot import get_telegram_notifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])

def get_db():
    from server import db
    return db

async def get_markup_percentage(db: AsyncIOMotorDatabase) -> float:
    """Получить текущий процент наценки"""
    settings = await db.settings.find_one({}, {"_id": 0})
    if settings:
        return settings.get('markup_percentage', 15.0)
    return float(os.environ.get('DEFAULT_MARKUP_PERCENTAGE', '15'))

@router.post("", response_model=Order)
async def create_order(
    order_data: OrderCreate,
    telegram_id: str = Query(..., description="Telegram ID пользователя"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Создать новый заказ
    Заказ создается со статусом pending_confirmation и ждет подтверждения админа
    """
    try:
        # Получаем пользователя
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем текущий процент наценки
        markup = await get_markup_percentage(db)
        
        # Вычисляем общую сумму
        total_amount = sum(item.price_final * item.quantity for item in order_data.items)
        
        # Создаем заказ
        user_display_name = user.get('username') or user.get('first_name') or telegram_id
        
        order = Order(
            user_telegram_id=telegram_id,
            user_name=user_display_name,
            items=order_data.items,
            total_amount=total_amount,
            markup_percentage=markup,
            delivery_address=order_data.delivery_address,
            status=OrderStatus.PENDING_CONFIRMATION
        )
        
        # Сохраняем в базу
        order_dict = order.model_dump()
        order_dict['created_at'] = order_dict['created_at'].isoformat()
        order_dict['status'] = order_dict['status'].value
        if order_dict.get('confirmed_at'):
            order_dict['confirmed_at'] = order_dict['confirmed_at'].isoformat()
        
        await db.orders.insert_one(order_dict)
        
        logger.info(f"Order created: {order.order_id} by user {telegram_id}")
        
        # Отправляем уведомление админу
        notifier = get_telegram_notifier()
        await notifier.notify_admin_new_order(
            order_id=order.order_id,
            user_name=user_display_name,
            total_amount=total_amount,
            items_count=len(order_data.items)
        )
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/my", response_model=List[Order])
async def get_my_orders(
    telegram_id: str = Query(..., description="Telegram ID пользователя"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить список заказов пользователя
    """
    try:
        orders = await db.orders.find(
            {"user_telegram_id": telegram_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        
        # Конвертируем даты и статусы
        for order in orders:
            if isinstance(order.get('created_at'), str):
                order['created_at'] = datetime.fromisoformat(order['created_at'])
            if isinstance(order.get('confirmed_at'), str):
                order['confirmed_at'] = datetime.fromisoformat(order['confirmed_at'])
            if isinstance(order.get('status'), str):
                order['status'] = OrderStatus(order['status'])
        
        return orders
        
    except Exception as e:
        logger.error(f"Error getting user orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    telegram_id: str = Query(..., description="Telegram ID пользователя"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить детали заказа
    """
    try:
        # Проверяем, является ли пользователь админом
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Если не админ, проверяем что заказ принадлежит пользователю
        query = {"order_id": order_id}
        if not user.get('is_admin'):
            query["user_telegram_id"] = telegram_id
        
        order = await db.orders.find_one(query, {"_id": 0})
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Конвертируем даты и статус
        if isinstance(order.get('created_at'), str):
            order['created_at'] = datetime.fromisoformat(order['created_at'])
        if isinstance(order.get('confirmed_at'), str):
            order['confirmed_at'] = datetime.fromisoformat(order['confirmed_at'])
        if isinstance(order.get('status'), str):
            order['status'] = OrderStatus(order['status'])
        
        return Order(**order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order")

@router.get("/admin/pending", response_model=List[Order])
async def get_pending_orders(
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить список заказов ожидающих подтверждения (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        orders = await db.orders.find(
            {"status": OrderStatus.PENDING_CONFIRMATION.value},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        
        # Конвертируем даты и статусы
        for order in orders:
            if isinstance(order.get('created_at'), str):
                order['created_at'] = datetime.fromisoformat(order['created_at'])
            if isinstance(order.get('confirmed_at'), str):
                order['confirmed_at'] = datetime.fromisoformat(order['confirmed_at'])
            if isinstance(order.get('status'), str):
                order['status'] = OrderStatus(order['status'])
        
        return orders
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pending orders")


@router.get("/admin/all", response_model=List[Order])
async def get_all_orders(
    telegram_id: str = Query(..., description="Telegram ID админа"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Получить список ВСЕХ заказов (только для админа)
    Опционально можно фильтровать по статусу
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Формируем фильтр
        filter_query = {}
        if status:
            filter_query["status"] = status
        
        orders = await db.orders.find(
            filter_query,
            {"_id": 0}
        ).sort("created_at", -1).to_list(1000)
        
        # Конвертируем даты и статусы
        for order in orders:
            if isinstance(order.get('created_at'), str):
                order['created_at'] = datetime.fromisoformat(order['created_at'])
            if isinstance(order.get('confirmed_at'), str):
                order['confirmed_at'] = datetime.fromisoformat(order['confirmed_at'])
            if isinstance(order.get('updated_at'), str):
                order['updated_at'] = datetime.fromisoformat(order['updated_at'])
            if isinstance(order.get('status'), str):
                order['status'] = OrderStatus(order['status'])
        
        return orders
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")


@router.post("/{order_id}/confirm", response_model=Order)
async def confirm_order(
    order_id: str,
    confirm_data: OrderConfirm,
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Подтвердить заказ (только для админа)
    Статус меняется на CONFIRMED для ручной обработки админом
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Получаем заказ
        order = await db.orders.find_one(
            {"order_id": order_id},
            {"_id": 0}
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order['status'] != OrderStatus.PENDING_CONFIRMATION.value:
            raise HTTPException(
                status_code=400, 
                detail=f"Order cannot be confirmed in status: {order['status']}"
            )
        
        # Обновляем заказ - НЕ отправляем поставщику, просто подтверждаем
        now = datetime.now(timezone.utc)
        update_data = {
            'status': OrderStatus.CONFIRMED.value,  # Статус "подтвержден" для ручной обработки
            'confirmed_at': now.isoformat(),
            'confirmed_by_admin': telegram_id
        }
        
        if confirm_data.admin_comment:
            update_data['admin_comment'] = confirm_data.admin_comment
        
        await db.orders.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        
        logger.info(f"Order {order_id} confirmed by admin {telegram_id} for manual processing")
        
        # Отправляем уведомление клиенту
        notifier = get_telegram_notifier()
        await notifier.notify_user_order_confirmed(
            user_telegram_id=order['user_telegram_id'],
            order_id=order_id
        )
        
        # Получаем обновленный заказ
        updated_order = await db.orders.find_one(
            {"order_id": order_id},
            {"_id": 0}
        )
        
        # Конвертируем даты и статус
        if isinstance(updated_order.get('created_at'), str):
            updated_order['created_at'] = datetime.fromisoformat(updated_order['created_at'])
        if isinstance(updated_order.get('confirmed_at'), str):
            updated_order['confirmed_at'] = datetime.fromisoformat(updated_order['confirmed_at'])
        if isinstance(updated_order.get('status'), str):
            updated_order['status'] = OrderStatus(updated_order['status'])
        
        return Order(**updated_order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to confirm order: {str(e)}")

@router.post("/{order_id}/reject", response_model=Order)
async def reject_order(
    order_id: str,
    reject_data: OrderReject,
    telegram_id: str = Query(..., description="Telegram ID админа"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Отклонить заказ (только для админа)
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Получаем заказ
        order = await db.orders.find_one(
            {"order_id": order_id},
            {"_id": 0}
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order['status'] != OrderStatus.PENDING_CONFIRMATION.value:
            raise HTTPException(
                status_code=400, 
                detail=f"Order cannot be rejected in status: {order['status']}"
            )
        
        # Обновляем заказ
        await db.orders.update_one(
            {"order_id": order_id},
            {"$set": {
                'status': OrderStatus.CANCELLED.value,
                'admin_comment': reject_data.reason
            }}
        )
        
        logger.info(f"Order {order_id} rejected by admin")
        
        # Отправляем уведомление клиенту
        notifier = get_telegram_notifier()
        await notifier.notify_user_order_rejected(
            user_telegram_id=order['user_telegram_id'],
            order_id=order_id,
            reason=reject_data.reason
        )
        
        # Получаем обновленный заказ
        updated_order = await db.orders.find_one(
            {"order_id": order_id},
            {"_id": 0}
        )
        
        # Конвертируем даты и статус
        if isinstance(updated_order.get('created_at'), str):
            updated_order['created_at'] = datetime.fromisoformat(updated_order['created_at'])
        if isinstance(updated_order.get('confirmed_at'), str):
            updated_order['confirmed_at'] = datetime.fromisoformat(updated_order['confirmed_at'])
        if isinstance(updated_order.get('status'), str):
            updated_order['status'] = OrderStatus(updated_order['status'])
        
        return Order(**updated_order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting order: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject order")


@router.patch("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: str,
    new_status: OrderStatus,
    telegram_id: str = Query(..., description="Telegram ID админа"),
    comment: Optional[str] = Query(None, description="Комментарий к изменению статуса"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Изменить статус заказа (только для админа)
    Доступные статусы после подтверждения:
    - awaiting_payment: Ожидание оплаты
    - in_progress: В работе
    - delivery: Доставка
    - delayed: Задержка
    - completed: Выполнен
    - cancelled: Отменен
    """
    try:
        # Проверяем, что пользователь админ
        user = await db.users.find_one(
            {"telegram_id": telegram_id},
            {"_id": 0}
        )
        
        if not user or not user.get('is_admin'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Получаем заказ
        order = await db.orders.find_one(
            {"order_id": order_id},
            {"_id": 0}
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Проверяем что заказ можно изменить
        if order['status'] == OrderStatus.PENDING_CONFIRMATION.value:
            raise HTTPException(
                status_code=400,
                detail="Use /confirm or /reject endpoints for pending orders"
            )
        
        # Обновляем статус
        update_data = {
            'status': new_status.value,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        if comment:
            update_data['status_comment'] = comment
        
        await db.orders.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        
        logger.info(f"Order {order_id} status changed to {new_status.value} by admin {telegram_id}")
        
        # Отправляем уведомление клиенту о изменении статуса
        notifier = get_telegram_notifier()
        status_messages = {
            OrderStatus.AWAITING_PAYMENT: "Ожидает оплаты",
            OrderStatus.IN_PROGRESS: "Принят в работу",
            OrderStatus.DELIVERY: "Передан в доставку",
            OrderStatus.DELAYED: "Задержан",
            OrderStatus.COMPLETED: "Выполнен",
            OrderStatus.CANCELLED: "Отменен"
        }
        
        status_text = status_messages.get(new_status, new_status.value)
        await notifier.notify_user_order_status_changed(
            user_telegram_id=order['user_telegram_id'],
            order_id=order_id,
            new_status=status_text,
            comment=comment
        )
        
        # Получаем обновленный заказ
        updated_order = await db.orders.find_one(
            {"order_id": order_id},
            {"_id": 0}
        )
        
        # Конвертируем даты и статус
        if isinstance(updated_order.get('created_at'), str):
            updated_order['created_at'] = datetime.fromisoformat(updated_order['created_at'])
        if isinstance(updated_order.get('confirmed_at'), str):
            updated_order['confirmed_at'] = datetime.fromisoformat(updated_order['confirmed_at'])
        if isinstance(updated_order.get('updated_at'), str):
            updated_order['updated_at'] = datetime.fromisoformat(updated_order['updated_at'])
        if isinstance(updated_order.get('status'), str):
            updated_order['status'] = OrderStatus(updated_order['status'])
        
        return Order(**updated_order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

