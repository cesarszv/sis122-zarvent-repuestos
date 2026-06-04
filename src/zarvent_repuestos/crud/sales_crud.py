"""CRUD and transactional operations for sales orders, items, payments, and dashboard metrics."""

import datetime
import mysql.connector
from typing import List, Optional, Dict, Any

from zarvent_repuestos.database.connection import get_database_connection


def crear_orden_venta(customer_id: int, items: List[Dict[str, Any]], payment_method: str) -> Optional[int]:
    """
    Creates a sales order, registers items, updates stock, and registers the payment.
    All operations are atomic and run under a single transaction.
    
    `items` format: [{"part_id": 1, "quantity": 2, "unit_price": 12.00, "discount_amount": 0.00}]
    """
    if not items:
        print("❌ No se enviaron ítems en la venta.")
        return None

    conexion = get_database_connection()
    cursor = conexion.cursor()
    
    # Calculate amounts
    subtotal = 0.0
    discount_total = 0.0
    for item in items:
        qty = int(item["quantity"])
        price = float(item["unit_price"])
        disc = float(item.get("discount_amount", 0.0))
        subtotal += price * qty
        discount_total += disc * qty
        
    total_amount = subtotal - discount_total
    order_date = datetime.date.today()
    
    try:
        # 1. Verify and lock stock for all items
        for item in items:
            part_id = int(item["part_id"])
            qty_needed = int(item["quantity"])
            
            cursor.execute(
                "SELECT quantity_on_hand FROM inventory_stock WHERE part_id = %s FOR UPDATE",
                (part_id,)
            )
            stock_row = cursor.fetchone()
            if not stock_row:
                raise ValueError(f"El producto con ID {part_id} no está registrado en el inventario.")
                
            qty_available = stock_row[0]
            if qty_available < qty_needed:
                raise ValueError(
                    f"Stock insuficiente para el producto ID {part_id}. "
                    f"Disponible: {qty_available}, Solicitado: {qty_needed}."
                )

        # 2. Insert Sales Order
        sql_order = """
        INSERT INTO sales_order (customer_id, order_date, status, subtotal, discount_amount, total_amount)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_order, (customer_id, order_date, "Paid", subtotal, discount_total, total_amount))
        sales_order_id = cursor.lastrowid

        # 3. Insert Items and Deduct Stock
        sql_item = """
        INSERT INTO sales_order_item (sales_order_id, part_id, quantity, unit_price, discount_amount)
        VALUES (%s, %s, %s, %s, %s)
        """
        sql_deduct = """
        UPDATE inventory_stock 
        SET quantity_on_hand = quantity_on_hand - %s
        WHERE part_id = %s
        """
        
        for item in items:
            part_id = int(item["part_id"])
            qty = int(item["quantity"])
            price = float(item["unit_price"])
            disc = float(item.get("discount_amount", 0.0))
            
            # Insert item line
            cursor.execute(sql_item, (sales_order_id, part_id, qty, price, disc))
            # Deduct inventory stock
            cursor.execute(sql_deduct, (qty, part_id))

        # 4. Insert Payment
        sql_payment = """
        INSERT INTO payment (sales_order_id, payment_date, method, amount, reference_number, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        ref_num = f"PAY-{sales_order_id}-{datetime.datetime.now().strftime('%M%S')}"
        cursor.execute(sql_payment, (sales_order_id, order_date, payment_method, total_amount, ref_num, "Completed"))

        conexion.commit()
        print(f"✅ Venta #{sales_order_id} guardada con éxito.")
        return sales_order_id
        
    except (mysql.connector.Error, ValueError) as err:
        conexion.rollback()
        print("❌ Error en la transacción de venta:", err)
        raise err
    finally:
        cursor.close()
        conexion.close()


def listar_ordenes_venta(status: Optional[str] = None, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all sales orders with customer and billing information, applying filters."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    
    sql = """
    SELECT o.sales_order_id, o.order_date, o.status, o.subtotal, o.discount_amount, o.total_amount,
           c.billing_name, c.tax_id, p.first_name, p.last_name
    FROM sales_order o
    JOIN customer c ON o.customer_id = c.customer_id
    JOIN person p ON c.person_id = p.person_id
    WHERE 1=1
    """
    params = []
    
    if status and status != "All Orders":
        sql += " AND o.status = %s"
        params.append(status)
        
    if start_date:
        sql += " AND o.order_date >= %s"
        params.append(start_date)
        
    if end_date:
        sql += " AND o.order_date <= %s"
        params.append(end_date)
        
    sql += " ORDER BY o.sales_order_id DESC"
    
    orders = []
    try:
        cursor.execute(sql, tuple(params))
        orders = cursor.fetchall()
    except mysql.connector.Error as err:
        print("❌ Error al listar ventas:", err)
    finally:
        cursor.close()
        conexion.close()
    return orders


def obtener_detalles_orden(sales_order_id: int) -> Optional[Dict[str, Any]]:
    """Returns details of a specific sales order and all its list items."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    
    sql_order = """
    SELECT o.sales_order_id, o.order_date, o.status, o.subtotal, o.discount_amount, o.total_amount,
           c.billing_name, c.tax_id, p.phone, p.email, p.address
    FROM sales_order o
    JOIN customer c ON o.customer_id = c.customer_id
    JOIN person p ON c.person_id = p.person_id
    WHERE o.sales_order_id = %s
    """
    
    sql_items = """
    SELECT i.sales_order_item_id, i.quantity, i.unit_price, i.discount_amount,
           p.internal_code, p.name, p.brand
    FROM sales_order_item i
    JOIN part p ON i.part_id = p.part_id
    WHERE i.sales_order_id = %s
    """
    
    try:
        # Fetch order header
        cursor.execute(sql_order, (sales_order_id,))
        order = cursor.fetchone()
        if not order:
            return None
            
        # Fetch items
        cursor.execute(sql_items, (sales_order_id,))
        order["items"] = cursor.fetchall()
        
        return order
    except mysql.connector.Error as err:
        print("❌ Error al obtener detalles de venta:", err)
        return None
    finally:
        cursor.close()
        conexion.close()


def obtener_metricas_dashboard() -> Dict[str, Any]:
    """Calculates all key metrics for the operational overview dashboard."""
    conexion = get_database_connection()
    cursor = conexion.cursor()
    
    metrics = {
        "today_sales_amount": 0.0,
        "categories_count": 0,
        "low_stock_count": 0,
        "total_orders_count": 0,
        "recent_orders": [],
        "low_stock_items": []
    }
    
    try:
        # 1. Today's sales amount
        cursor.execute(
            "SELECT COALESCE(SUM(total_amount), 0.0) FROM sales_order "
            "WHERE order_date = CURDATE() AND status != 'Cancelled'"
        )
        row = cursor.fetchone()
        metrics["today_sales_amount"] = float(row[0]) if row else 0.0
        
        # 2. Categories count
        cursor.execute("SELECT COUNT(*) FROM part_category")
        row = cursor.fetchone()
        metrics["categories_count"] = row[0] if row else 0
        
        # 3. Low stock count
        cursor.execute(
            "SELECT COUNT(*) FROM inventory_stock WHERE quantity_on_hand <= reorder_level"
        )
        row = cursor.fetchone()
        metrics["low_stock_count"] = row[0] if row else 0
        
        # 4. Total orders count
        cursor.execute("SELECT COUNT(*) FROM sales_order")
        row = cursor.fetchone()
        metrics["total_orders_count"] = row[0] if row else 0
        
        # 5. Recent orders (last 5)
        cursor.close() # Refresh to fetch dict cursor
        cursor = conexion.cursor(dictionary=True)
        
        sql_recent = """
        SELECT o.sales_order_id, o.order_date, o.status, o.total_amount, c.billing_name
        FROM sales_order o
        JOIN customer c ON o.customer_id = c.customer_id
        ORDER BY o.sales_order_id DESC LIMIT 5
        """
        cursor.execute(sql_recent)
        metrics["recent_orders"] = cursor.fetchall()
        
        # 6. Low stock items (first 5)
        sql_low = """
        SELECT p.internal_code, p.name, p.brand, s.quantity_on_hand, s.reorder_level
        FROM part p
        JOIN inventory_stock s ON p.part_id = s.part_id
        WHERE s.quantity_on_hand <= s.reorder_level
        ORDER BY s.quantity_on_hand ASC LIMIT 5
        """
        cursor.execute(sql_low)
        metrics["low_stock_items"] = cursor.fetchall()

    except mysql.connector.Error as err:
        print("❌ Error al obtener métricas del dashboard:", err)
    finally:
        cursor.close()
        conexion.close()
        
    return metrics
