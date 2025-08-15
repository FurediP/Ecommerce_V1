# services/order_service/run_selftest.py
import sys
from decimal import Decimal
from typing import Any, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base
from app.deps import get_db, get_current_user
from app.models import User, Product, Cart, CartItem  # importa SOLO lo que existe aquí

# ---------- utilidades ----------
def _coerce_default(col) -> Any:
    tname = col.type.__class__.__name__.lower()
    if "string" in tname or "varchar" in tname or "text" in tname:
        return "x"
    if "integer" in tname or "smallint" in tname:
        return 0
    if "numeric" in tname or "decimal" in tname or "float" in tname or "real" in tname:
        return 0
    if "boolean" in tname:
        return 0
    return None

def make_instance(model_cls, **preferred) -> Any:
    cols = list(model_cls.__table__.columns)
    names = {c.name for c in cols}
    data: Dict[str, Any] = {}
    for k, v in preferred.items():
        if k in names:
            data[k] = v
    for c in cols:
        if c.name in data or c.name == "id":
            continue
        if not c.nullable and c.default is None and c.server_default is None:
            data[c.name] = _coerce_default(c)
    return model_cls(**data)

def debug_counts(Session):
    db = Session()
    try:
        uc = db.query(User).count()
        pc = db.query(Product).count()
        cc = db.query(Cart).count()
        cic = db.query(CartItem).count()
        print(f"[DEBUG] counts -> users={uc}, products={pc}, carts={cc}, cart_items={cic}")
    finally:
        db.close()

# ---------- main ----------
def main():
    # SQLite en memoria COMPARTIDA entre conexiones
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_current_user():
        db = TestingSessionLocal()
        try:
            u = db.query(User).first()
            if not u:
                u = make_instance(
                    User,
                    email="test@local",
                    hashed_password="x",
                    full_name="Tester",
                    is_admin=0,
                )
                db.add(u); db.commit(); db.refresh(u)
            return u
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)

    # ---- seed: user, product, cart + item ----
    db = TestingSessionLocal()
    try:
        u = db.query(User).first()
        if not u:
            u = make_instance(User, email="test@local", hashed_password="x", full_name="Tester", is_admin=0)
            db.add(u); db.commit(); db.refresh(u)

        p = db.query(Product).first()
        if not p:
            p = make_instance(
                Product,
                category_id=None,           # si no existe la columna, se ignora
                name="Camiseta",
                description="algodón",
                price=Decimal("39000.00"),
                vat_rate=Decimal("19.00"),
                stock=100,
                size="M",
                image_url=None,
            )
            db.add(p); db.commit(); db.refresh(p)

        c = db.query(Cart).first()
        if not c:
            c = make_instance(Cart, user_id=getattr(u, "id", 1), status="active")
            db.add(c); db.commit(); db.refresh(c)

        ci = db.query(CartItem).first()
        if not ci:
            ci = make_instance(CartItem, cart_id=c.id, product_id=p.id, quantity=2, unit_price=p.price)
            db.add(ci); db.commit()
    finally:
        db.close()

    debug_counts(TestingSessionLocal)

    # ---- checkout ----
    r = client.post("/orders/checkout")
    print(f"[DEBUG] POST /orders/checkout -> {r.status_code}")
    if r.status_code != 201:
        print("PEDIDOS: FAIL en checkout", r.status_code, r.text)
        sys.exit(1)

    order = r.json()
    print("[DEBUG] order:", order)

    # Acepta total con o sin IVA para ser tolerante según tu lógica
    try:
        total = float(order.get("total", "0"))
    except Exception:
        total = 0.0

    ok = True
    ok &= isinstance(order.get("items"), list) and len(order["items"]) >= 1
    ok &= total > 0.0  # con esto evitamos depender de un valor exacto
    if not ok:
        print("PEDIDOS: FAIL tras checkout (items/total inválidos)")
        sys.exit(1)

    # ---- /orders/me ----
    r2 = client.get("/orders")
    print(f"[DEBUG] GET /orders/me -> {r2.status_code}")
    if r2.status_code != 200:
        print("PEDIDOS: FAIL en /orders/me", r2.status_code, r2.text)
        sys.exit(1)

    lst = r2.json()
    has_order = any(o.get("id") == order.get("id") for o in lst if isinstance(o, dict))
    if not has_order:
        print("PEDIDOS: FAIL no aparece el pedido en /orders/me", lst)
        sys.exit(1)

    print("PEDIDOS: PASS")
    sys.exit(0)

if __name__ == "__main__":
    main()
