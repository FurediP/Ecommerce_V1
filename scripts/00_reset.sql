-- DESACTIVAR FKs para poder borrar sin problemas
SET FOREIGN_KEY_CHECKS = 0;

-- Borra BDs de intentos previos (ajusta si quieres conservar alguna)
DROP DATABASE IF EXISTS ecommerce;
DROP DATABASE IF EXISTS ecommerce_db;
DROP DATABASE IF EXISTS auth_db;
DROP DATABASE IF EXISTS catalog_db;
DROP DATABASE IF EXISTS cart_db;
DROP DATABASE IF EXISTS order_db;

-- Borra el usuario antiguo
DROP USER IF EXISTS 'ecom_user'@'localhost';

SET FOREIGN_KEY_CHECKS = 1;
