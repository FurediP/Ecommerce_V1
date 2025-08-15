from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from decimal import Decimal

from .database import Base, engine
from .models import Cart, CartItem, Product, Order, OrderItem, User
from .schemas import OrderOut, OrderItemOut, UpdateStatusIn
from .deps import get_db, get_current_user, require_admin
from .config import settings

app = FastAPI(title="Order Service")
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- Helpers ----------
def _get_active_cart(db: Session, user: User) -> Cart | None:
    return (
        db.execute(
            select(Cart)
            .where(Cart.user_id == user.id, Cart.status == "active")
            .order_by(desc(Cart.id))
        )
        .unique().scalars().first()
    )

def _create_order_from_cart(db: Session, user: User) -> Order:
    cart = _get_active_cart(db, user)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Carrito vacío")

    total_net = Decimal("0.00")
    total_vat = Decimal("0.00")

    order = Order(user_id=user.id, status="created", total=Decimal("0.00"))
    db.add(order)
    db.flush()  # tener order.id

    for it in cart.items:
        vat_rate = Decimal(it.product.vat_rate if it.product and it.product.vat_rate is not None else "19.00")
        unit_price = Decimal(it.unit_price)
        qty = Decimal(it.quantity)
        total_net += unit_price * qty
        total_vat += (unit_price * (vat_rate/Decimal("100"))) * qty

        oi = OrderItem(
            order_id=order.id,
            product_id=it.product_id,
            quantity=int(qty),
            unit_price=unit_price,
            vat_rate=vat_rate
        )
        db.add(oi)

    order.total = total_net + total_vat

    # marcar carrito como convertido
    cart.status = "converted"
    db.commit()
    db.refresh(order)
    return order

def _order_to_out(db: Session, order: Order) -> OrderOut:
    # anexar nombre de producto para comodidad
    items_out = []
    for oi in order.items:
        items_out.append(OrderItemOut(
            id=oi.id,
            product_id=oi.product_id,
            quantity=oi.quantity,
            unit_price=oi.unit_price,
            vat_rate=oi.vat_rate,
            product_name=oi.product.name if oi.product else None
        ))
    return OrderOut(id=order.id, user_id=order.user_id, total=order.total, status=order.status, items=items_out)

# ---------- Endpoints ----------
@app.post("/orders/checkout", response_model=OrderOut, status_code=201)
def checkout(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = _create_order_from_cart(db, user)
    return _order_to_out(db, order)

@app.get("/orders", response_model=list[OrderOut])
def my_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.execute(
            select(Order)
            .where(Order.user_id == user.id)
            .order_by(desc(Order.id))
        )
        .unique().scalars().all()
    )
    return [_order_to_out(db, o) for o in rows]

@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.user_id != user.id:
        # permitir luego a admin; por ahora restringimos al dueño
        raise HTTPException(status_code=403, detail="No autorizado")
    return _order_to_out(db, order)

# ---- Endpoints admin (si quieres permitirlos, protege con require_admin) ----
@app.get("/admin/orders", response_model=list[OrderOut])
def list_all_orders(
    status_filter: str | None = Query(None, description="created|paid|shipped|delivered|cancelled"),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_user)  # cambia a require_admin cuando tengas flag
):
    stmt = select(Order).order_by(desc(Order.id))
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    rows = db.execute(stmt).unique().scalars().all()
    return [_order_to_out(db, o) for o in rows]

@app.put("/admin/orders/{order_id}/status", response_model=OrderOut)
def update_status(order_id: int, payload: UpdateStatusIn, db: Session = Depends(get_db), _admin: User = Depends(get_current_user)):
    allowed = {"created", "paid", "shipped", "delivered", "cancelled"}
    if payload.status not in allowed:
        raise HTTPException(status_code=400, detail=f"status inválido ({allowed})")
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return _order_to_out(db, order)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=settings.ORDER_PORT, reload=True)
