/*
Zarvent Repuestos, Database Schema

Source model:
docs/database/erd.md

Target engine:
PostgreSQL 18.4
*/
BEGIN;

CREATE TABLE person (
    person_id integer GENERATED ALWAYS AS IDENTITY,
    first_name varchar(80) NOT NULL,
    last_name varchar(80) NOT NULL,
    identity_number varchar(30),
    phone varchar(30),
    email varchar(120),
    address varchar(200),

    CONSTRAINT pk_person PRIMARY KEY (person_id),
    CONSTRAINT uk_person_identity_number UNIQUE (identity_number)
);

CREATE TABLE customer (
    customer_id integer GENERATED ALWAYS AS IDENTITY,
    person_id integer NOT NULL,
    billing_name varchar(160),
    tax_id varchar(30),

    CONSTRAINT pk_customer PRIMARY KEY (customer_id),
    CONSTRAINT uk_customer_person_id UNIQUE (person_id),
    CONSTRAINT fk_customer_person
        FOREIGN KEY (person_id)
        REFERENCES person (person_id)
        ON UPDATE CASCADE
);

CREATE TABLE supplier (
    supplier_id integer GENERATED ALWAYS AS IDENTITY,
    business_name varchar(160) NOT NULL,
    tax_id varchar(30),
    phone varchar(30),
    email varchar(120),
    address varchar(200),
    is_active boolean NOT NULL DEFAULT true,

    CONSTRAINT pk_supplier PRIMARY KEY (supplier_id),
    CONSTRAINT uk_supplier_tax_id UNIQUE (tax_id)
);

CREATE TABLE part_category (
    part_category_id integer GENERATED ALWAYS AS IDENTITY,
    name varchar(80) NOT NULL,
    description varchar(250),

    CONSTRAINT pk_part_category PRIMARY KEY (part_category_id),
    CONSTRAINT uk_part_category_name UNIQUE (name)
);

CREATE TABLE part (
    part_id integer GENERATED ALWAYS AS IDENTITY,
    part_category_id integer NOT NULL,
    internal_code varchar(40) NOT NULL,
    oem_code varchar(60),
    name varchar(160) NOT NULL,
    brand varchar(80),
    unit varchar(30) NOT NULL DEFAULT 'unit',
    sale_price numeric(12, 2) NOT NULL,
    purchase_cost numeric(12, 2) NOT NULL,
    warranty_days integer NOT NULL DEFAULT 0,
    status varchar(20) NOT NULL DEFAULT 'active',

    CONSTRAINT pk_part PRIMARY KEY (part_id),
    CONSTRAINT uk_part_internal_code UNIQUE (internal_code),
    CONSTRAINT fk_part_part_category
        FOREIGN KEY (part_category_id)
        REFERENCES part_category (part_category_id)
        ON UPDATE CASCADE,
    CONSTRAINT ck_part_sale_price_non_negative
        CHECK (sale_price >= 0),
    CONSTRAINT ck_part_purchase_cost_non_negative
        CHECK (purchase_cost >= 0),
    CONSTRAINT ck_part_warranty_days_non_negative
        CHECK (warranty_days >= 0),
    CONSTRAINT ck_part_status
        CHECK (status IN ('active', 'inactive', 'discontinued', 'blocked'))
);

CREATE TABLE vehicle_model (
    vehicle_model_id integer GENERATED ALWAYS AS IDENTITY,
    make varchar(80) NOT NULL,
    model varchar(80) NOT NULL,
    year_from integer,
    year_to integer,

    CONSTRAINT pk_vehicle_model PRIMARY KEY (vehicle_model_id),
    CONSTRAINT uk_vehicle_model
        UNIQUE NULLS NOT DISTINCT (make, model, year_from, year_to),
    CONSTRAINT ck_vehicle_model_year_range
        CHECK (year_from IS NULL OR year_to IS NULL OR year_to >= year_from)
);

CREATE TABLE part_compatibility (
    part_compatibility_id integer GENERATED ALWAYS AS IDENTITY,
    part_id integer NOT NULL,
    vehicle_model_id integer NOT NULL,
    engine_code varchar(60),
    notes varchar(250),

    CONSTRAINT pk_part_compatibility PRIMARY KEY (part_compatibility_id),
    CONSTRAINT fk_part_compatibility_part
        FOREIGN KEY (part_id)
        REFERENCES part (part_id)
        ON UPDATE CASCADE,
    CONSTRAINT fk_part_compatibility_vehicle_model
        FOREIGN KEY (vehicle_model_id)
        REFERENCES vehicle_model (vehicle_model_id)
        ON UPDATE CASCADE,
    CONSTRAINT uk_part_compatibility
        UNIQUE NULLS NOT DISTINCT (part_id, vehicle_model_id, engine_code)
);

