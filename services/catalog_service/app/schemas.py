from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from typing import Optional

# ---- Usuarios (para /me si lo usas aquí en futuro)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool
    class Config:
        from_attributes = True

# ---- Categorías
class CategoryIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class CategoryOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

# ---- Productos
class ProductIn(BaseModel):
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: Decimal
    vat_rate: Decimal = Decimal("19.00")
    stock: int = 0
    size: Optional[str] = None
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None
    stock: Optional[int] = None
    size: Optional[str] = None
    image_url: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    category_id: Optional[int]
    name: str
    description: Optional[str]
    price: Decimal
    vat_rate: Decimal
    stock: int
    size: Optional[str]
    image_url: Optional[str]
    class Config:
        from_attributes = True
