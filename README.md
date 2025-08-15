# E-commerce de ropa — FastAPI + JWT + MySQL

Microservicios:
- `auth_service` → Login/Signup + JWT
- `catalog_service` → Categorías/Productos (público + admin)
- `cart_service` → Carrito por usuario (JWT)
- `order_service` → Checkout y pedidos (JWT)

## Requisitos
- Windows / Python 3.12
- MySQL 8.x (usuario root local)
- VS Code (recomendado)

## 1) Setup
```powershell
cd C:\Users\fdpas\Desktop\Ecommerce
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

## 2) Base de datos
Usando MySQLWorkbench ejecutamos el script 'scripts\01_schema.sql', eso crea BD ecommerce, usuario ecom_user y tablas + datos demo