CREATE TABLE inventory_stock (
    inventory_stock_id integer GENERATED ALWAYS AS IDENTITY,
    part_id integer NOT NULL,
    location_name varchar(100) NOT NULL,
    quantity_on_hand integer NOT NULL DEFAULT 0,
    reorder_level integer NOT NULL DEFAULT 0,

    CONSTRAINT pk_inventory_stock PRIMARY KEY (inventory_stock_id),
    CONSTRAINT fk_inventory_stock_part
        FOREIGN KEY (part_id)
        REFERENCES part (part_id)
        ON UPDATE CASCADE,
    CONSTRAINT uk_inventory_stock_part_location
        UNIQUE (part_id, location_name),
    CONSTRAINT ck_inventory_stock_quantity_on_hand_non_negative
        CHECK (quantity_on_hand >= 0),
    CONSTRAINT ck_inventory_stock_reorder_level_non_negative
        CHECK (reorder_level >= 0)
);

CREATE TABLE sales_order (
    sales_order_id integer GENERATED ALWAYS AS IDENTITY,
    customer_id integer NOT NULL,
    order_date date NOT NULL DEFAULT CURRENT_DATE,
    status varchar(20) NOT NULL DEFAULT 'draft',
    subtotal numeric(12, 2) NOT NULL DEFAULT 0,
    discount_amount numeric(12, 2) NOT NULL DEFAULT 0,
    total_amount numeric(12, 2) NOT NULL DEFAULT 0,

    CONSTRAINT pk_sales_order PRIMARY KEY (sales_order_id),
    CONSTRAINT fk_sales_order_customer
        FOREIGN KEY (customer_id)
        REFERENCES customer (customer_id)
        ON UPDATE CASCADE,
    CONSTRAINT ck_sales_order_status
        CHECK (status IN ('draft', 'confirmed', 'paid', 'cancelled', 'returned')),
    CONSTRAINT ck_sales_order_subtotal_non_negative
        CHECK (subtotal >= 0),
    CONSTRAINT ck_sales_order_discount_amount_non_negative
        CHECK (discount_amount >= 0),
    CONSTRAINT ck_sales_order_total_amount_non_negative
        CHECK (total_amount >= 0),
    CONSTRAINT ck_sales_order_discount_not_greater_than_subtotal
        CHECK (discount_amount <= subtotal),
    CONSTRAINT ck_sales_order_total_matches_subtotal
        CHECK (total_amount = subtotal - discount_amount)
);

CREATE TABLE sales_order_item (
    sales_order_item_id integer GENERATED ALWAYS AS IDENTITY,
    sales_order_id integer NOT NULL,
    part_id integer NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(12, 2) NOT NULL,
    discount_amount numeric(12, 2) NOT NULL DEFAULT 0,

    CONSTRAINT pk_sales_order_item PRIMARY KEY (sales_order_item_id),
    CONSTRAINT fk_sales_order_item_sales_order
        FOREIGN KEY (sales_order_id)
        REFERENCES sales_order (sales_order_id)
        ON UPDATE CASCADE,
    CONSTRAINT fk_sales_order_item_part
        FOREIGN KEY (part_id)
        REFERENCES part (part_id)
        ON UPDATE CASCADE,
    CONSTRAINT ck_sales_order_item_quantity_positive
        CHECK (quantity > 0),
    CONSTRAINT ck_sales_order_item_unit_price_non_negative
        CHECK (unit_price >= 0),
    CONSTRAINT ck_sales_order_item_discount_amount_non_negative
        CHECK (discount_amount >= 0),
    CONSTRAINT ck_sales_order_item_discount_not_greater_than_line_total
        CHECK (discount_amount <= quantity * unit_price)
);

CREATE TABLE payment (
    payment_id integer GENERATED ALWAYS AS IDENTITY,
    sales_order_id integer NOT NULL,
    payment_date date NOT NULL DEFAULT CURRENT_DATE,
    method varchar(30) NOT NULL,
    amount numeric(12, 2) NOT NULL,
    reference_number varchar(80),
    status varchar(20) NOT NULL DEFAULT 'pending',

    CONSTRAINT pk_payment PRIMARY KEY (payment_id),
    CONSTRAINT fk_payment_sales_order
        FOREIGN KEY (sales_order_id)
        REFERENCES sales_order (sales_order_id)
        ON UPDATE CASCADE,
    CONSTRAINT ck_payment_amount_positive
        CHECK (amount > 0),
    CONSTRAINT ck_payment_method
        CHECK (method IN ('cash', 'bank_transfer', 'qr', 'card', 'other')),
    CONSTRAINT ck_payment_status
        CHECK (status IN ('pending', 'confirmed', 'cancelled', 'refunded'))
);

