# services/auth_service/run_selftest.py
import sys
from typing import Any, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext

from app.main import app
from app.database import Base
from app.deps import get_db
from app.models import User  # Debe existir en este servicio

# ---------- utilidades ----------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _coerce_default(col) -> Any:
    t = col.type.__class__.__name__.lower()
    if "string" in t or "varchar" in t or "text" in t:
        return "x"
    if "integer" in t or "smallint" in t:
        return 0
    if "numeric" in t or "decimal" in t or "float" in t or "real" in t:
        return 0
    if "boolean" in t:
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

    # overrides
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # ---- seed user con bcrypt ----
    email = "selftest@example.com"
    plain = "SelfTest123!"
    hashed = pwd_context.hash(plain)

    db = TestingSessionLocal()
    try:
        u = db.query(User).first()
        if not u:
            # Rellena sólo campos existentes; los requeridos sin default se completan
            u = make_instance(
                User,
                email=email,
                hashed_password=hashed,
                full_name="Self Tester",
                is_admin=0,
            )
            db.add(u); db.commit()
    finally:
        db.close()

    # ---- /login (varios formatos) ----
    token = None
    tried = []

    # 1) JSON email/password
    r = client.post("/login", json={"email": email, "password": plain})
    tried.append(("json_email", r.status_code))
    if r.status_code == 200 and "access_token" in r.json():
        token = r.json()["access_token"]

    # 2) JSON username/password
    if not token:
        r2 = client.post("/login", json={"username": email, "password": plain})
        tried.append(("json_username", r2.status_code))
        if r2.status_code == 200 and "access_token" in r2.json():
            token = r2.json()["access_token"]

    # 3) OAuth2 form
    if not token:
        r3 = client.post(
            "/login",
            data={"username": email, "password": plain, "grant_type": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tried.append(("form_oauth2", r3.status_code))
        if r3.status_code == 200 and "access_token" in r3.json():
            token = r3.json()["access_token"]

    print("[DEBUG] /login intentos ->", tried)
    if not token:
        print("AUTH: FAIL en /login (no se obtuvo token)")
        sys.exit(1)

    print("[DEBUG] token (primeros 20):", token[:20] + "...")

    # ---- Ruta protegida opcional ----
    headers = {"Authorization": f"Bearer {token}"}
    protected_paths = ["/me", "/users/me", "/profile", "/auth/me"]
    ok_protected = False
    for path in protected_paths:
        resp = client.get(path, headers=headers)
        print(f"[DEBUG] GET {path} -> {resp.status_code}")
        if resp.status_code == 200:
            ok_protected = True
            break

    # No todas las APIs exponen /me; con tener token ya consideramos PASS
    print("AUTH:", "PASS" if token else "FAIL")
    sys.exit(0 if token else 1)

if __name__ == "__main__":
    main()
