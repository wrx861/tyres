from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class CartItem(BaseModel):
    code: str  # Код товара SAE
    name: str
    brand: str
    model: Optional[str] = None
    quantity: int
    price: float
    warehouse_id: int
    warehouse_name: str
    rest: int  # Доступное количество на складе
    img_small: Optional[str] = None
    # Дополнительные поля для шин
    width: Optional[int] = None
    height: Optional[int] = None
    diameter: Optional[int] = None
    season: Optional[str] = None
    # Дополнительные поля для дисков
    disk_type: Optional[str] = None
    color: Optional[str] = None

class Cart(BaseModel):
    telegram_id: str
    items: List[CartItem] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItemAdd(BaseModel):
    code: str
    name: str
    brand: str
    model: Optional[str] = None
    quantity: int
    price: float
    warehouse_id: int
    warehouse_name: str
    rest: int
    img_small: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    diameter: Optional[int] = None
    season: Optional[str] = None
    disk_type: Optional[str] = None
    color: Optional[str] = None

class CartUpdateQuantity(BaseModel):
    quantity: int
