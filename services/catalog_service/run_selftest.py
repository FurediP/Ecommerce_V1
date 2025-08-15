# services/catalog_service/run_selftest.py
import sys
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base
from app.deps import get_db
from app.models import Category, Product

def main():
    # DB SQLite en memoria compartida entre conexiones
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

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # seed
    db = TestingSessionLocal()
    try:
        cat = Category(name="Ropa"); db.add(cat); db.flush()
        p = Product(
            category_id=cat.id, name="Camiseta básica blanca",
            description="algodón", price=Decimal("39000.00"),
            vat_rate=Decimal("19.00"), stock=100, size="M",
        )
        db.add(p); db.commit()
    finally:
        db.close()

    # test
    r = client.get("/products?q=camiseta")
    ok = (r.status_code == 200) and any("camiseta" in x["name"].lower() for x in r.json())
    print("CATÁLOGO:", "PASS" if ok else "FAIL", f"(status={r.status_code}, items={len(r.json()) if r.status_code==200 else 'n/a'})")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
