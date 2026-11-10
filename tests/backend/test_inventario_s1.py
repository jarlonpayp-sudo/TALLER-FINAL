def test_alertas_stock_minimo(client):
    """
    CP-05: Detección y listado de repuestos en alerta de stock bajo o agotado
    """
    response = client.get("/api/v1/inventario/alertas")
    assert response.status_code == 200
    data = response.get_json()
    assert "productos_en_alerta" in data
    assert data["total_alertas"] >= 1
    
    # El producto 2 (Bandas GN125) tiene stock 2 y stock_minimo 4, debe estar en alerta
    ids_en_alerta = [p["id"] for p in data["productos_en_alerta"]]
    assert 2 in ids_en_alerta

def test_ajuste_inventario_valido(client):
    """
    CP-06: Ajuste manual de existencias positivo
    """
    # Agregar 5 unidades al producto 1 (Pastillas FZ16 tenía 12, ahora tendrá 17)
    payload = {
        "repuesto_id": 1,
        "cantidad": 5,
        "tipo": "COMPRA_ENTRADA",
        "usuario_id": 1,
        "justificacion": "Llegada de pedido de proveedor"
    }
    response = client.post("/api/v1/inventario/ajuste", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["resultado"]["stock_anterior"] == 12
    assert data["resultado"]["stock_nuevo"] == 17

def test_bloqueo_ajuste_stock_negativo(client):
    """
    CP-07: Rechazo de ajuste que deje el inventario en saldo negativo
    """
    # Intentar restar 50 unidades al producto 1 (que tiene 17)
    payload = {
        "repuesto_id": 1,
        "cantidad": -50,
        "tipo": "AJUSTE",
        "usuario_id": 1,
        "justificacion": "Pérdida no justificada"
    }
    response = client.post("/api/v1/inventario/ajuste", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "insuficiente" in data["error"].lower()

def test_venta_descuenta_inventario_atomicamente(client):
    """
    CP-06 y RF-06: Venta de mostrador descuenta el inventario de forma inmediata y exacta
    """
    # El producto 3 (Kit arrastre) tiene 8 unidades en stock
    venta_payload = {
        "usuario_id": 2,
        "notas": "Venta de mostrador cliente particular",
        "items": [
            {"repuesto_id": 3, "cantidad": 2}
        ]
    }
    response = client.post("/api/v1/ventas", json=venta_payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "venta" in data
    assert data["venta"]["items_vendidos"] == 1
    assert data["venta"]["total"] == 250000.0 # 2 * 125,000

    # Comprobar que en el catálogo el stock bajó a 6
    res_prod = client.get("/api/v1/productos/3")
    assert res_prod.status_code == 200
    assert res_prod.get_json()["stock_actual"] == 6

def test_bloqueo_sobreventa_stock_insuficiente(client):
    """
    CP-07 / RF-07: Bloqueo de venta si la cantidad supera las existencias (Anti-Sobrevanta)
    """
    # El producto 3 tiene 6 unidades; intentamos vender 10
    venta_invalida = {
        "usuario_id": 2,
        "items": [
            {"repuesto_id": 3, "cantidad": 10}
        ]
    }
    response = client.post("/api/v1/ventas", json=venta_invalida)
    assert response.status_code == 400
    data = response.get_json()
    assert "insuficiente" in data["error"].lower()

    # Comprobar que el inventario se mantuvo intacto en 6
    res_prod = client.get("/api/v1/productos/3")
    assert res_prod.get_json()["stock_actual"] == 6

