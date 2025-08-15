from sqlalchemy import Column, Integer, String, Text, Numeric, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_admin = Column(Integer, nullable=False, server_default=text("0"))  # tinyint(1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    products = relationship(
        "Product",
        back_populates="category",
        lazy="selectin",          # <- antes "joined"
        cascade="all,delete-orphan"
    )

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    vat_rate = Column(Numeric(5, 2), nullable=False, server_default=text("19.00"))
    stock = Column(Integer, nullable=False, server_default=text("0"))
    size = Column(String(10))       # guardamos texto (XS,S,M,L,XL,XXL o numérico de jeans)
    image_url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    category = relationship("Category", back_populates="products", lazy="selectin")
