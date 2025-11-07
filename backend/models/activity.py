from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class ActivityType(str, Enum):
    TIRE_SEARCH = "tire_search"
    DISK_SEARCH = "disk_search"
    CAR_SELECTION = "car_selection"
    ORDER_CREATED = "order_created"
    CART_ADD = "cart_add"
    CART_REMOVE = "cart_remove"

class ActivityLog(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    activity_type: ActivityType
    search_params: Optional[Dict[str, Any]] = None
    result_count: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class ActivityLogCreate(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    activity_type: ActivityType
    search_params: Optional[Dict[str, Any]] = None
    result_count: Optional[int] = None
