from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    vat_rate: Decimal
    product_name: Optional[str] = None
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    total: Decimal
    status: str
    items: List[OrderItemOut]
    class Config:
        from_attributes = True

class UpdateStatusIn(BaseModel):
    status: str  # created, paid, shipped, delivered, cancelled
