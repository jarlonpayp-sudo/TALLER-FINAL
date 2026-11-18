def test_listar_productos(client):
    """
    CP-04: Listado general de repuestos activos del catálogo ampliado.
    """
    response = client.get("/api/v1/productos")
    assert response.status_code == 200
    data = response.get_json()
    assert "productos" in data
    assert data["total"] == 24
    assert len(data["productos"]) == 24

    ids = {p["id"] for p in data["productos"]}
    assert 18 not in ids  # Producto inactivo del catálogo
    assert {1, 5, 6, 15, 25}.issubset(ids)

    conteo_categorias = {}
    for producto in data["productos"]:
        categoria = producto["categoria_nombre"]
        conteo_categorias[categoria] = conteo_categorias.get(categoria, 0) + 1

    assert conteo_categorias == {
        "Frenos": 6,
        "Motor y Transmisión": 5,
        "Eléctrico": 5,
        "Lubricantes y Químicos": 4,
        "Accesorios": 4,
    }

def test_buscar_producto_por_nombre_o_oem(client):
    """
    CP-04: Búsqueda multicriterio con texto parcial, por nombre y por OEM.
    """
    response_nombre = client.get("/api/v1/productos?q=Yamaha")
    assert response_nombre.status_code == 200
    data_nombre = response_nombre.get_json()
    assert data_nombre["total"] == 2
    assert {1, 14}.issubset({p["id"] for p in data_nombre["productos"]})
    assert all("Yamaha" in p["nombre"] for p in data_nombre["productos"])

    response_oem = client.get("/api/v1/productos?q=OEM-36DK0013")
    assert response_oem.status_code == 200
    data_oem = response_oem.get_json()
    assert data_oem["total"] == 1
    assert data_oem["productos"][0]["id"] == 6

def test_crear_repuesto_valido(client):
    """
    CP-02: Registro exitoso de un repuesto con todos los campos válidos
    """
    nuevo = {
        "categoria_id": 1,
        "codigo_referencia": "DISC-FR-NMAX155",
        "codigo_oem": "OEM-2DP-F582U-00",
        "nombre": "Disco de Freno Delantero NMAX 155",
        "marca_moto": "Yamaha NMAX",
        "precio_compra": 45000.0,
        "precio_venta": 78000.0,
        "stock_actual": 10,
        "stock_minimo": 2
    }
    response = client.post("/api/v1/productos", json=nuevo)
    assert response.status_code == 201
    data = response.get_json()
    assert data["producto"]["codigo_referencia"] == "DISC-FR-NMAX155"
    assert data["producto"]["stock_actual"] == 10

def test_rechazo_repuesto_sin_existencias_iniciales(client):
    """
    RF-02: El stock inicial es obligatorio aunque su valor válido pueda ser cero.
    """
    incompleto = {
        "categoria_id": 1,
        "codigo_referencia": "SIN-STOCK-001",
        "nombre": "Repuesto sin stock informado",
        "precio_venta": 25000.0,
    }
    response = client.post("/api/v1/productos", json=incompleto)
    assert response.status_code == 422
    assert "existencias iniciales" in response.get_json()["error"]

def test_rechazo_codigo_duplicado(client):
    """
    CP-03: Rechazo por código de referencia duplicado (HTTP 409 Conflict)
    """
    duplicado = {
        "categoria_id": 1,
        "codigo_referencia": "PAST-FR-FZ16", # Código ya existente
        "nombre": "Otro repuesto con el mismo código",
        "precio_venta": 30000.0,
        "stock_actual": 5
    }
    response = client.post("/api/v1/productos", json=duplicado)
    assert response.status_code == 409
    data = response.get_json()
    assert "error" in data

def test_rechazo_precio_limite_invalido_bva(client):
    """
    CP-03 / BVA: Rechazo de precios menores o iguales a cero (HTTP 422)
    """
    # Prueba con 0.00 (Límite frontera)
    invalido_cero = {
        "categoria_id": 1,
        "codigo_referencia": "TEST-PRECIO-0",
        "nombre": "Repuesto con precio cero",
        "precio_venta": 0.00,
        "stock_actual": 5
    }
    res_cero = client.post("/api/v1/productos", json=invalido_cero)
    assert res_cero.status_code == 422

    # Prueba con precio negativo (-1000)
    invalido_neg = {
        "categoria_id": 1,
        "codigo_referencia": "TEST-PRECIO-NEG",
        "nombre": "Repuesto con precio negativo",
        "precio_venta": -1000.0,
        "stock_actual": 5
    }
    res_neg = client.post("/api/v1/productos", json=invalido_neg)
    assert res_neg.status_code == 422

def test_desactivar_repuesto_logico(client):
    """
    CP-08: Desactivación lógica de repuesto (conserva integridad)
    """
    # Desactivar producto id 4 (Bujía)
    response = client.delete("/api/v1/productos/4")
    assert response.status_code == 200

    # Al volver a consultar, no debe aparecer en el listado activo
    res_list = client.get("/api/v1/productos")
    ids = [p["id"] for p in res_list.get_json()["productos"]]
    assert 4 not in ids

