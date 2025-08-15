E-COMMERCE (ROPA) — FASTAPI + JWT + MYSQL + REACT (VITE)
========================================================

Microservicios de e-commerce (ropa) con FastAPI + JWT, MySQL y un frontend React (Vite + Tailwind).
Incluye scripts de self-tests SIN pytest y un agregador para correrlos todos desde la terminal.

--------------------------------------------------------
1) ESTRUCTURA
--------------------------------------------------------
(Estructura.png)
(EcommerceUML.png)
--------------------------------------------------------
2) REQUISITOS
--------------------------------------------------------
- Windows 10/11 o similar
- Python 3.12.x + pip
- Node.js 18+ (recomendado 20+)
- MySQL 8.x
- (Python) Crear y activar venv:
    > python -m venv .venv
    > .\.venv\Scripts\Activate.ps1
- Instalar dependencias:
    > pip install -r requirements.txt

--------------------------------------------------------
3) CONFIGURACIÓN (.env)
--------------------------------------------------------
Coloca un archivo .env en la raíz del proyecto:

# MySQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=ecommerce
DB_USER=ecom_user
DB_PASS=ecom_pass

# JWT
JWT_SECRET=change_this_secret
JWT_ALG=HS256
JWT_EXPIRE_MIN=43200
# 43200 = 30 días (si cambias aquí, no pongas el comentario en la misma línea)

# Puertos
AUTH_PORT=8001
CATALOG_PORT=8002
CART_PORT=8004
ORDER_PORT=8005

NOTAS:
- Importa el esquema: docs/01_schema.sql (crea DB y tablas, y usuario ecom_user/ecom_pass).
- Cada servicio también puede leer un .env local; por defecto apuntan al .env de la raíz.

--------------------------------------------------------
4) ARRANQUE RÁPIDO (LOCAL)
--------------------------------------------------------
1. Asegúrate de tener la base de datos creada (docs/01_schema.sql).
2. Activa el venv:
   > .\.venv\Scripts\Activate.ps1
3. Levanta los servicios (cada uno en su carpeta):

Auth (8001)
> cd services\auth_service
> uvicorn app.main:app --reload --port 8001

Catalog (8002)
> cd services\catalog_service
> uvicorn app.main:app --reload --port 8002

Cart (8004)
> cd services\cart_service
> uvicorn app.main:app --reload --port 8004

Order (8005)
> cd services\order_service
> uvicorn app.main:app --reload --port 8005

4. Frontend (Vite en 5173)
> cd ecommerce-ui
> npm install
> npm run dev
Abrir: http://localhost:5173/

APIs (OpenAPI/Swagger):
- http://127.0.0.1:8001/docs (auth)
- http://127.0.0.1:8002/docs (catalog)
- http://127.0.0.1:8004/docs (cart)
- http://127.0.0.1:8005/docs (order)

--------------------------------------------------------
5) ENDPOINTS PRINCIPALES (RESUMEN)
--------------------------------------------------------
AUTH
- POST /login                           -> devuelve JWT (Bearer)
- GET  /me                              -> usuario autenticado

CATÁLOGO
- GET  /products?q=&skip=0&limit=50     -> listar/buscar
- GET  /products/{id}                   -> detalle

CARRITO  (requiere Authorization: Bearer <token>)
- GET    /cart                          -> ver carrito activo
- POST   /cart/items                    -> body: {product_id, quantity}
- PUT    /cart/items/{item_id}          -> body: {quantity}
- DELETE /cart/items/{item_id}          -> eliminar item
- DELETE /cart/items                    -> vaciar carrito

PEDIDOS (requiere Authorization)
- POST /orders/checkout                 -> crea pedido desde carrito
- GET  /orders                          -> mis pedidos (alias de /orders/me)
- GET  /orders/{order_id}               -> ver un pedido propio

ADMIN (opcional, si activas require_admin)
- GET  /admin/orders?status=created|... -> listar pedidos
- PUT  /admin/orders/{id}/status        -> cambiar estado

--------------------------------------------------------
6) FRONTEND (VITE + TAILWIND)
--------------------------------------------------------
- Stack: React + Vite + TailwindCSS 3 + @tailwindcss/forms.
- Variables de API apuntan por defecto a 127.0.0.1 y puertos del .env.
- Flujo: login → catálogo (busca/añade con qty) → carrito (editar qty, eliminar, vaciar) → checkout → pedidos.

--------------------------------------------------------
7) SELF-TESTS SIN PYTEST
--------------------------------------------------------
Cada servicio tiene un script de prueba autocontenida (SQLite en memoria + TestClient):

Auth:
> cd services\auth_service
> python run_selftest.py
Salida esperada: AUTH: PASS

Catalog:
> cd services\catalog_service
> python run_selftest.py
Salida esperada: CATÁLOGO: PASS

Cart:
> cd services\cart_service
> python run_selftest.py
Salida esperada: CARRITO: PASS

Order:
> cd services\order_service
> python run_selftest.py
Salida esperada: PEDIDOS: PASS

IMPORTANTE
- No requieren MySQL (usan SQLite en memoria).
- Sirven como pruebas unitarias mínimas reproducibles sin pytest.

--------------------------------------------------------
8) EJECUTAR TODOS LOS SELF-TESTS
--------------------------------------------------------
En la raíz:
> python run_all_selftests.py

Genera reporte en:
- docs/tests-summary.txt
y devuelve código de salida 0 si todo PASS.

--------------------------------------------------------
9) SMOKE TEST (OPCIONAL, END-TO-END)
--------------------------------------------------------
Con los 4 servicios corriendo en local:
> python smoke_test_local.py

Prueba: login → listar productos → añadir al carrito → ver carrito → checkout → mis pedidos.

Variables opcionales (en la misma sesión):
> set TEST_EMAIL=admin@shop.com
> set TEST_PASSWORD=Admin123!

--------------------------------------------------------
10) CASO DE USO
--------------------------------------------------------
Ver docs/UC-01-Checkout.txt (describe actores, precondiciones, flujo principal y alternos).

--------------------------------------------------------
11) PROBLEMAS FRECUENTES (TROUBLESHOOTING)
--------------------------------------------------------
- 422 en /login durante self-test:
  Usa un email válido (p.ej. selftest@example.com). EmailStr rechaza dominios no válidos.

- “(trapped) error reading bcrypt version” al iniciar auth:
  Es un warning de passlib con bcrypt 4.x; no afecta funcionamiento.
  Opcional: bajar bcrypt a 3.x → pip install "bcrypt<4" y fijar en requirements.

- ImportError: email-validator:
  > pip install pydantic[email]

- CORS “OPTIONS 405” desde Vite:
  Asegúrate de tener ambos orígenes permitidos en cada servicio:
    allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

- JWT expira “muy rápido”:
  Aumenta JWT_EXPIRE_MIN en .env (p.ej. 43200 = 30 días). Evita comentarios en la misma línea.
  Los services toleran comentarios si usas el validator que limpia “# …”.

- SQLite vs MySQL (en self-tests):
  Los self-tests usan SQLite y no requieren MySQL. Para uso real, corre contra MySQL.

--------------------------------------------------------
12) CREDENCIALES DE EJEMPLO
--------------------------------------------------------
Usuario admin de ejemplo (siembra inicial / script SQL / Uso log in FrontEnd):
- email: admin@example.com
- pass: 123


--------------------------------------------------------
13) CONTACTO
--------------------------------------------------------
Este proyecto fue preparado como prueba técnica. Cualquier duda sobre ejecución, scripts o endpoints, revisar README y /docs de cada servicio (Swagger), o contactar al autor del repositorio.