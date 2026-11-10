import os
import sys
import pytest
import pymysql

# Agregar la ruta del backend al PATH de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

from app import create_app

class FakeMySQLCursor:
    def __init__(self, db_state):
        self.db = db_state
        self.lastrowid = None
        self.rowcount = 0
        self._last_result = None

    def execute(self, query, params=None):
        params = params or ()
        q = query.strip()

        # SELECT usuarios (Login)
        if q.startswith("SELECT u.id, u.nombre, u.email, u.password_hash"):
            email = params[0]
            user = next((u for u in self.db["usuarios"] if u["email"] == email), None)
            self._last_result = user
            self.rowcount = 1 if user else 0

        # SELECT repuestos (Listar / Buscar)
        elif q.startswith("SELECT r.*, c.nombre as categoria_nombre FROM repuestos r"):
            cat_map = {c["id"]: c["nombre"] for c in self.db["categorias"]}
            res = []
            for r in self.db["repuestos"]:
                if not r.get("activo", 1):
                    continue
                # Filtro por id
                if "WHERE r.id = %s" in q and r["id"] != params[0]:
                    continue
                # Filtro por búsqueda
                if "r.nombre LIKE %s" in q:
                    filtro = params[0].replace("%", "").lower()
                    if filtro not in r["nombre"].lower() and filtro not in r["codigo_referencia"].lower() and filtro not in r.get("codigo_oem", "").lower():
                        continue
                item = dict(r)
                item["categoria_nombre"] = cat_map.get(r["categoria_id"], "General")
                res.append(item)
            
            if "WHERE r.id = %s" in q:
                self._last_result = res[0] if res else None
            else:
                self._last_result = res
            self.rowcount = len(res)

        # SELECT alertas de stock
        elif "WHERE r.activo = 1 AND r.stock_actual <= r.stock_minimo" in q:
            cat_map = {c["id"]: c["nombre"] for c in self.db["categorias"]}
            alertas = []
            for r in self.db["repuestos"]:
                if r.get("activo", 1) and r["stock_actual"] <= r["stock_minimo"]:
                    item = dict(r)
                    item["categoria_nombre"] = cat_map.get(r["categoria_id"], "General")
                    item["nivel_alerta"] = "AGOTADO" if r["stock_actual"] == 0 else "STOCK_BAJO"
                    alertas.append(item)
            self._last_result = alertas
            self.rowcount = len(alertas)

        # SELECT repuesto por id (para ajuste o venta)
        elif q.startswith("SELECT stock_actual, nombre FROM repuestos") or q.startswith("SELECT id, nombre, precio_venta, stock_actual FROM repuestos"):
            rep_id = params[0]
            prod = next((r for r in self.db["repuestos"] if r["id"] == rep_id and r.get("activo", 1)), None)
            self._last_result = prod
            self.rowcount = 1 if prod else 0

        # Check unicidad código
        elif q.startswith("SELECT id FROM repuestos WHERE codigo_referencia = %s"):
            codigo = params[0]
            prod = next((r for r in self.db["repuestos"] if r["codigo_referencia"] == codigo), None)
            self._last_result = prod
            self.rowcount = 1 if prod else 0

        # INSERT repuestos
        elif q.startswith("INSERT INTO repuestos"):
            cat_id, cod, oem, nom, marca, p_comp, p_vent, stock, s_min = params
            nuevo_id = max([r["id"] for r in self.db["repuestos"]], default=0) + 1
            nuevo_rep = {
                "id": nuevo_id,
                "categoria_id": cat_id,
                "codigo_referencia": cod,
                "codigo_oem": oem,
                "nombre": nom,
                "marca_moto": marca,
                "precio_compra": p_comp,
                "precio_venta": p_vent,
                "stock_actual": stock,
                "stock_minimo": s_min,
                "activo": 1
            }
            self.db["repuestos"].append(nuevo_rep)
            self.lastrowid = nuevo_id
            self.rowcount = 1

        # UPDATE stock repuestos
        elif q.startswith("UPDATE repuestos SET stock_actual = %s WHERE id = %s"):
            nuevo_stock, rep_id = params
            prod = next((r for r in self.db["repuestos"] if r["id"] == rep_id), None)
            if prod:
                prod["stock_actual"] = nuevo_stock
                self.rowcount = 1

        # UPDATE activo repuestos (desactivación lógica)
        elif q.startswith("UPDATE repuestos SET activo = 0 WHERE id = %s"):
            rep_id = params[0]
            prod = next((r for r in self.db["repuestos"] if r["id"] == rep_id), None)
            if prod:
                prod["activo"] = 0
                self.rowcount = 1

        # INSERT ventas
        elif q.startswith("INSERT INTO ventas"):
            u_id, n_fac, sub, iva, tot, notas = params
            v_id = max([v["id"] for v in self.db["ventas"]], default=0) + 1
            self.db["ventas"].append({
                "id": v_id,
                "usuario_id": u_id,
                "numero_factura": n_fac,
                "subtotal": sub,
                "iva": iva,
                "total": tot,
                "estado": "COMPLETADA",
                "notas": notas
            })
            self.lastrowid = v_id
            self.rowcount = 1

        # INSERT detalle_ventas
        elif q.startswith("INSERT INTO detalle_ventas"):
            v_id, r_id, cant, p_u, sub = params
            self.db["detalle_ventas"].append({
                "id": len(self.db["detalle_ventas"]) + 1,
                "venta_id": v_id,
                "repuesto_id": r_id,
                "cantidad": cant,
                "precio_unitario": p_u,
                "subtotal": sub
            })
            self.rowcount = 1

        # INSERT auditoria_movimientos
        elif q.startswith("INSERT INTO auditoria_movimientos"):
            self.rowcount = 1

    def fetchone(self):
        return self._last_result

    def fetchall(self):
        return self._last_result if isinstance(self._last_result, list) else []

    def close(self):
        pass

