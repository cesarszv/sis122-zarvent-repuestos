"""Seed mock data into the database to match the user's mockup views."""

import sys
import datetime
from pathlib import Path

import mysql.connector

# Ensure src/ is in the python path
SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from zarvent_repuestos.database.connection import get_database_connection
from zarvent_repuestos.crud import user_crud, part_crud, customer_crud, sales_crud
from zarvent_repuestos.models.part import Part


def main():
    print("🌱 Iniciando población de datos de prueba...")
    
    try:
        conexion = get_database_connection()
        conexion.close()
    except mysql.connector.Error as err:
        print("❌ ERROR: No se puede conectar a MySQL con las credenciales de .env.")
        print(err)
        return 1

    # 1. Seed admin user
    print("👤 Creando usuario administrador...")
    user_crud.crear_usuario("admin", "admin123")
    
    # 2. Seed Categories
    print("📦 Creando categorías de repuestos...")
    categories = [
        ("Engine Parts", "Componentes internos y auxiliares de motor (bujías, pistones, filtros)."),
        ("Transmission", "Cajas de cambio, embragues y transmisiones homocinéticas."),
        ("Electrical", "Alternadores, arrancadores, sensores y cableado eléctrico."),
        ("Suspension", "Amortiguadores, resortes, bandejas y rótulas de suspensión.")
    ]
    
    for name, desc in categories:
        part_crud.crear_categoria(name, desc)
        
    # Get created categories to associate parts
    cats = part_crud.listar_categorias()
    cat_map = {c.name: c.part_category_id for c in cats}
    
    # 3. Seed Products (Parts) & Stock
    print("⚙️ Creando repuestos y stock de inventario...")
    products = [
        {
            "name": "Oxygen Sensor (Lambda Probe)",
            "internal_code": "ZR-10492",
            "oem_code": "0258006028",
            "brand": "Bosch",
            "category": "Electrical",
            "sale_price": 124.50,
            "purchase_cost": 85.00,
            "stock": 42,
            "location": "Estante A-4"
        },
        {
            "name": "Spark Plug Standard",
            "internal_code": "ZR-29411",
            "oem_code": "BKR6E-11",
            "brand": "NGK",
            "category": "Engine Parts",
            "sale_price": 8.25,
            "purchase_cost": 4.50,
            "stock": 150,
            "location": "Pasillo 2 - Cajón 3"
        },
        {
            "name": "Clutch Kit 3-Piece",
            "internal_code": "ZR-55032",
            "oem_code": "826325",
            "brand": "Valeo",
            "category": "Transmission",
            "sale_price": 285.00,
            "purchase_cost": 190.00,
            "stock": 14,
            "location": "Área de Pesados B"
        },
        {
            "name": "Iridium TT Spark Plug",
            "internal_code": "ZR-88190",
            "oem_code": "IK20TT",
            "brand": "Denso",
            "category": "Engine Parts",
            "sale_price": 15.75,
            "purchase_cost": 9.00,
            "stock": 3,  # Low stock item
            "location": "Pasillo 2 - Cajón 5"
        },
        {
            "name": "Front Strut Mount",
            "internal_code": "ZR-11004",
            "oem_code": "31306781547",
            "brand": "OEM",
            "category": "Suspension",
            "sale_price": 45.20,
            "purchase_cost": 30.00,
            "stock": 28,
            "location": "Estante D-1"
        }
    ]
    
    for prod in products:
        p = Part(
            part_category_id=cat_map[prod["category"]],
            internal_code=prod["internal_code"],
            oem_code=prod["oem_code"],
            name=prod["name"],
            brand=prod["brand"],
            sale_price=prod["sale_price"],
            purchase_cost=prod["purchase_cost"],
            status="active"
        )
        part_crud.crear_producto(p, prod["stock"], prod["location"])

    # 4. Seed Customers
    print("👥 Creando clientes...")
    customers = [
        {"first_name": "Elena", "last_name": "Rostova", "id_num": "6704921", "billing": "Elena Rostova", "tax": "6704921"},
        {"first_name": "Marcus", "last_name": "Vance", "id_num": "9820381", "billing": "Marcus Vance", "tax": "9820381"},
        {"first_name": "Silvia", "last_name": "Plath", "id_num": "5639103", "billing": "Silvia Plath", "tax": "5639103"},
        {"first_name": "Julian", "last_name": "Black", "id_num": "4930219", "billing": "Julian Black", "tax": "4930219"}
    ]
    
    for cust in customers:
        customer_crud.crear_cliente(
            first_name=cust["first_name"],
            last_name=cust["last_name"],
            identity_number=cust["id_num"],
            billing_name=cust["billing"],
            tax_id=cust["tax"]
        )
        
    # Get created parts and customers to place sales orders
    catalog = part_crud.listar_productos()
    part_map = {p["internal_code"]: p["part_id"] for p in catalog}
    
    cust_list = customer_crud.listar_clientes()
    cust_map = {c["first_name"]: c["customer_id"] for c in cust_list}
    
    # 5. Seed Orders (Sales & Payments)
    print("💰 Creando ventas históricas...")
    
    # Order 1: Elena Rostova ($1,240.00)
    # We will buy 4 Clutch Kits ($285.00 * 4 = $1,140) and 8 Spark Plugs ($8.25 * 8 = $66) + some oxygen sensors to total around $1,240
    # Let's seed it directly:
    sales_crud.crear_orden_venta(
        customer_id=cust_map["Elena"],
        items=[
            {"part_id": part_map["ZR-55032"], "quantity": 4, "unit_price": 285.00, "discount_amount": 0.0},
            {"part_id": part_map["ZR-29411"], "quantity": 8, "unit_price": 8.25, "discount_amount": 0.0},
            {"part_id": part_map["ZR-11004"], "quantity": 1, "unit_price": 45.20, "discount_amount": 0.0}
        ],
        payment_method="Transferencia"
    )
    
    # Order 2: Marcus Vance ($450.50)
    sales_crud.crear_orden_venta(
        customer_id=cust_map["Marcus"],
        items=[
            {"part_id": part_map["ZR-10492"], "quantity": 3, "unit_price": 124.50, "discount_amount": 0.0},
            {"part_id": part_map["ZR-11004"], "quantity": 1, "unit_price": 45.20, "discount_amount": 0.0},
            {"part_id": part_map["ZR-29411"], "quantity": 4, "unit_price": 8.25, "discount_amount": 0.0}
        ],
        payment_method="Efectivo"
    )
    
    # Order 3: Julian Black ($2,100.00)
    sales_crud.crear_orden_venta(
        customer_id=cust_map["Julian"],
        items=[
            {"part_id": part_map["ZR-55032"], "quantity": 7, "unit_price": 285.00, "discount_amount": 0.0},
            {"part_id": part_map["ZR-11004"], "quantity": 2, "unit_price": 45.20, "discount_amount": 0.0},
            {"part_id": part_map["ZR-10492"], "quantity": 1, "unit_price": 124.50, "discount_amount": 0.0}
        ],
        payment_method="Tarjeta de Crédito"
    )
    
    print("✅ Población de datos completada con éxito.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
