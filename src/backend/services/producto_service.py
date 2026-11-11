from database.connection import get_db

class ProductoService:
    @staticmethod
    def listar(q=None, categoria_id=None):
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT r.*, c.nombre as categoria_nombre FROM repuestos r JOIN categorias c ON r.categoria_id = c.id WHERE r.activo = 1"
        params = []

        if q:
            query += " AND (r.nombre LIKE %s OR r.codigo_referencia LIKE %s OR r.codigo_oem LIKE %s)"
            param_q = f"%{q}%"
            params.extend([param_q, param_q, param_q])
            
        if categoria_id:
            query += " AND r.categoria_id = %s"
            params.append(categoria_id)

        query += " ORDER BY r.nombre ASC"
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def obtener_por_id(producto_id):
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT r.*, c.nombre as categoria_nombre FROM repuestos r JOIN categorias c ON r.categoria_id = c.id WHERE r.id = %s"
        cursor.execute(query, (producto_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    @staticmethod
    def crear(data):
        codigo = data.get("codigo_referencia", "").strip()
        nombre = data.get("nombre", "").strip()
        categoria_id = data.get("categoria_id")
        precio_venta = data.get("precio_venta")
        stock_actual = data.get("stock_actual", 0)
        stock_minimo = data.get("stock_minimo", 3)

        if not codigo or not nombre or not categoria_id:
            raise ValueError("Los campos código, nombre y categoría son obligatorios.")
        if "stock_actual" not in data:
            raise ValueError("Las existencias iniciales son obligatorias.")

        try:
            precio_venta = float(precio_venta)
            if precio_venta <= 0:
                raise ValueError("El precio de venta debe ser un número estrictamente mayor a 0.")
        except (TypeError, ValueError):
            raise ValueError("El precio de venta debe ser un número válido mayor a 0.")

        try:
            stock_actual = int(stock_actual)
            stock_minimo = int(stock_minimo)
            if stock_actual < 0 or stock_minimo < 0:
                raise ValueError("Las existencias y el stock mínimo no pueden ser números negativos.")
        except (TypeError, ValueError):
            raise ValueError("El stock debe ser un valor entero no negativo.")

        conn = get_db()
        cursor = conn.cursor()

        # Verificar unicidad de código de referencia (RF-02)
        check_query = "SELECT id FROM repuestos WHERE codigo_referencia = %s"
        cursor.execute(check_query, (codigo,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise KeyError(f"El código de referencia '{codigo}' ya está registrado.")

        insert_query = """
        INSERT INTO repuestos (categoria_id, codigo_referencia, codigo_oem, nombre, marca_moto, precio_compra, precio_venta, stock_actual, stock_minimo, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """
        params = (
            categoria_id,
            codigo,
            data.get("codigo_oem", ""),
            nombre,
            data.get("marca_moto", ""),
            float(data.get("precio_compra", 0.0)),
            precio_venta,
            stock_actual,
            stock_minimo
        )
        cursor.execute(insert_query, params)
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return ProductoService.obtener_por_id(nuevo_id)

    @staticmethod
    def actualizar(producto_id, data):
        codigo = data.get("codigo_referencia", "").strip()
        nombre = data.get("nombre", "").strip()
        categoria_id = data.get("categoria_id")
        precio_venta = data.get("precio_venta")
        precio_compra = data.get("precio_compra", 0)
        stock_minimo = data.get("stock_minimo", 3)

        if not codigo or not nombre or not categoria_id:
            raise ValueError("Los campos código, nombre y categoría son obligatorios.")

        try:
            precio_venta = float(precio_venta)
            precio_compra = float(precio_compra)
            stock_minimo = int(stock_minimo)
        except (TypeError, ValueError):
            raise ValueError("Los precios y el stock mínimo deben ser valores numéricos.")

        if precio_venta <= 0:
            raise ValueError("El precio de venta debe ser un número estrictamente mayor a 0.")
        if precio_compra < 0:
            raise ValueError("El precio de compra no puede ser negativo.")
        if stock_minimo < 0:
            raise ValueError("El stock mínimo no puede ser negativo.")

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id FROM repuestos WHERE id = %s", (producto_id,))
            if not cursor.fetchone():
                raise LookupError("Repuesto no encontrado.")

            cursor.execute(
                "SELECT id FROM repuestos WHERE codigo_referencia = %s",
                (codigo,)
            )
            existente = cursor.fetchone()
            if existente and existente["id"] != producto_id:
                raise KeyError(f"El código de referencia '{codigo}' ya está registrado.")

            cursor.execute("""
                UPDATE repuestos
                SET categoria_id = %s,
                    codigo_referencia = %s,
                    codigo_oem = %s,
                    nombre = %s,
                    marca_moto = %s,
                    precio_compra = %s,
                    precio_venta = %s,
                    stock_minimo = %s
                WHERE id = %s
            """, (
                categoria_id,
                codigo,
                data.get("codigo_oem", ""),
                nombre,
                data.get("marca_moto", ""),
                precio_compra,
                precio_venta,
                stock_minimo,
                producto_id
            ))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return ProductoService.obtener_por_id(producto_id)

    @staticmethod
    def desactivar(producto_id):
        conn = get_db()
        cursor = conn.cursor()
        query = "UPDATE repuestos SET activo = 0 WHERE id = %s"
        cursor.execute(query, (producto_id,))
        filas = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return filas > 0
