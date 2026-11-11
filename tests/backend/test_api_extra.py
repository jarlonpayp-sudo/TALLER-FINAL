"""
Pruebas adicionales de la API: errores HTTP, categorías, actualización de productos e historial de ventas.

Cubren rutas de error, validaciones de entrada y el flujo completo de
registro y consulta de una venta. Complementan los casos CP-01 a CP-08
del plan de pruebas.
"""


def test_health_endpoint(client):
    """El health check debe responder sin depender de MySQL."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "online"
    assert "AllQuality" in data["sistema"]


def test_obtener_producto_inexistente(client):
    """GET de un repuesto inexistente debe devolver 404."""
    response = client.get("/api/v1/productos/99")
    assert response.status_code == 404
    assert "no encontrado" in response.get_json()["error"].lower()


def test_desactivar_producto_inexistente(client):
    """DELETE de un repuesto inexistente debe devolver 404."""
    response = client.delete("/api/v1/productos/99")
    assert response.status_code == 404
    assert "no encontrado" in response.get_json()["error"].lower()


def test_crear_producto_sin_campos_obligatorios(client):
    """La creación sin código, nombre o categoría debe devolver 422."""
    response = client.post("/api/v1/productos", json={})
    assert response.status_code == 422
    assert "error" in response.get_json()


def test_listar_con_categoria_invalida(client):
    """Un parámetro de categoría no numérico no debe romper el listado."""
    response = client.get("/api/v1/productos?cat=abc")
    assert response.status_code == 200
    assert "productos" in response.get_json()


def test_login_sin_password(client):
    """El login sin contraseña debe devolver 400."""
    response = client.post("/api/v1/auth/login", json={"email": "vendedor@allquality.com"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_login_usuario_inactivo(client):
    """Un usuario con activo = 0 debe recibir 403."""
    response = client.post("/api/v1/auth/login", json={
        "email": "inactivo@allquality.com",
        "password": "Admin123*"
    })
    assert response.status_code == 403
    assert "inactiva" in response.get_json()["error"].lower()


def test_ajuste_sin_campos_obligatorios(client):
    """El ajuste sin repuesto_id ni cantidad debe devolver 400."""
    response = client.post("/api/v1/inventario/ajuste", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_ajuste_repuesto_inexistente(client):
    """El ajuste de un repuesto inexistente debe devolver 400."""
    response = client.post("/api/v1/inventario/ajuste", json={
        "repuesto_id": 99,
        "cantidad": 5
    })
    assert response.status_code == 400
    assert "no existe" in response.get_json()["error"].lower()


def test_venta_carrito_vacio(client):
    """Una venta sin ítems debe devolver 400."""
    response = client.post("/api/v1/ventas", json={"usuario_id": 2, "items": []})
    assert response.status_code == 400
    assert "al menos un producto" in response.get_json()["error"].lower()


def test_venta_repuesto_inexistente(client):
    """Una venta con un repuesto inexistente debe devolver 400."""
    response = client.post("/api/v1/ventas", json={
        "usuario_id": 2,
        "items": [{"repuesto_id": 99, "cantidad": 1}]
    })
    assert response.status_code == 400
    assert "no existe" in response.get_json()["error"].lower()


def test_venta_cantidad_invalida(client):
    """Una cantidad igual a cero debe rechazarse antes de tocar el stock."""
    response = client.post("/api/v1/ventas", json={
        "usuario_id": 2,
        "items": [{"repuesto_id": 1, "cantidad": 0}]
    })
    assert response.status_code == 400
    assert "cantidad mayor a cero" in response.get_json()["error"].lower()


def test_registrar_y_consultar_venta(client):
    """Flujo completo: registrar una venta y consultar su detalle."""
    response = client.post("/api/v1/ventas", json={
        "usuario_id": 2,
        "notas": "Venta de prueba de integración",
        "items": [{"repuesto_id": 1, "cantidad": 2}]
    })
    assert response.status_code == 201
    venta_id = response.get_json()["venta"]["venta_id"]

    consulta = client.get(f"/api/v1/ventas/{venta_id}")
    assert consulta.status_code == 200
    data = consulta.get_json()
    assert data["id"] == venta_id
    assert data["estado"] == "COMPLETADA"
    assert len(data["items"]) == 1
    assert data["items"][0]["repuesto_id"] == 1
    assert data["items"][0]["cantidad"] == 2


def test_consultar_venta_inexistente(client):
    """GET de una venta inexistente debe devolver 404."""
    response = client.get("/api/v1/ventas/99")
    assert response.status_code == 404
    assert "no encontrada" in response.get_json()["error"].lower()


def test_listar_categorias(client):
    """El frontend necesita las categorías para el formulario de repuestos."""
    response = client.get("/api/v1/categorias")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] >= 4
    assert any(c["nombre"] == "Frenos" for c in data["categorias"])


def test_listar_ventas(client):
    """El historial de ventas debe devolver las ventas registradas."""
    client.post("/api/v1/ventas", json={
        "usuario_id": 2,
        "notas": "Venta para historial",
        "items": [{"repuesto_id": 1, "cantidad": 1}]
    })

    response = client.get("/api/v1/ventas?limit=10")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] >= 1
    assert data["ventas"][0]["numero_factura"].startswith("FAC-")


def test_actualizar_producto_valido(client):
    """PUT debe actualizar los datos de catálogo sin tocar el stock."""
    response = client.put("/api/v1/productos/1", json={
        "categoria_id": 1,
        "codigo_referencia": "PAST-FR-FZ16",
        "codigo_oem": "OEM-54B-W0045-00",
        "nombre": "Pastillas de Freno Delanteras Yamaha FZ16 (actualizado)",
        "marca_moto": "Yamaha FZ16",
        "precio_compra": 19000.0,
        "precio_venta": 34000.0,
        "stock_minimo": 4
    })
    assert response.status_code == 200
    producto = response.get_json()["producto"]
    assert producto["nombre"].endswith("(actualizado)")
    assert producto["precio_venta"] == 34000.0
    assert producto["stock_actual"] == 12


def test_actualizar_producto_inexistente(client):
    """PUT de un repuesto inexistente debe devolver 404."""
    response = client.put("/api/v1/productos/99", json={
        "categoria_id": 1,
        "codigo_referencia": "NO-EXISTE",
        "nombre": "Repuesto inexistente",
        "precio_venta": 1000.0
    })
    assert response.status_code == 404


def test_actualizar_producto_codigo_duplicado(client):
    """PUT con un código de otro repuesto debe devolver 409."""
    response = client.put("/api/v1/productos/1", json={
        "categoria_id": 1,
        "codigo_referencia": "BND-TR-GN125",
        "nombre": "Pastillas de Freno Delanteras Yamaha FZ16",
        "precio_venta": 32000.0
    })
    assert response.status_code == 409


def test_actualizar_producto_precio_invalido(client):
    """PUT con precio cero debe devolver 422."""
    response = client.put("/api/v1/productos/1", json={
        "categoria_id": 1,
        "codigo_referencia": "PAST-FR-FZ16",
        "nombre": "Pastillas de Freno Delanteras Yamaha FZ16",
        "precio_venta": 0
    })
    assert response.status_code == 422
