from pydantic import BaseModel
from datetime import datetime, timezone

class AppSettings(BaseModel):
    markup_percentage: float = 15.0  # Процент наценки по умолчанию
    updated_at: datetime
    updated_by_admin: str