class FakeMySQLConnection:
    def __init__(self, db_state):
        self.db = db_state

    def cursor(self):
        return FakeMySQLCursor(self.db)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

_shared_test_state = {
    "roles": [
        {"id": 1, "nombre": "ADMIN"},
        {"id": 2, "nombre": "VENDEDOR"},
        {"id": 3, "nombre": "INVENTARIO"}
    ],
    "usuarios": [
        {"id": 1, "rol_id": 1, "rol": "ADMIN", "nombre": "Alejandro Londoño", "email": "admin@allquality.com", "password_hash": "Admin123*", "activo": 1},
        {"id": 2, "rol_id": 2, "rol": "VENDEDOR", "nombre": "Cristian Carabalí", "email": "vendedor@allquality.com", "password_hash": "Admin123*", "activo": 1}
    ],
    "categorias": [
        {"id": 1, "nombre": "Frenos"},
        {"id": 2, "nombre": "Motor y Transmisión"},
        {"id": 3, "nombre": "Eléctrico"},
        {"id": 4, "nombre": "Lubricantes y Químicos"}
    ],
    "repuestos": [
        {"id": 1, "categoria_id": 1, "codigo_referencia": "PAST-FR-FZ16", "codigo_oem": "OEM-54B-W0045-00", "nombre": "Pastillas de Freno Delanteras Yamaha FZ16", "marca_moto": "Yamaha FZ16", "precio_compra": 18000.0, "precio_venta": 32000.0, "stock_actual": 12, "stock_minimo": 3, "activo": 1},
        {"id": 2, "categoria_id": 1, "codigo_referencia": "BND-TR-GN125", "codigo_oem": "OEM-64410-05300", "nombre": "Bandas de Freno Traseras Suzuki GN125", "marca_moto": "Suzuki GN125", "precio_compra": 12000.0, "precio_venta": 22000.0, "stock_actual": 2, "stock_minimo": 4, "activo": 1},
        {"id": 3, "categoria_id": 2, "codigo_referencia": "KIT-ARR-PULSAR200", "codigo_oem": "OEM-36DK0012", "nombre": "Kit de Arrastre Reforzado Bajaj Pulsar 200 NS", "marca_moto": "Bajaj Pulsar NS200", "precio_compra": 75000.0, "precio_venta": 125000.0, "stock_actual": 8, "stock_minimo": 2, "activo": 1},
        {"id": 4, "categoria_id": 3, "codigo_referencia": "BUJ-NGK-CR8E", "codigo_oem": "NGK-1275", "nombre": "Bujía Estándar NGK CR8E", "marca_moto": "Universal", "precio_compra": 9000.0, "precio_venta": 16000.0, "stock_actual": 25, "stock_minimo": 5, "activo": 1}
    ],
    "ventas": [],
    "detalle_ventas": [],
    "auditoria_movimientos": []
}

@pytest.fixture(autouse=True)
def mock_mysql_connection(monkeypatch):
    """
    Emula la conexión de PyMySQL en memoria para pruebas rápidas y deterministas
    sin necesidad de requerir el servicio MySQL encendido durante la suite.
    """
    monkeypatch.setattr(pymysql, "connect", lambda *args, **kwargs: FakeMySQLConnection(_shared_test_state))

@pytest.fixture
def app():
    application = create_app({"TESTING": True})
    return application

@pytest.fixture
def client(app):
    return app.test_client()
