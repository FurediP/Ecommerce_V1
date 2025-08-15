from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=9999)

class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=0, le=9999)  # 0 = eliminar
    
class ProductMini(BaseModel):
    id: int
    name: str
    price: Decimal
    vat_rate: Decimal
    size: Optional[str] = None
    image_url: Optional[str] = None
    class Config:
        from_attributes = True

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_net: Decimal
    line_vat: Decimal
    line_gross: Decimal
    product: ProductMini
    class Config:
        from_attributes = True

class CartTotals(BaseModel):
    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal

class CartOut(BaseModel):
    id: int
    status: str
    items: List[CartItemOut]
    totals: CartTotals
    class Config:
        from_attributes = True