CREATE TABLE purchase_order (
    purchase_order_id integer GENERATED ALWAYS AS IDENTITY,
    supplier_id integer NOT NULL,
    order_date date NOT NULL DEFAULT CURRENT_DATE,
    expected_date date,
    status varchar(20) NOT NULL DEFAULT 'draft',
    total_amount numeric(12, 2) NOT NULL DEFAULT 0,

    CONSTRAINT pk_purchase_order PRIMARY KEY (purchase_order_id),
    CONSTRAINT fk_purchase_order_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES supplier (supplier_id)
        ON UPDATE CASCADE,
    CONSTRAINT ck_purchase_order_status
        CHECK (status IN ('draft', 'sent', 'partial', 'received', 'cancelled')),
    CONSTRAINT ck_purchase_order_total_amount_non_negative
        CHECK (total_amount >= 0),
    CONSTRAINT ck_purchase_order_expected_date
        CHECK (expected_date IS NULL OR expected_date >= order_date)
);

CREATE TABLE purchase_order_item (
    purchase_order_item_id integer GENERATED ALWAYS AS IDENTITY,
    purchase_order_id integer NOT NULL,
    part_id integer NOT NULL,
    quantity_ordered integer NOT NULL,
    quantity_received integer NOT NULL DEFAULT 0,
    unit_cost numeric(12, 2) NOT NULL,

    CONSTRAINT pk_purchase_order_item PRIMARY KEY (purchase_order_item_id),
    CONSTRAINT fk_purchase_order_item_purchase_order
        FOREIGN KEY (purchase_order_id)
        REFERENCES purchase_order (purchase_order_id)
        ON UPDATE CASCADE,
    CONSTRAINT fk_purchase_order_item_part
        FOREIGN KEY (part_id)
        REFERENCES part (part_id)
        ON UPDATE CASCADE,
    CONSTRAINT ck_purchase_order_item_quantity_ordered_positive
        CHECK (quantity_ordered > 0),
    CONSTRAINT ck_purchase_order_item_quantity_received_valid
        CHECK (quantity_received >= 0 AND quantity_received <= quantity_ordered),
    CONSTRAINT ck_purchase_order_item_unit_cost_non_negative
        CHECK (unit_cost >= 0)
);

CREATE TABLE return_order (
    return_order_id integer GENERATED ALWAYS AS IDENTITY,
    sales_order_id integer NOT NULL,
    return_date date NOT NULL DEFAULT CURRENT_DATE,
    reason varchar(250) NOT NULL,
    resolution varchar(250),
    status varchar(20) NOT NULL DEFAULT 'requested',

    CONSTRAINT pk_return_order PRIMARY KEY (return_order_id),
    CONSTRAINT fk_return_order_sales_order
        FOREIGN KEY (sales_order_id)
        REFERENCES sales_order (sales_order_id)
        ON UPDATE CASCADE,
    CONSTRAINT ck_return_order_status
        CHECK (status IN ('requested', 'approved', 'rejected', 'completed'))
);

CREATE TABLE return_order_item (
    return_order_item_id integer GENERATED ALWAYS AS IDENTITY,
    return_order_id integer NOT NULL,
    sales_order_item_id integer NOT NULL,
    quantity integer NOT NULL,
    refund_amount numeric(12, 2) NOT NULL DEFAULT 0,
    restock_allowed boolean NOT NULL DEFAULT false,

    CONSTRAINT pk_return_order_item PRIMARY KEY (return_order_item_id),
    CONSTRAINT fk_return_order_item_return_order
        FOREIGN KEY (return_order_id)
        REFERENCES return_order (return_order_id)
        ON UPDATE CASCADE,
    CONSTRAINT fk_return_order_item_sales_order_item
        FOREIGN KEY (sales_order_item_id)
        REFERENCES sales_order_item (sales_order_item_id)
        ON UPDATE CASCADE,
    CONSTRAINT ck_return_order_item_quantity_positive
        CHECK (quantity > 0),
    CONSTRAINT ck_return_order_item_refund_amount_non_negative
        CHECK (refund_amount >= 0)
);

CREATE INDEX ix_part_part_category_id
    ON part (part_category_id);

CREATE INDEX ix_part_compatibility_vehicle_model_id
    ON part_compatibility (vehicle_model_id);

CREATE INDEX ix_sales_order_customer_id
    ON sales_order (customer_id);

CREATE INDEX ix_sales_order_item_sales_order_id
    ON sales_order_item (sales_order_id);

CREATE INDEX ix_sales_order_item_part_id
    ON sales_order_item (part_id);

CREATE INDEX ix_payment_sales_order_id
    ON payment (sales_order_id);

CREATE INDEX ix_purchase_order_supplier_id
    ON purchase_order (supplier_id);

CREATE INDEX ix_purchase_order_item_purchase_order_id
    ON purchase_order_item (purchase_order_id);

CREATE INDEX ix_purchase_order_item_part_id
    ON purchase_order_item (part_id);

CREATE INDEX ix_return_order_sales_order_id
    ON return_order (sales_order_id);

CREATE INDEX ix_return_order_item_return_order_id
    ON return_order_item (return_order_id);

CREATE INDEX ix_return_order_item_sales_order_item_id
    ON return_order_item (sales_order_item_id);

COMMIT;
