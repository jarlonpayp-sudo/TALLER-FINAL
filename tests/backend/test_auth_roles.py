from auth_utils import create_token


def _headers(app, rol="VENDEDOR", usuario_id=2):
    with app.app_context():
        token = create_token({"id": usuario_id, "rol": rol})
    return {"Authorization": f"Bearer {token}"}


def test_endpoint_protegido_sin_token(app):
    """RF-01 / RF-13: las rutas de negocio no aceptan peticiones sin sesión."""
    client = app.test_client()
    response = client.get("/api/v1/productos")
    assert response.status_code == 401
    assert "Sesión requerida" in response.get_json()["error"]


def test_token_invalido_es_rechazado(app):
    """RF-01: un token manipulado no permite acceder a la API."""
    client = app.test_client()
    response = client.get(
        "/api/v1/productos",
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert response.status_code == 401


def test_vendedor_puede_consultar_catalogo(app):
    """RF-13: el rol VENDEDOR conserva acceso de solo lectura al catálogo."""
    client = app.test_client()
    response = client.get("/api/v1/productos", headers=_headers(app))
    assert response.status_code == 200


def test_vendedor_no_puede_crear_productos(app):
    """RF-13: el rol VENDEDOR no puede administrar el catálogo."""
    client = app.test_client()
    response = client.post(
        "/api/v1/productos",
        headers=_headers(app),
        json={
            "codigo_referencia": "TEST-ROL-001",
            "nombre": "Producto de prueba",
            "categoria_id": 1,
            "precio_compra": 1000,
            "precio_venta": 2000,
            "stock_actual": 1,
            "stock_minimo": 1,
        },
    )
    assert response.status_code == 403
    assert "permisos" in response.get_json()["error"]


def test_vendedor_no_puede_ajustar_inventario(app):
    """RF-13: el rol VENDEDOR no puede modificar existencias."""
    client = app.test_client()
    response = client.post(
        "/api/v1/inventario/ajuste",
        headers=_headers(app),
        json={"repuesto_id": 1, "cantidad": 1},
    )
    assert response.status_code == 403


def test_inventario_puede_ajustar_stock(app):
    """RF-13: el rol INVENTARIO puede registrar ajustes de stock."""
    client = app.test_client()
    response = client.post(
        "/api/v1/inventario/ajuste",
        headers=_headers(app, rol="INVENTARIO", usuario_id=3),
        json={
            "repuesto_id": 1,
            "cantidad": 1,
            "justificacion": "Prueba de permisos",
        },
    )
    assert response.status_code == 200
