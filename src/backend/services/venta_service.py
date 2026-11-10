import time
import random
from database.connection import get_db

class VentaService:
    @staticmethod
    def registrar_venta(usuario_id, items, notas=""):
        """
        Registra una venta de mostrador de forma atómica en MySQL (ACID).
        Verifica existencias disponibles para todos los repuestos (RF-05, RF-06, RF-07).
        Si falta stock en un solo producto, aborta toda la transacción.
        """
        if not items or not isinstance(items, list):
            raise ValueError("El carrito de venta debe contener al menos un producto.")

        conn = get_db()
        cursor = conn.cursor()

        try:
            detalles_procesados = []
            subtotal_total = 0.0

            for item in items:
                repuesto_id = item.get("repuesto_id")
                cantidad = item.get("cantidad")

                if not repuesto_id or not cantidad or int(cantidad) <= 0:
                    raise ValueError("Cada producto debe tener un ID válido y cantidad mayor a cero.")

                cantidad = int(cantidad)

                # Consultar repuesto
                select_q = "SELECT id, nombre, precio_venta, stock_actual FROM repuestos WHERE id = %s AND activo = 1 FOR UPDATE"
                cursor.execute(select_q, (repuesto_id,))
                producto = cursor.fetchone()

                if not producto:
                    raise ValueError(f"El repuesto con ID {repuesto_id} no existe o no está activo.")

                p_id = producto["id"]
                p_nombre = producto["nombre"]
                precio_unitario = float(producto["precio_venta"])
                stock_actual = int(producto["stock_actual"])

                # Validación Anti-Sobrevanta estricta
                if cantidad > stock_actual:
                    raise ValueError(f"Stock insuficiente para '{p_nombre}': quedan {stock_actual} unidades y solicitó {cantidad}.")

                subtotal_item = round(precio_unitario * cantidad, 2)
                subtotal_total += subtotal_item

                detalles_procesados.append({
                    "repuesto_id": p_id,
                    "nombre": p_nombre,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal_item,
                    "stock_anterior": stock_actual,
                    "stock_nuevo": stock_actual - cantidad
                })

            # Generar número de factura único
            num_factura = f"FAC-{int(time.time())}-{random.randint(100, 999)}"
            total = subtotal_total

            # Insertar cabecera de venta
            insert_venta = """
            INSERT INTO ventas (usuario_id, numero_factura, subtotal, iva, total, estado, notas)
            VALUES (%s, %s, %s, %s, %s, 'COMPLETADA', %s)
            """
            cursor.execute(insert_venta, (usuario_id, num_factura, subtotal_total, 0.0, total, notas))
            venta_id = cursor.lastrowid

            # Insertar detalles y descontar inventario
            insert_det = """
            INSERT INTO detalle_ventas (venta_id, repuesto_id, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
            """
            update_stock = "UPDATE repuestos SET stock_actual = %s WHERE id = %s"
            insert_audit = """
            INSERT INTO auditoria_movimientos (repuesto_id, usuario_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, justificacion)
            VALUES (%s, %s, 'VENTA', %s, %s, %s, %s)
            """

            for d in detalles_procesados:
                cursor.execute(insert_det, (venta_id, d["repuesto_id"], d["cantidad"], d["precio_unitario"], d["subtotal"]))
                cursor.execute(update_stock, (d["stock_nuevo"], d["repuesto_id"]))
                cursor.execute(insert_audit, (
                    d["repuesto_id"],
                    usuario_id,
                    -d["cantidad"],
                    d["stock_anterior"],
                    d["stock_nuevo"],
                    f"Venta confirmada {num_factura}"
                ))

            # Confirmar transacción atómica en MySQL
            conn.commit()

            return {
                "venta_id": venta_id,
                "numero_factura": num_factura,
                "total": total,
                "items_vendidos": len(detalles_procesados),
                "detalles": detalles_procesados
            }

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_venta(venta_id):
        conn = get_db()
        cursor = conn.cursor()

        query_v = "SELECT v.*, u.nombre as vendedor_nombre FROM ventas v JOIN usuarios u ON v.usuario_id = u.id WHERE v.id = %s"
        query_d = "SELECT d.*, r.nombre, r.codigo_referencia FROM detalle_ventas d JOIN repuestos r ON d.repuesto_id = r.id WHERE d.venta_id = %s"

        cursor.execute(query_v, (venta_id,))
        venta = cursor.fetchone()
        if not venta:
            cursor.close()
            conn.close()
            return None

        cursor.execute(query_d, (venta_id,))
        detalles = cursor.fetchall()
        cursor.close()
        conn.close()

        venta["items"] = detalles
        return venta
