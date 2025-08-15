# services/cart_service/run_selftest.py
import sys
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base
from app.deps import get_db, get_current_user
from app.models import User, Category, Product

def main():
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
                u = User(email="test@local", hashed_password="x", full_name="Tester", is_admin=0)
                db.add(u); db.commit(); db.refresh(u)
            return u
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(app)

    # seed producto
    db = TestingSessionLocal()
    try:
        cat = Category(name="Ropa"); db.add(cat); db.flush()
        p = Product(
            category_id=cat.id, name="Camiseta básica blanca",
            description="algodón", price=Decimal("39000.00"),
            vat_rate=Decimal("19.00"), stock=100, size="M",
        )
        db.add(p); db.commit(); db.refresh(p)
        pid = p.id
    finally:
        db.close()

    ok = True
    # add 2
    r1 = client.post("/cart/items", json={"product_id": pid, "quantity": 2})
    ok &= r1.status_code == 201
    data = r1.json() if r1.status_code == 201 else {}
    ok &= len(data.get("items", [])) == 1 and data["items"][0]["quantity"] == 2
    ok &= int(float(data["totals"]["total_net"])) == 78000
    ok &= int(float(data["totals"]["total_vat"])) == 14820
    ok &= int(float(data["totals"]["total_gross"])) == 92820

    if not ok:
        print("CARRITO: FAIL en POST /cart/items", r1.status_code, r1.text)
        sys.exit(1)

    item_id = data["items"][0]["id"]
    # update -> 3
    r2 = client.put(f"/cart/items/{item_id}", json={"quantity": 3})
    ok2 = r2.status_code == 200 and r2.json()["items"][0]["quantity"] == 3
    if not ok2:
        print("CARRITO: FAIL en PUT /cart/items/{id}", r2.status_code, r2.text)
        sys.exit(1)

    # delete
    r3 = client.delete(f"/cart/items/{item_id}")
    ok3 = r3.status_code == 200 and r3.json()["items"] == []
    print("CARRITO:", "PASS" if ok3 else "FAIL")
    sys.exit(0 if ok3 else 1)

if __name__ == "__main__":
    main()
