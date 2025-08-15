from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal
from sqlalchemy import select, desc
from .database import Base, engine
from .models import Cart, CartItem, Product, User
from .schemas import CartItemCreate, CartItemUpdate, CartOut, CartItemOut, CartTotals
from .deps import get_db, get_current_user
from .config import settings

app = FastAPI(title="Cart Service")
from fastapi.middleware.cors import CORSMiddleware

# incluye AMBOS orígenes: localhost y 127.0.0.1 (Vite suele usar localhost)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # ⚠️ no uses "*" si allow_credentials=True
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Solo dev: no crea tablas nuevas si ya existen
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

# Helpers -------------------------------------------------
def _ensure_active_cart(db: Session, user: User) -> Cart:
    # toma el último carrito 'active' si hubiera más de uno
    cart = (
        db.execute(
            select(Cart)
            .where(Cart.user_id == user.id, Cart.status == "active")
            .order_by(desc(Cart.id))
        )
        .unique()          # 👈 clave para evitar el error de filas duplicadas
        .scalars()
        .first()
    )
    if not cart:
        cart = Cart(user_id=user.id, status="active")
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def _calc_totals(cart: Cart) -> CartTotals:
    total_net = Decimal("0.00")
    total_vat = Decimal("0.00")
    for it in cart.items:
        price = Decimal(it.unit_price)
        vat_rate = Decimal(it.product.vat_rate if it.product and it.product.vat_rate is not None else "19.00")
        qty = Decimal(it.quantity)
        line_net = price * qty
        line_vat = (price * (vat_rate / Decimal("100"))) * qty
        total_net += line_net
        total_vat += line_vat
    total_gross = total_net + total_vat
    return CartTotals(total_net=total_net, total_vat=total_vat, total_gross=total_gross)

def _item_to_out(it: CartItem) -> CartItemOut:
    price = Decimal(it.unit_price)
    vat_rate = Decimal(it.product.vat_rate if it.product and it.product.vat_rate is not None else "19.00")
    qty = Decimal(it.quantity)
    line_net = price * qty
    line_vat = (price * (vat_rate / Decimal("100"))) * qty
    line_gross = line_net + line_vat
    return CartItemOut(
        id=it.id,
        product_id=it.product_id,
        quantity=it.quantity,
        unit_price=price,
        line_net=line_net,
        line_vat=line_vat,
        line_gross=line_gross,
        product=it.product,  # Pydantic usa from_attributes
    )

def _cart_to_out(cart: Cart) -> CartOut:
    items = [_item_to_out(i) for i in cart.items]
    totals = _calc_totals(cart)
    return CartOut(id=cart.id, status=cart.status, items=items, totals=totals)

# Endpoints ------------------------------------------------
@app.get("/cart", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _ensure_active_cart(db, user)
    db.refresh(cart)
    return _cart_to_out(cart)

@app.post("/cart/items", response_model=CartOut, status_code=201)
def add_item(payload: CartItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _ensure_active_cart(db, user)
    prod = db.get(Product, payload.product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # ¿ya existe el producto en el carrito?
    existing = next((i for i in cart.items if i.product_id == prod.id), None)
    if existing:
        existing.quantity = existing.quantity + max(1, payload.quantity)
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=prod.id,
            quantity=max(1, payload.quantity),
            unit_price=prod.price,  # se guarda el precio actual
        )
        db.add(item)
    db.commit()
    db.refresh(cart)
    return _cart_to_out(cart)

@app.put("/cart/items/{item_id}", response_model=CartOut)
def update_item(item_id: int, payload: CartItemUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _ensure_active_cart(db, user)
    item = db.get(CartItem, item_id)
    if not item or item.cart_id != cart.id:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    if payload.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = payload.quantity
    db.commit()
    db.refresh(cart)
    return _cart_to_out(cart)

@app.delete("/cart/items/{item_id}", response_model=CartOut)
def delete_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _ensure_active_cart(db, user)
    item = db.get(CartItem, item_id)
    if not item or item.cart_id != cart.id:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    db.delete(item)
    db.commit()
    db.refresh(cart)
    return _cart_to_out(cart)

@app.delete("/cart/items", response_model=CartOut)
def clear_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _ensure_active_cart(db, user)
    for it in list(cart.items):
        db.delete(it)
    db.commit()
    db.refresh(cart)
    return _cart_to_out(cart)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=settings.CART_PORT, reload=True)
