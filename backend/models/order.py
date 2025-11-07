from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum

class OrderStatus(str, Enum):
    PENDING_CONFIRMATION = "pending_confirmation"  # Ждет подтверждения админа
    CONFIRMED = "confirmed"  # Подтвержден админом (в обработке)
    AWAITING_PAYMENT = "awaiting_payment"  # Ожидание оплаты
    IN_PROGRESS = "in_progress"  # В работе (заказан у поставщика)
    DELIVERY = "delivery"  # Доставка
    DELAYED = "delayed"  # Задержка
    COMPLETED = "completed"  # Выполнен
    CANCELLED = "cancelled"  # Отменен

class OrderItem(BaseModel):
    code: str  # Код товара SAE
    name: str
    brand: str
    quantity: int
    price_base: float  # Базовая цена от поставщика
    price_final: float  # Цена с наценкой для клиента
    warehouse_id: int
    warehouse_name: str

class DeliveryAddress(BaseModel):
    city: str
    street: str
    house: str
    apartment: Optional[str] = None
    phone: str  # Телефон клиента (обязательно)
    comment: Optional[str] = None

class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    user_telegram_id: str
    user_name: Optional[str] = None
    items: List[OrderItem]
    total_amount: float
    markup_percentage: float  # Процент наценки на момент заказа
    status: OrderStatus = OrderStatus.PENDING_CONFIRMATION
    delivery_address: Optional[DeliveryAddress] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confirmed_at: Optional[datetime] = None
    confirmed_by_admin: Optional[str] = None
    fourthchki_order_id: Optional[str] = None  # ID заказа в системе 4tochki
    fourthchki_order_number: Optional[str] = None  # Номер заказа от 4tochki
    admin_comment: Optional[str] = None

class OrderCreate(BaseModel):
    items: List[OrderItem]
    delivery_address: DeliveryAddress

class OrderConfirm(BaseModel):
    admin_comment: Optional[str] = None

class OrderReject(BaseModel):
    reason: str
