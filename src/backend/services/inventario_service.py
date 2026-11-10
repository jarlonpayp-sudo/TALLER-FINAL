from database.connection import get_db

class InventarioService:
    @staticmethod
    def obtener_alertas():
        """
        Retorna los repuestos cuyas existencias sean menores o iguales al stock mínimo configurado en MySQL (RF-04, RF-11).
        """
        conn = get_db()
        cursor = conn.cursor()
        query = """
        SELECT r.id, r.codigo_referencia, r.nombre, r.stock_actual, r.stock_minimo,
               c.nombre as categoria_nombre,
               CASE 
                   WHEN r.stock_actual = 0 THEN 'AGOTADO'
                   ELSE 'STOCK_BAJO'
               END as nivel_alerta
        FROM repuestos r
        JOIN categorias c ON r.categoria_id = c.id
        WHERE r.activo = 1 AND r.stock_actual <= r.stock_minimo
        ORDER BY r.stock_actual ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def ajustar_stock(repuesto_id, cantidad_cambio, tipo_movimiento, usuario_id=1, justificacion=""):
        """
        Ajusta el stock físico y registra el movimiento de auditoría en MySQL (RF-06, RF-07, RF-18).
        Garantiza que el saldo resultante nunca sea negativo.
        """
        conn = get_db()
        cursor = conn.cursor()

        # 1. Obtener stock actual
        select_q = "SELECT stock_actual, nombre FROM repuestos WHERE id = %s AND activo = 1"
        cursor.execute(select_q, (repuesto_id,))
        producto = cursor.fetchone()

        if not producto:
            cursor.close()
            conn.close()
            raise ValueError(f"El repuesto con ID {repuesto_id} no existe o está inactivo.")

        stock_anterior = producto["stock_actual"]
        stock_nuevo = stock_anterior + cantidad_cambio

        # Validación Anti-Sobrevanta
        if stock_nuevo < 0:
            cursor.close()
            conn.close()
            raise ValueError(f"Operación rechazada: existencia insuficiente. Saldo actual: {stock_anterior}, requerido: {abs(cantidad_cambio)}")

        # 2. Actualizar existencias
        update_q = "UPDATE repuestos SET stock_actual = %s WHERE id = %s"
        cursor.execute(update_q, (stock_nuevo, repuesto_id))

        # 3. Registrar auditoría
        audit_q = """
        INSERT INTO auditoria_movimientos (repuesto_id, usuario_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, justificacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(audit_q, (repuesto_id, usuario_id, tipo_movimiento, cantidad_cambio, stock_anterior, stock_nuevo, justificacion))
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "repuesto_id": repuesto_id,
            "stock_anterior": stock_anterior,
            "stock_nuevo": stock_nuevo,
            "cambio": cantidad_cambio
        }
