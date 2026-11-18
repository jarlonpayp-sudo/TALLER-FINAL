import copy
import os
import sys
import pytest
import pymysql

# Agregar la ruta del backend al PATH de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

from app import create_app
from auth_utils import create_token

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

        # SELECT usuarios (administración de colaboradores)
        elif q.startswith("SELECT u.id, u.nombre, u.email, u.rol_id, u.activo"):
            roles = {r["id"]: r["nombre"] for r in self.db["roles"]}
            usuarios = []
            for u in self.db["usuarios"]:
                item = dict(u)
                item.pop("password_hash", None)
                item["rol"] = roles.get(u["rol_id"], "SIN ROL")
                usuarios.append(item)
            if "WHERE u.id = %s" in q:
                usuario_id = params[0]
                self._last_result = next(
                    (u for u in usuarios if u["id"] == usuario_id), None
                )
            else:
                self._last_result = sorted(usuarios, key=lambda u: u["nombre"])
            self.rowcount = 1 if self._last_result else 0

        # SELECT roles (formulario de colaboradores)
        elif q.startswith("SELECT id, nombre, descripcion") and "FROM roles" in q:
            self._last_result = [dict(r) for r in self.db["roles"]]
            self.rowcount = len(self._last_result)

        # SELECT categorias (formulario de repuestos)
        elif q.startswith("SELECT id, nombre, descripcion") and "FROM categorias" in q:
            self._last_result = [dict(c) for c in self.db["categorias"]]
            self.rowcount = len(self._last_result)

        # Verificar rol de usuario
        elif q.startswith("SELECT id FROM roles WHERE id = %s"):
            rol_id = params[0]
            rol = next((r for r in self.db["roles"] if r["id"] == rol_id), None)
            self._last_result = {"id": rol["id"]} if rol else None
            self.rowcount = 1 if rol else 0

        # Verificar existencia de usuario
        elif q.startswith("SELECT id FROM usuarios WHERE id = %s"):
            usuario_id = params[0]
            usuario = next(
                (u for u in self.db["usuarios"] if u["id"] == usuario_id), None
            )
            self._last_result = {"id": usuario["id"]} if usuario else None
            self.rowcount = 1 if usuario else 0

        # Verificar estado activo, rol actual y rol_id del usuario para la sesión
        elif q.startswith("SELECT u.activo, u.rol_id, r.nombre AS rol"):
            usuario_id = params[0]
            roles = {r["id"]: r["nombre"] for r in self.db["roles"]}
            usuario = next(
                (u for u in self.db["usuarios"] if u["id"] == usuario_id), None
            )
            self._last_result = (
                {
                    "activo": usuario["activo"],
                    "rol_id": usuario["rol_id"],
                    "rol": roles.get(usuario["rol_id"], "SIN ROL"),
                }
                if usuario
                else None
            )
            self.rowcount = 1 if usuario else 0

        # Verificar correo único de usuario
        elif q.startswith("SELECT id FROM usuarios WHERE email = %s"):
            email = params[0]
            usuarios = [
                u for u in self.db["usuarios"]
                if u["email"].lower() == email.lower()
            ]
            if "AND id <> %s" in q and len(params) > 1:
                usuarios = [u for u in usuarios if u["id"] != params[1]]
            usuario = usuarios[0] if usuarios else None
            self._last_result = {"id": usuario["id"]} if usuario else None
            self.rowcount = 1 if usuario else 0

        # INSERT usuarios
        elif q.startswith("INSERT INTO usuarios"):
            nombre, email, password_hash, rol_id, activo = params
            nuevo_id = max([u["id"] for u in self.db["usuarios"]], default=0) + 1
            self.db["usuarios"].append({
                "id": nuevo_id,
                "rol_id": rol_id,
                "rol": next(
                    (r["nombre"] for r in self.db["roles"] if r["id"] == rol_id),
                    "SIN ROL",
                ),
                "nombre": nombre,
                "email": email,
                "password_hash": password_hash,
                "activo": activo,
            })
            self.lastrowid = nuevo_id
            self.rowcount = 1

        # UPDATE usuarios con contraseña
        elif q.startswith("UPDATE usuarios") and "password_hash = %s" in q:
            nombre, email, rol_id, activo, password_hash, usuario_id = params
            usuario = next(
                (u for u in self.db["usuarios"] if u["id"] == usuario_id), None
            )
            if usuario:
                usuario.update({
                    "nombre": nombre,
                    "email": email,
                    "rol_id": rol_id,
                    "activo": activo,
                    "password_hash": password_hash,
                })
                self.rowcount = 1

        # UPDATE usuarios sin contraseña
        elif q.startswith("UPDATE usuarios") and "SET nombre = %s" in q:
            nombre, email, rol_id, activo, usuario_id = params
            usuario = next(
                (u for u in self.db["usuarios"] if u["id"] == usuario_id), None
            )
            if usuario:
                usuario.update({
                    "nombre": nombre,
                    "email": email,
                    "rol_id": rol_id,
                    "activo": activo,
                })
                self.rowcount = 1

        # Suspender usuario
        elif q.startswith("UPDATE usuarios SET activo = 0 WHERE id = %s"):
            usuario_id = params[0]
            usuario = next(
                (u for u in self.db["usuarios"] if u["id"] == usuario_id), None
            )
            if usuario:
                usuario["activo"] = 0
                self.rowcount = 1

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

        # Verificar existencia de repuesto para actualización
        elif q.startswith("SELECT id FROM repuestos WHERE id = %s"):
            rep_id = params[0]
            prod = next((r for r in self.db["repuestos"] if r["id"] == rep_id), None)
            self._last_result = {"id": prod["id"]} if prod else None
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

        # UPDATE datos de catálogo del repuesto
        elif q.startswith("UPDATE repuestos") and "SET categoria_id = %s" in q:
            cat_id, cod, oem, nom, marca, p_comp, p_vent, s_min, rep_id = params
            prod = next((r for r in self.db["repuestos"] if r["id"] == rep_id), None)
            if prod:
                prod.update({
                    "categoria_id": cat_id,
                    "codigo_referencia": cod,
                    "codigo_oem": oem,
                    "nombre": nom,
                    "marca_moto": marca,
                    "precio_compra": p_comp,
                    "precio_venta": p_vent,
                    "stock_minimo": s_min
                })
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

        # SELECT listado de ventas
        elif q.startswith("SELECT v.id,") and "FROM ventas v" in q:
            ventas = []
            for venta in sorted(
                self.db["ventas"],
                key=lambda v: (v.get("created_at", ""), v["id"]),
                reverse=True
            ):
                usuario = next(
                    (u for u in self.db["usuarios"] if u["id"] == venta["usuario_id"]),
                    None
                )
                item = dict(venta)
                item["vendedor_nombre"] = usuario["nombre"] if usuario else "Desconocido"
                ventas.append(item)
            self._last_result = ventas[:int(params[0])] if params else ventas
            self.rowcount = len(self._last_result)

        # SELECT venta con vendedor (consulta de venta)
        elif q.startswith("SELECT v.*, u.nombre as vendedor_nombre FROM ventas v"):
            venta_id = params[0]
            venta = next((v for v in self.db["ventas"] if v["id"] == venta_id), None)
            if venta:
                usuario = next((u for u in self.db["usuarios"] if u["id"] == venta["usuario_id"]), None)
                item = dict(venta)
                item["vendedor_nombre"] = usuario["nombre"] if usuario else "Desconocido"
                self._last_result = item
            else:
                self._last_result = None
            self.rowcount = 1 if venta else 0

        # SELECT detalle de venta
        elif q.startswith("SELECT d.*, r.nombre, r.codigo_referencia FROM detalle_ventas d"):
            venta_id = params[0]
            rep_map = {r["id"]: r for r in self.db["repuestos"]}
            detalles = []
            for detalle in self.db["detalle_ventas"]:
                if detalle["venta_id"] == venta_id:
                    item = dict(detalle)
                    repuesto = rep_map.get(detalle["repuesto_id"], {})
                    item["nombre"] = repuesto.get("nombre", "Repuesto")
                    item["codigo_referencia"] = repuesto.get("codigo_referencia", "")
                    detalles.append(item)
            self._last_result = detalles
            self.rowcount = len(detalles)

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

