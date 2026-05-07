# Entity Relationship Diagram (ERD)

Este documento contiene un **ERD compacto** para Zarvent Repuestos, construido
desde los procesos documentados: clientes, catalogo de repuestos, inventario,
ventas, pagos, compras a proveedores y devoluciones.

El objetivo no es meter todas las tablas posibles. El objetivo es modelar el
nucleo del negocio sin duplicar informacion y dejando relaciones claras.

## Diagrama base

```mermaid
erDiagram
    PERSON ||--o| CUSTOMER : identifica
    CUSTOMER ||--o{ SALES_ORDER : re    aliza
    SALES_ORDER ||--|{ SALES_ORDER_ITEM : contiene
    SALES_ORDER ||--o{ PAYMENT : recibe
    SALES_ORDER ||--o{ RETURN_ORDER : puede_tener
    RETURN_ORDER ||--|{ RETURN_ORDER_ITEM : contiene
    SALES_ORDER_ITEM ||--o{ RETURN_ORDER_ITEM : puede_devolverse

    PART_CATEGORY ||--o{ PART : agrupa
    PART ||--o{ SALES_ORDER_ITEM : se_vende_como
    PART ||--o{ PURCHASE_ORDER_ITEM : se_compra_como
    PART ||--o{ INVENTORY_STOCK : se_controla_como
    PART ||--o{ PART_COMPATIBILITY : encaja
    VEHICLE_MODEL ||--o{ PART_COMPATIBILITY : acepta

    SUPPLIER ||--o{ PURCHASE_ORDER : recibe
    PURCHASE_ORDER ||--|{ PURCHASE_ORDER_ITEM : contiene

    PERSON {
        int person_id PK
        varchar first_name
        varchar last_name
        varchar identity_number UK
        varchar phone
        varchar email
        varchar address
    }

    CUSTOMER {
        int customer_id PK
        int person_id FK
        varchar billing_name
        varchar tax_id
        boolean is_active
    }

    SUPPLIER {
        int supplier_id PK
        varchar business_name
        varchar tax_id UK
        varchar phone
        varchar email
        varchar address
        boolean is_active
    }

    PART_CATEGORY {
        int part_category_id PK
        varchar name UK
        varchar description
    }

    PART {
        int part_id PK
        int part_category_id FK
        varchar internal_code UK
        varchar oem_code
        varchar name
        varchar brand
        varchar unit
        decimal sale_price
        decimal purchase_cost
        int warranty_days
        varchar status
    }

    VEHICLE_MODEL {
        int vehicle_model_id PK
        varchar make
        varchar model
        int year_from
        int year_to
    }

    PART_COMPATIBILITY {
        int part_compatibility_id PK
        int part_id FK
        int vehicle_model_id FK
        varchar engine_code
        varchar notes
    }

    INVENTORY_STOCK {
        int inventory_stock_id PK
        int part_id FK
        varchar location_name
        int quantity_on_hand
        int reorder_level
    }

    SALES_ORDER {
        int sales_order_id PK
        int customer_id FK
        date order_date
        varchar status
        decimal subtotal
        decimal discount_amount
        decimal total_amount
    }

    SALES_ORDER_ITEM {
        int sales_order_item_id PK
        int sales_order_id FK
        int part_id FK
        int quantity
        decimal unit_price
        decimal discount_amount
    }

    PAYMENT {
        int payment_id PK
        int sales_order_id FK
        date payment_date
        varchar method
        decimal amount
        varchar reference_number
        varchar status
    }

    PURCHASE_ORDER {
        int purchase_order_id PK
        int supplier_id FK
        date order_date
        date expected_date
        varchar status
        decimal total_amount
    }

    PURCHASE_ORDER_ITEM {
        int purchase_order_item_id PK
        int purchase_order_id FK
        int part_id FK
        int quantity_ordered
        int quantity_received
        decimal unit_cost
    }

    RETURN_ORDER {
        int return_order_id PK
        int sales_order_id FK
        date return_date
        varchar reason
        varchar resolution
        varchar status
    }

    RETURN_ORDER_ITEM {
        int return_order_item_id PK
        int return_order_id FK
        int sales_order_item_id FK
        int quantity
        decimal refund_amount
        boolean restock_allowed
    }

```

## Decisiones de diseno

- `PERSON` separa la identidad civil del rol comercial. Asi una persona puede
  existir primero como contacto y luego convertirse en `CUSTOMER` sin duplicar
  datos.
- `SALES_ORDER_ITEM` guarda `unit_price` historico. NO dependas del precio
  actual de `PART` para reconstruir ventas pasadas.
- `PURCHASE_ORDER_ITEM` guarda `unit_cost` historico para comparar costos de
  proveedor y margen.
- `PART_COMPATIBILITY` resuelve la relacion muchos-a-muchos entre repuestos y
  vehiculos. Sin esta tabla, vas a terminar duplicando descripciones a mano.
- `INVENTORY_STOCK` mantiene el stock actual por repuesto y ubicacion. Los
  movimientos detallados pueden agregarse como extension cuando el diseno base
  ya este estable.

## Alcance no incluido en este ERD compacto

Para mantener el modelo corto, quedan fuera del diagrama principal:

- usuarios, roles y permisos
- comprobantes/facturas con detalle tributario
- movimientos historicos de inventario
- marcas y modelos de vehiculo normalizados en tablas separadas
- reportes, porque los reportes se consultan desde las tablas operativas
