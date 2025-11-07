from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, timezone
import os

from models.cart import Cart, CartItem, CartItemAdd, CartUpdateQuantity
from models.activity import ActivityLog, ActivityType

router = APIRouter(prefix="/cart", tags=["cart"])

# Получаем database из server.py через dependency
def get_database():
    from server import db
    return db

@router.get("/{telegram_id}", response_model=Cart)
async def get_cart(telegram_id: str, db = Depends(get_database)):
    """Получить корзину пользователя"""
    cart = await db.carts.find_one({"telegram_id": telegram_id})
    
    if not cart:
        # Создаем пустую корзину если её нет
        new_cart = {
            "telegram_id": telegram_id,
            "items": [],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.carts.insert_one(new_cart)
        return Cart(**new_cart)
    
    # Конвертируем ISO строки обратно в datetime
    if isinstance(cart.get('updated_at'), str):
        cart['updated_at'] = datetime.fromisoformat(cart['updated_at'])
    
    return Cart(**cart)

@router.post("/{telegram_id}/items")
async def add_to_cart(telegram_id: str, item: CartItemAdd, db = Depends(get_database)):
    """Добавить товар в корзину"""
    # Проверяем блокировку пользователя
    user = await db.users.find_one({"telegram_id": telegram_id})
    if user and user.get("is_blocked"):
        raise HTTPException(status_code=403, detail="Слишком много запросов, подождите еще и вернитесь не скоро")
    
    cart = await db.carts.find_one({"telegram_id": telegram_id})
    
    if not cart:
        # Создаем новую корзину
        cart = {
            "telegram_id": telegram_id,
            "items": [],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    # Проверяем есть ли уже этот товар в корзине
    items = cart.get("items", [])
    item_exists = False
    
    for existing_item in items:
        if existing_item["code"] == item.code and existing_item["warehouse_id"] == item.warehouse_id:
            # Обновляем количество
            new_quantity = existing_item["quantity"] + item.quantity
            if new_quantity > item.rest:
                raise HTTPException(status_code=400, detail=f"Недостаточно товара на складе. Доступно: {item.rest}")
            existing_item["quantity"] = new_quantity
            item_exists = True
            break
    
    if not item_exists:
        # Проверяем доступное количество
        if item.quantity > item.rest:
            raise HTTPException(status_code=400, detail=f"Недостаточно товара на складе. Доступно: {item.rest}")
        # Добавляем новый товар
        items.append(item.dict())
    
    # Обновляем корзину
    cart["items"] = items
    cart["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.carts.update_one(
        {"telegram_id": telegram_id},
        {"$set": cart},
        upsert=True
    )
    
    # Логируем активность
    user_display = None
    if user:
        user_display = user.get("username") or user.get("first_name") or f"User_{telegram_id[-4:]}"
    activity = {
        "telegram_id": telegram_id,
        "username": user_display,
        "activity_type": ActivityType.CART_ADD.value,
        "search_params": {"code": item.code, "quantity": item.quantity},
        "result_count": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.activity_logs.insert_one(activity)
    
    return {"message": "Товар добавлен в корзину", "cart_items_count": len(items)}

@router.put("/{telegram_id}/items/{item_code}")
async def update_cart_item(
    telegram_id: str, 
    item_code: str, 
    warehouse_id: int,
    update: CartUpdateQuantity, 
    db = Depends(get_database)
):
    """Обновить количество товара в корзине"""
    # Проверяем блокировку пользователя
    user = await db.users.find_one({"telegram_id": telegram_id})
    if user and user.get("is_blocked"):
        raise HTTPException(status_code=403, detail="Слишком много запросов, подождите еще и вернитесь не скоро")
    
    cart = await db.carts.find_one({"telegram_id": telegram_id})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Корзина не найдена")
    
    items = cart.get("items", [])
    item_found = False
    
    for item in items:
        if item["code"] == item_code and item["warehouse_id"] == warehouse_id:
            if update.quantity > item["rest"]:
                raise HTTPException(status_code=400, detail=f"Недостаточно товара на складе. Доступно: {item['rest']}")
            if update.quantity <= 0:
                raise HTTPException(status_code=400, detail="Количество должно быть больше 0")
            item["quantity"] = update.quantity
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")
    
    # Обновляем корзину
    cart["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.carts.update_one(
        {"telegram_id": telegram_id},
        {"$set": cart}
    )
    
    return {"message": "Количество обновлено"}

@router.delete("/{telegram_id}/items/{item_code}")
async def remove_from_cart(
    telegram_id: str, 
    item_code: str,
    warehouse_id: int,
    db = Depends(get_database)
):
    """Удалить товар из корзины"""
    # Проверяем блокировку пользователя
    user = await db.users.find_one({"telegram_id": telegram_id})
    if user and user.get("is_blocked"):
        raise HTTPException(status_code=403, detail="Слишком много запросов, подождите еще и вернитесь не скоро")
    
    cart = await db.carts.find_one({"telegram_id": telegram_id})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Корзина не найдена")
    
    items = cart.get("items", [])
    items = [item for item in items if not (item["code"] == item_code and item["warehouse_id"] == warehouse_id)]
    
    cart["items"] = items
    cart["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.carts.update_one(
        {"telegram_id": telegram_id},
        {"$set": cart}
    )
    
    # Логируем активность
    activity = {
        "telegram_id": telegram_id,
        "username": user.get("username") if user else None,
        "activity_type": ActivityType.CART_REMOVE.value,
        "search_params": {"code": item_code},
        "result_count": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.activity_logs.insert_one(activity)
    
    return {"message": "Товар удален из корзины", "cart_items_count": len(items)}

@router.delete("/{telegram_id}")
async def clear_cart(telegram_id: str, db = Depends(get_database)):
    """Очистить корзину"""
    # Проверяем блокировку пользователя
    user = await db.users.find_one({"telegram_id": telegram_id})
    if user and user.get("is_blocked"):
        raise HTTPException(status_code=403, detail="Слишком много запросов, подождите еще и вернитесь не скоро")
    
    await db.carts.update_one(
        {"telegram_id": telegram_id},
        {"$set": {
            "items": [],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {"message": "Корзина очищена"}