_seed_test_state = {
    "roles": [
        {"id": 1, "nombre": "ADMIN"},
        {"id": 2, "nombre": "VENDEDOR"},
        {"id": 3, "nombre": "INVENTARIO"}
    ],
    "usuarios": [
        {"id": 1, "rol_id": 1, "rol": "ADMIN", "nombre": "Alejandro Londoño", "email": "admin@allquality.com", "password_hash": "pbkdf2:sha256:1000000$SSDmAem1zvm5BJlR$ef3fd42b108d997c03970069576a7e675685ed71853f2984aa81f65cdeeac4b1", "activo": 1},
        {"id": 2, "rol_id": 2, "rol": "VENDEDOR", "nombre": "Cristian Carabalí", "email": "vendedor@allquality.com", "password_hash": "pbkdf2:sha256:1000000$GL9QXf8uwKPxWPhM$6ef23813eba1d98c5a09f14d65c0b557ec1133582846a621e5babec3047e271c", "activo": 1},
        {"id": 3, "rol_id": 3, "rol": "INVENTARIO", "nombre": "Steven Rendón", "email": "bodega@allquality.com", "password_hash": "pbkdf2:sha256:1000000$Y83sSRiXGebBJGgk$bf15d53bcc456f364e00b5f3bf8222008b2cb9e15fb1ee6e876bf2b5ffa98d51", "activo": 1},
        {"id": 4, "rol_id": 3, "rol": "INVENTARIO", "nombre": "Usuario Inactivo", "email": "inactivo@allquality.com", "password_hash": "pbkdf2:sha256:1000000$Y83sSRiXGebBJGgk$bf15d53bcc456f364e00b5f3bf8222008b2cb9e15fb1ee6e876bf2b5ffa98d51", "activo": 0}
    ],
    "categorias": [
        {"id": 1, "nombre": "Frenos"},
        {"id": 2, "nombre": "Motor y Transmisión"},
        {"id": 3, "nombre": "Eléctrico"},
        {"id": 4, "nombre": "Lubricantes y Químicos"},
        {"id": 5, "nombre": "Accesorios"}
    ],
    "repuestos": [
        {"id": 1, "categoria_id": 1, "codigo_referencia": "PAST-FR-FZ16", "codigo_oem": "OEM-54B-W0045-00", "nombre": "Pastillas de Freno Delanteras Yamaha FZ16", "marca_moto": "Yamaha FZ16", "precio_compra": 18000.0, "precio_venta": 32000.0, "stock_actual": 12, "stock_minimo": 3, "activo": 1},
        {"id": 2, "categoria_id": 1, "codigo_referencia": "BND-TR-GN125", "codigo_oem": "OEM-64410-05300", "nombre": "Bandas de Freno Traseras Suzuki GN125", "marca_moto": "Suzuki GN125", "precio_compra": 12000.0, "precio_venta": 22000.0, "stock_actual": 2, "stock_minimo": 4, "activo": 1},
        {"id": 3, "categoria_id": 2, "codigo_referencia": "KIT-ARR-PULSAR200", "codigo_oem": "OEM-36DK0012", "nombre": "Kit de Arrastre Reforzado Bajaj Pulsar 200 NS", "marca_moto": "Bajaj Pulsar NS200", "precio_compra": 75000.0, "precio_venta": 125000.0, "stock_actual": 8, "stock_minimo": 2, "activo": 1},
        {"id": 4, "categoria_id": 3, "codigo_referencia": "BUJ-NGK-CR8E", "codigo_oem": "NGK-1275", "nombre": "Bujía Estándar NGK CR8E", "marca_moto": "Universal", "precio_compra": 9000.0, "precio_venta": 16000.0, "stock_actual": 25, "stock_minimo": 5, "activo": 1},
        {"id": 5, "categoria_id": 4, "codigo_referencia": "ACE-MOT-7100", "codigo_oem": "MOT-7100-10W40", "nombre": "Aceite 100% Sintético Motul 7100 10W40 1L", "marca_moto": "Universal 4T", "precio_compra": 42000.0, "precio_venta": 62000.0, "stock_actual": 1, "stock_minimo": 3, "activo": 1},
        {"id": 6, "categoria_id": 1, "codigo_referencia": "DISC-FR-PULSAR200", "codigo_oem": "OEM-36DK0013", "nombre": "Disco de Freno Delantero Bajaj Pulsar 200 NS", "marca_moto": "Bajaj Pulsar NS200", "precio_compra": 48000.0, "precio_venta": 82000.0, "stock_actual": 0, "stock_minimo": 2, "activo": 1},
        {"id": 7, "categoria_id": 2, "codigo_referencia": "CAD-520H-120", "codigo_oem": "OEM-520H120", "nombre": "Cadena de Transmisión 520H x 120 Eslabones", "marca_moto": "Universal 200cc-250cc", "precio_compra": 38000.0, "precio_venta": 68000.0, "stock_actual": 14, "stock_minimo": 4, "activo": 1},
        {"id": 8, "categoria_id": 3, "codigo_referencia": "BOB-CB190R", "codigo_oem": "OEM-30510-KWPB01", "nombre": "Bobina de Encendido Honda CB 190R", "marca_moto": "Honda CB 190R", "precio_compra": 28000.0, "precio_venta": 52000.0, "stock_actual": 11, "stock_minimo": 3, "activo": 1},
        {"id": 9, "categoria_id": 4, "codigo_referencia": "ACE-YAM-20W50", "codigo_oem": "YAM-20W50-1L", "nombre": "Aceite Semisintético Yamalube 20W50 1L", "marca_moto": "Universal 4T", "precio_compra": 24000.0, "precio_venta": 39000.0, "stock_actual": 20, "stock_minimo": 5, "activo": 1},
        {"id": 10, "categoria_id": 1, "codigo_referencia": "LIQ-FR-DOT4", "codigo_oem": "DOT4-500", "nombre": "Líquido de Frenos DOT 4 500 ml", "marca_moto": "Universal", "precio_compra": 14000.0, "precio_venta": 26000.0, "stock_actual": 18, "stock_minimo": 4, "activo": 1},
        {"id": 11, "categoria_id": 2, "codigo_referencia": "KIT-CIL-150", "codigo_oem": "OEM-150CIL", "nombre": "Kit de Cilindro y Pistón 150cc", "marca_moto": "Universal 150cc", "precio_compra": 85000.0, "precio_venta": 145000.0, "stock_actual": 6, "stock_minimo": 2, "activo": 1},
        {"id": 12, "categoria_id": 3, "codigo_referencia": "REG-VOL-GN125", "codigo_oem": "OEM-32800-05300", "nombre": "Regulador de Voltaje Suzuki GN125", "marca_moto": "Suzuki GN125", "precio_compra": 32000.0, "precio_venta": 58000.0, "stock_actual": 9, "stock_minimo": 3, "activo": 1},
        {"id": 13, "categoria_id": 4, "codigo_referencia": "LIM-INI-300", "codigo_oem": "LIM-300", "nombre": "Limpiador de Inyectores 300 ml", "marca_moto": "Universal", "precio_compra": 13000.0, "precio_venta": 25000.0, "stock_actual": 17, "stock_minimo": 4, "activo": 1},
        {"id": 14, "categoria_id": 5, "codigo_referencia": "ESP-IZ-FZ16", "codigo_oem": "OEM-54B-F6280-00", "nombre": "Espejo Retrovisor Izquierdo Yamaha FZ16", "marca_moto": "Yamaha FZ16", "precio_compra": 22000.0, "precio_venta": 38000.0, "stock_actual": 10, "stock_minimo": 3, "activo": 1},
        {"id": 15, "categoria_id": 3, "codigo_referencia": "BAT-12V-7AH", "codigo_oem": "BAT-12V7A", "nombre": "Batería Sellada 12V 7Ah", "marca_moto": "Universal", "precio_compra": 48000.0, "precio_venta": 85000.0, "stock_actual": 0, "stock_minimo": 2, "activo": 1},
        {"id": 16, "categoria_id": 5, "codigo_referencia": "MAN-DEP-22", "codigo_oem": "MAN-22MM", "nombre": "Manillar Deportivo Universal 22 mm", "marca_moto": "Universal", "precio_compra": 28000.0, "precio_venta": 49000.0, "stock_actual": 7, "stock_minimo": 2, "activo": 1},
        {"id": 17, "categoria_id": 5, "codigo_referencia": "DEF-MOT-PULSAR200", "codigo_oem": "OEM-36DK0014", "nombre": "Defensa de Motor Acero Bajaj Pulsar 200 NS", "marca_moto": "Bajaj Pulsar NS200", "precio_compra": 65000.0, "precio_venta": 110000.0, "stock_actual": 5, "stock_minimo": 2, "activo": 1},
        {"id": 18, "categoria_id": 5, "codigo_referencia": "COR-UNI-NEG", "codigo_oem": "COR-NEG", "nombre": "Cortavientos Universal Negro", "marca_moto": "Universal", "precio_compra": 30000.0, "precio_venta": 55000.0, "stock_actual": 6, "stock_minimo": 2, "activo": 0},
        {"id": 19, "categoria_id": 1, "codigo_referencia": "PAST-FR-CB190R", "codigo_oem": "OEM-06455-KWPB01", "nombre": "Kit de Pastillas de Freno Delanteras Honda CB 190R", "marca_moto": "Honda CB 190R", "precio_compra": 22000.0, "precio_venta": 40000.0, "stock_actual": 13, "stock_minimo": 4, "activo": 1},
        {"id": 20, "categoria_id": 2, "codigo_referencia": "PIN-SAL-15T", "codigo_oem": "PIN-15T", "nombre": "Piñón de Salida 15T 520", "marca_moto": "Universal 200cc-250cc", "precio_compra": 18000.0, "precio_venta": 34000.0, "stock_actual": 16, "stock_minimo": 5, "activo": 1},
        {"id": 21, "categoria_id": 3, "codigo_referencia": "BOM-LED-H4", "codigo_oem": "LED-H4-12V", "nombre": "Bombillo LED H4 12V", "marca_moto": "Universal", "precio_compra": 15000.0, "precio_venta": 29000.0, "stock_actual": 22, "stock_minimo": 6, "activo": 1},
        {"id": 22, "categoria_id": 4, "codigo_referencia": "GRA-MUL-500", "codigo_oem": "GRA-500", "nombre": "Grasa Multipropósito 500 g", "marca_moto": "Universal", "precio_compra": 12000.0, "precio_venta": 22000.0, "stock_actual": 19, "stock_minimo": 5, "activo": 1},
        {"id": 23, "categoria_id": 5, "codigo_referencia": "SOP-CEL-MOTO", "codigo_oem": "SOP-MOTO", "nombre": "Soporte de Celular para Moto", "marca_moto": "Universal", "precio_compra": 18000.0, "precio_venta": 35000.0, "stock_actual": 12, "stock_minimo": 3, "activo": 1},
        {"id": 24, "categoria_id": 1, "codigo_referencia": "BOM-FR-UNI", "codigo_oem": "BOM-FR-UNI", "nombre": "Bomba de Freno Trasera Universal", "marca_moto": "Universal", "precio_compra": 35000.0, "precio_venta": 62000.0, "stock_actual": 8, "stock_minimo": 2, "activo": 1},
        {"id": 25, "categoria_id": 2, "codigo_referencia": "FIL-ACE-CB190R", "codigo_oem": "OEM-15412-KWPB01", "nombre": "Filtro de Aceite Honda CB 190R", "marca_moto": "Honda CB 190R", "precio_compra": 12000.0, "precio_venta": 24000.0, "stock_actual": 15, "stock_minimo": 4, "activo": 1}
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

    Se entrega una copia profunda del estado semilla a cada prueba para que los
    casos sean independientes y no dependan del orden de ejecución.
    """
    db_state = copy.deepcopy(_seed_test_state)
    monkeypatch.setattr(pymysql, "connect", lambda *args, **kwargs: FakeMySQLConnection(db_state))

@pytest.fixture
def app():
    application = create_app({"TESTING": True})
    return application

@pytest.fixture
def client(app):
    """Cliente autenticado como ADMIN para las pruebas del núcleo funcional."""
    test_client = app.test_client()
    with app.app_context():
        token = create_token({"id": 1, "rol": "ADMIN"})
    test_client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return test_client
