ECOMMERCE (FASTAPI + MYSQL + REACT/TAILWIND)
===========================================

Proyecto ejemplo de e-commerce de ropa con microservicios en FastAPI y frontend en React + Vite + Tailwind.
Incluye: Auth (JWT), Catálogo, Carrito con controles (− / + / Quitar / Vaciar) y Checkout (Pedidos).
Todo preparado para ejecutarse en LOCAL.

----------------------------------------------------------------------
1) ESTRUCTURA DEL PROYECTO
----------------------------------------------------------------------
Ecommerce/
├─ .env                         -> variables compartidas (DB, JWT, PUERTOS)
├─ docs/
│  └─ 01_schema.sql             -> script MySQL (db, usuario, tablas, datos)
├─ services/
│  ├─ auth_service/
│  ├─ catalog_service/
│  ├─ cart_service/
│  └─ order_service/
└─ ecommerce-ui/                -> Vite + React + TypeScript + Tailwind

----------------------------------------------------------------------
2) REQUISITOS
----------------------------------------------------------------------
- Python 3.12
- MySQL 8.x
- Node.js 20+ (probado con Node 22) y npm 10+
- VS Code recomendado

----------------------------------------------------------------------
3) ARCHIVO .ENV (RAÍZ)
----------------------------------------------------------------------
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=ecommerce
DB_USER=ecom_user
DB_PASS=ecom_pass

JWT_SECRET=change_this_secret
JWT_ALG=HS256
JWT_EXPIRE_MIN=120   ; puedes subirlo (ej. 43200 = 30 días)

AUTH_PORT=8001
CATALOG_PORT=8002
CART_PORT=8004
ORDER_PORT=8005

NOTA: todos los servicios leen este .env y ya tienen CORS para http://localhost:5173 y http://127.0.0.1:5173

----------------------------------------------------------------------
4) BASE DE DATOS
----------------------------------------------------------------------
1. Abrir MySQL Workbench y ejecutar docs/01_schema.sql
   - Crea la BD ecommerce, el usuario ecom_user/ecom_pass, tablas y datos de ejemplo.
2. Si tenías una versión anterior, puedes DROPear tablas o la base antes de ejecutar.

----------------------------------------------------------------------
5) BACKEND (FASTAPI)
----------------------------------------------------------------------
En la raíz:
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt

Levanta CADA servicio desde su carpeta (4 terminales):

Auth (8001)
  cd services\auth_service
  uvicorn app.main:app --reload --port 8001

Catálogo (8002)
  cd services\catalog_service
  uvicorn app.main:app --reload --port 8002

Carrito (8004)
  cd services\cart_service
  uvicorn app.main:app --reload --port 8004

Pedidos (8005)
  cd services\order_service
  uvicorn app.main:app --reload --port 8005

Swagger:
- Auth      -> http://127.0.0.1:8001/docs
- Catálogo  -> http://127.0.0.1:8002/docs
- Carrito   -> http://127.0.0.1:8004/docs
- Pedidos   -> http://127.0.0.1:8005/docs

Notas técnicas:
- Si ves “InvalidRequestError: The unique() method must be invoked…”, añade .unique() a Result o usa lazy="selectin" en relaciones.
- Si Pydantic pide email-validator:  pip install email-validator  (o  pip install "pydantic[email]")
- CORS/OPTIONS 405: ya está configurado CORSMiddleware para localhost:5173 y 127.0.0.1:5173

----------------------------------------------------------------------
6) FRONTEND (VITE + REACT + TAILWIND)
----------------------------------------------------------------------
cd ecommerce-ui
npm i
npm run dev
Abrir: http://localhost:5173/

Tailwind ya está configurado (ESM):
- tailwind.config.js incluye plugin @tailwindcss/forms y la paleta "brand".
- src/index.css aplica tema dark (bg-slate-950, text-slate-100).

Funcionalidades:
- Catálogo con búsqueda y selector de cantidad (− / número / +) antes de “+ Carrito”.
- Carrito con controles por ítem: − / +, Quitar y Vaciar; muestra neto/IVA/total.
- Checkout crea pedido; vista de Pedidos lista.
- Login con JWT guardado en localStorage (Authorization: Bearer).

Credenciales de ejemplo (si existen en tu DB):
  Email: admin@shop.com
  Pass : Admin123!

----------------------------------------------------------------------
7) JWT: DURACIÓN Y OPCIONES
----------------------------------------------------------------------
Opción rápida (DEV): aumentar JWT_EXPIRE_MIN en .env (ej. 43200 = 30 días) y reiniciar auth_service.

Solo DEV: puedes decodificar ignorando exp (options={"verify_exp": false}) para que no caduque; no usar en producción.

Producción (recomendado): Access Token corto (15–60 min) + Refresh Token largo (30–60 días) y endpoint /refresh para renovar.
Para hacerlo robusto: guardar/rotar refresh tokens y usar cookies httpOnly.

----------------------------------------------------------------------
8) FLUJO DE PRUEBA EN LOCAL
----------------------------------------------------------------------
1. MySQL corriendo y DB creada con docs/01_schema.sql
2. Activar venv e instalar requirements.txt
3. Levantar servicios: Auth -> Catálogo -> Carrito -> Pedidos
4. Frontend: npm run dev en ecommerce-ui
5. En http://localhost:5173:
   - Inicia sesión
   - Catálogo: selecciona cantidad y “+ Carrito”
   - Carrito: ajusta cantidades, Quitar/Vaciar, Checkout
   - Pedidos: verifica pedido creado

----------------------------------------------------------------------
9) ENDPOINTS CLAVE
----------------------------------------------------------------------
Auth:
  POST /login  -> { access_token, token_type }
(Con refresh en prod: POST /refresh -> nuevo access_token)

Catálogo:
  GET  /products?q=

Carrito:
  GET    /cart
  POST   /cart/items               body { product_id, quantity }
  PUT    /cart/items/{item_id}     body { quantity } (0 elimina)
  DELETE /cart/items/{item_id}
  DELETE /cart/items               (vaciar)

Pedidos:
  POST /orders/checkout
  GET  /orders/me

----------------------------------------------------------------------
10) PROBLEMAS COMUNES
----------------------------------------------------------------------
- 401/403: token ausente/expirado -> vuelve a iniciar sesión o aumenta JWT_EXPIRE_MIN.
- OPTIONS 405: revisar CORSMiddleware y usar http://localhost:5173 (o 127.0.0.1:5173).
- ModuleNotFoundError: 'app' al iniciar Uvicorn -> ejecuta uvicorn DENTRO de cada carpeta de servicio.
  Ej.: cd services\auth_service && uvicorn app.main:app --reload --port 8001

----------------------------------------------------------------------
11) AUTOR
----------------------------------------------------------------------
Fredy David Pastrana García.
