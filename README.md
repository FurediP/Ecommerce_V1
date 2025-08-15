E-COMMERCE LOCAL (ROPA) — FastAPI + JWT + MySQL + React (Vite)
=============================================================

Este proyecto implementa un e-commerce simple por microservicios:
- auth_service: registro/login y emisión de JWT
- catalog_service: categorías y productos (público + admin)
- cart_service: carrito por usuario (JWT)
- order_service: checkout/pedidos (JWT)
- ecommerce-ui: frontend mínimo con React + Vite

Tecnologías
-----------
- Python 3.12, FastAPI, SQLAlchemy, PyMySQL, Pydantic
- MySQL 8.x
- Node 18+ / npm
- Swagger (OpenAPI) para pruebas
- React + Vite para UI

Estructura
----------
Ecommerce/
├─ services/
│  ├─ auth_service/
│  ├─ catalog_service/
│  ├─ cart_service/
│  └─ order_service/
├─ scripts/        (SQL para crear/reiniciar BD)
├─ .env            (variables de entorno)
├─ requirements.txt
└─ ecommerce-ui/   (frontend)

Requisitos
----------
- Windows, Python 3.12, MySQL 8.x, Node 18+, npm
- MySQL local con usuario root para ejecutar scripts

1) Instalación backend
----------------------
# en la raíz del proyecto
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

2) Base de datos
----------------
- Abrir MySQL Workbench y ejecutar:
  scripts\01_schema.sql   (crea BD ecommerce, usuario ecom_user/ecom_pass, tablas y datos demo)
- Si necesitas limpiar todo:
  scripts\00_reset.sql    (DROP + CREATE)

3) Variables de entorno (.env en la raíz)
-----------------------------------------
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=ecommerce
DB_USER=ecom_user
DB_PASS=ecom_pass

JWT_SECRET=change_this_secret
JWT_ALG=HS256
JWT_EXPIRE_MIN=120

AUTH_PORT=8001
CATALOG_PORT=8002
CART_PORT=8003
ORDER_PORT=8005   # recomendado: cart en 8004 y orders en 8005

4) Levantar servicios (cada uno en su terminal)
-----------------------------------------------
# Auth
cd services\auth_service
uvicorn app.main:app --reload --port 8001

# Catálogo
cd services\catalog_service
uvicorn app.main:app --reload --port 8002

# Carrito
cd services\cart_service
uvicorn app.main:app --reload --port 8004

# Pedidos
cd services\order_service
uvicorn app.main:app --reload --port 8005

Swagger /docs
-------------
Auth:    http://127.0.0.1:8001/docs
Catalog: http://127.0.0.1:8002/docs
Cart:    http://127.0.0.1:8004/docs
Order:   http://127.0.0.1:8005/docs

5) Flujo rápido de pruebas (Swagger)
------------------------------------
1. Auth → POST /signup (opcional) y POST /login → copia access_token.
2. Catalog → (público) GET /products. Con token admin → POST /products:
   {
     "category_id": 1,
     "name": "Camiseta unisex básica negra",
     "description": "Algodón 100%",
     "price": 45000,
     "vat_rate": 19.00,
     "stock": 120,
     "size": "M",
     "image_url": null
   }
3. Cart → Authorize con tu token → GET /cart → POST /cart/items:
   { "product_id": 1, "quantity": 2 }
4. Order → Authorize con el mismo token → POST /orders/checkout.
   Luego GET /orders.

6) Frontend local (opcional)
----------------------------
cd Ecommerce
npm create vite@latest ecommerce-ui -- --template react
cd ecommerce-ui
npm install

Crear archivo .env.development:
VITE_AUTH_URL=http://127.0.0.1:8001
VITE_CATALOG_URL=http://127.0.0.1:8002
VITE_CART_URL=http://127.0.0.1:8004
VITE_ORDER_URL=http://127.0.0.1:8005

npm run dev   (abre http://localhost:5173)

CORS (ya habilitado en cada servicio):
- allow_origins = ["http://localhost:5173","http://127.0.0.1:5173"]

7) cURL de ejemplo
------------------
# login
curl -X POST http://127.0.0.1:8001/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@shop.com\",\"password\":\"Admin123!\"}"

# productos
curl http://127.0.0.1:8002/products

# agregar al carrito (reemplaza TOKEN)
curl -X POST http://127.0.0.1:8004/cart/items ^
  -H "Authorization: Bearer TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"product_id\":1,\"quantity\":2}"

# checkout
curl -X POST http://127.0.0.1:8005/orders/checkout -H "Authorization: Bearer TOKEN"

8) Solución de problemas comunes
--------------------------------
- ModuleNotFoundError: app → ejecuta uvicorn dentro de la carpeta del servicio
  (p.ej., cd services\auth_service; uvicorn app.main:app --reload --port 8001)
- ImportError email_validator → pip install email-validator
- Pydantic "Extra inputs are not permitted" → en config.py usa model_config extra="ignore"
- SQLAlchemy InvalidRequestError unique() → añade .unique() a los Result y usa lazy="selectin"
- CORS 404/405 en OPTIONS → verifica CORSMiddleware y origins (localhost y 127.0.0.1 con puerto 5173)
- 403 vs 401:
  * 403: no enviaste Authorization (falta token)
  * 401: token inválido/expirado
- .env: los servicios leen el .env de la raíz (ruta ajustada en config.py)

9) Licencia
-----------
MIT (o la que prefieras).

Autor
-----
Proyecto didáctico para uso local.
