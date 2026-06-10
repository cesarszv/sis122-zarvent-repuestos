-- ============================================================================
-- Zarvent Repuestos - MySQL schema (script ejecutable, idempotente)
-- ----------------------------------------------------------------------------
-- Este archivo traduce el ERD academico de docs/database/erd.md a un esquema
-- MySQL real. La aplicacion tambien crea las tablas via
-- src/zarvent_repuestos/database/init_db.py (CREATE TABLE IF NOT EXISTS);
-- este script es la referencia academica y la fuente de verdad para que un
-- mysql-client y verificarlo con DataGrip.
--
-- Convenciones:
--   - Nombres tecnicos en native US English.
--   - Textos descriptivos en Latam Spanish.
--   - Orden de creacion: entidades base -> dependencias.
--   - Todas las sentencias son idempotentes (IF NOT EXISTS / OR REPLACE).
-- ============================================================================

CREATE DATABASE IF NOT EXISTS sis122_zarvent_repuestos
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE sis122_zarvent_repuestos;

-- ----------------------------------------------------------------------------
-- 1. PERSON (identidad separada del rol comercial; 1..0..1 con customer)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS person (
    person_id        INT AUTO_INCREMENT PRIMARY KEY,
    first_name       VARCHAR(100) NOT NULL,
    last_name        VARCHAR(100) NOT NULL,
    identity_number  VARCHAR(50)  UNIQUE NOT NULL,
    phone            VARCHAR(50),
    email            VARCHAR(100),
    address          VARCHAR(255)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 2. CUSTOMER (rol comercial; persona que compra)
--    RF-01. Migracion v1: agregar is_active para soft-delete defensible.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customer (
    customer_id  INT AUTO_INCREMENT PRIMARY KEY,
    person_id    INT          UNIQUE NOT NULL,
    billing_name VARCHAR(150),
    tax_id       VARCHAR(50),
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 3. SUPPLIER (RF-07)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS supplier (
    supplier_id    INT AUTO_INCREMENT PRIMARY KEY,
    business_name  VARCHAR(150) NOT NULL,
    tax_id         VARCHAR(50)  UNIQUE NOT NULL,
    phone          VARCHAR(50),
    email          VARCHAR(100),
    address        VARCHAR(255),
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 4. PART_CATEGORY (RF-02)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS part_category (
    part_category_id INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100) UNIQUE NOT NULL,
    description      TEXT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 5. PART (RF-02, RF-04)
--    status soporta soft-delete via inactivacion logica.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS part (
    part_id          INT AUTO_INCREMENT PRIMARY KEY,
    part_category_id INT          NOT NULL,
    internal_code    VARCHAR(50)  UNIQUE NOT NULL,
    oem_code         VARCHAR(50),
    name             VARCHAR(150) NOT NULL,
    brand            VARCHAR(100),
    unit             VARCHAR(20)  NOT NULL DEFAULT 'pcs',
    sale_price       DECIMAL(10, 2) NOT NULL,
    purchase_cost    DECIMAL(10, 2) NOT NULL,
    warranty_days    INT          NOT NULL DEFAULT 0,
    status           VARCHAR(50)  NOT NULL DEFAULT 'active',
    FOREIGN KEY (part_category_id) REFERENCES part_category (part_category_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 6. INVENTORY_STOCK (RF-04)
--    relacion 1 a 1 forzada por UNIQUE(part_id) - decision del esquema fisico
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory_stock (
    inventory_stock_id INT AUTO_INCREMENT PRIMARY KEY,
    part_id            INT          UNIQUE NOT NULL,
    location_name      VARCHAR(100),
    quantity_on_hand   INT          NOT NULL DEFAULT 0,
    reorder_level      INT          NOT NULL DEFAULT 10,
    FOREIGN KEY (part_id) REFERENCES part (part_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 7. SALES_ORDER (RF-05, RF-06)
--    status: 'Paid' (unico valor usado por la app en v1).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales_order (
    sales_order_id   INT AUTO_INCREMENT PRIMARY KEY,
    customer_id      INT          NOT NULL,
    order_date       DATE         NOT NULL,
    status           VARCHAR(50)  NOT NULL DEFAULT 'Paid',
    subtotal         DECIMAL(10, 2) NOT NULL,
    discount_amount  DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount     DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 8. SALES_ORDER_ITEM (RF-05; precio historico)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales_order_item (
    sales_order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sales_order_id      INT          NOT NULL,
    part_id             INT          NOT NULL,
    quantity            INT          NOT NULL,
    unit_price          DECIMAL(10, 2) NOT NULL,
    discount_amount     DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (sales_order_id) REFERENCES sales_order (sales_order_id) ON DELETE CASCADE,
    FOREIGN KEY (part_id)        REFERENCES part (part_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 9. PAYMENT (RF-06)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payment (
    payment_id        INT AUTO_INCREMENT PRIMARY KEY,
    sales_order_id    INT          NOT NULL,
    payment_date      DATE         NOT NULL,
    method            VARCHAR(50)  NOT NULL,
    amount            DECIMAL(10, 2) NOT NULL,
    reference_number  VARCHAR(100),
    status            VARCHAR(50)  NOT NULL DEFAULT 'Completed',
    FOREIGN KEY (sales_order_id) REFERENCES sales_order (sales_order_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 10. PURCHASE_ORDER (RF-07)
--     status: 'Pending' | 'Partially Received' | 'Received' | 'Cancelled'
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchase_order (
    purchase_order_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id       INT          NOT NULL,
    order_date        DATE         NOT NULL,
    expected_date     DATE,
    status            VARCHAR(50)  NOT NULL DEFAULT 'Pending',
    total_amount      DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES supplier (supplier_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 11. PURCHASE_ORDER_ITEM (RF-07)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchase_order_item (
    purchase_order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_order_id      INT          NOT NULL,
    part_id                INT          NOT NULL,
    quantity_ordered       INT          NOT NULL,
    quantity_received      INT          NOT NULL DEFAULT 0,
    unit_cost              DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_order (purchase_order_id) ON DELETE CASCADE,
    FOREIGN KEY (part_id)           REFERENCES part (part_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 12. USERS (autenticacion; no parte del ERD academico)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    username  VARCHAR(50) UNIQUE NOT NULL,
    password  VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

-- ============================================================================
-- MIGRACIONES IDEMPOTENTES (v1)
-- ----------------------------------------------------------------------------
-- Estas sentencias son seguras de correr varias veces: usan INFORMATION_SCHEMA
-- para detectar si la columna ya existe. La aplicacion tambien las ejecuta
-- desde init_db.py, pero quedan aca para quien prefiera crear el schema
-- desde cliente MySQL.
-- ============================================================================

-- customer.is_active: soporte de soft-delete para RF-01
SET @col_exists := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME   = 'customer'
      AND COLUMN_NAME  = 'is_active'
);
SET @sql := IF(
    @col_exists = 0,
    'ALTER TABLE customer ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE AFTER tax_id',
    'SELECT 1'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- ============================================================================
-- VISTAS (RF-09)
-- ----------------------------------------------------------------------------
-- Las vistas encapsulan consultas que el dashboard y otras pantallas repiten.
-- Son objetos academicos defendibles: muestran el uso de CREATE VIEW y permiten
-- que un SELECT complejo sea leido por un junior sin entender el JOIN completo.
-- ============================================================================

-- Repuestos con stock bajo o igual al umbral de reorden.
-- Equivale a la consulta inline que actualmente vive en
-- sales_crud.obtener_metricas_dashboard().
CREATE OR REPLACE VIEW vw_low_stock_parts AS
SELECT
    p.part_id,
    p.internal_code,
    p.name,
    p.brand,
    s.quantity_on_hand,
    s.reorder_level,
    (s.reorder_level - s.quantity_on_hand) AS shortage
FROM part p
JOIN inventory_stock s ON p.part_id = s.part_id
WHERE s.quantity_on_hand <= s.reorder_level
ORDER BY s.quantity_on_hand ASC;

-- Resumen diario de ventas pagadas, con conteo y total.
-- Equivale a la consulta de "Ventas de Hoy" del dashboard.
CREATE OR REPLACE VIEW vw_daily_sales_summary AS
SELECT
    order_date,
    COUNT(*)            AS orders_count,
    SUM(subtotal)       AS subtotal_total,
    SUM(discount_amount) AS discount_total,
    SUM(total_amount)   AS total_amount
FROM sales_order
WHERE status = 'Paid'
GROUP BY order_date
ORDER BY order_date DESC;

-- ============================================================================
-- Procedimientos almacenados y triggers: FUERA DE ALCANCE v1.
-- El plan los marca como backlog v2. Para la defensa basta con mencionar que
-- quedan disponibles como objetos academicos si se justifican.
-- ============================================================================
