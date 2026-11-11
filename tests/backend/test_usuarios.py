from auth_utils import create_token


def _headers(app, rol="ADMIN", usuario_id=1):
    with app.app_context():
        token = create_token({"id": usuario_id, "rol": rol})
    return {"Authorization": f"Bearer {token}"}


def test_admin_puede_listar_usuarios_y_roles(client):
    response = client.get("/api/v1/usuarios")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 4
    assert len(data["roles"]) == 3
    assert all("password_hash" not in usuario for usuario in data["usuarios"])


def test_admin_puede_crear_colaborador_y_este_puede_iniciar_sesion(client):
    response = client.post("/api/v1/usuarios", json={
        "nombre": "Laura Gómez",
        "email": "laura@allquality.com",
        "password": "ClaveSegura123*",
        "rol_id": 2,
    })
    assert response.status_code == 201
    usuario = response.get_json()["usuario"]
    assert usuario["email"] == "laura@allquality.com"
    assert usuario["rol"] == "VENDEDOR"
    assert "password_hash" not in usuario

    login = client.post("/api/v1/auth/login", json={
        "email": "laura@allquality.com",
        "password": "ClaveSegura123*",
    })
    assert login.status_code == 200
    assert login.get_json()["usuario"]["rol"] == "VENDEDOR"


def test_no_permite_correos_duplicados(client):
    response = client.post("/api/v1/usuarios", json={
        "nombre": "Duplicado",
        "email": "admin@allquality.com",
        "password": "ClaveSegura123*",
        "rol_id": 1,
    })
    assert response.status_code == 409


def test_no_permite_password_corta(client):
    response = client.post("/api/v1/usuarios", json={
        "nombre": "Clave corta",
        "email": "corta@allquality.com",
        "password": "123",
        "rol_id": 2,
    })
    assert response.status_code == 422


def test_admin_puede_cambiar_rol_y_suspender_usuario(client):
    response = client.put("/api/v1/usuarios/2", json={
        "nombre": "Cristian Carabalí",
        "email": "vendedor@allquality.com",
        "rol_id": 3,
        "activo": True,
    })
    assert response.status_code == 200
    assert response.get_json()["usuario"]["rol"] == "INVENTARIO"

    session = client.post("/api/v1/auth/login", json={
        "email": "vendedor@allquality.com",
        "password": "Admin123*",
    }).get_json()["token"]

    response = client.delete("/api/v1/usuarios/2")
    assert response.status_code == 200

    usuarios = client.get("/api/v1/usuarios").get_json()["usuarios"]
    actualizado = next(u for u in usuarios if u["id"] == 2)
    assert actualizado["activo"] == 0

    revocada = client.get(
        "/api/v1/productos",
        headers={"Authorization": f"Bearer {session}"},
    )
    assert revocada.status_code == 401

    login = client.post("/api/v1/auth/login", json={
        "email": "vendedor@allquality.com",
        "password": "Admin123*",
    })
    assert login.status_code == 403


def test_admin_no_puede_suspenderse_a_si_mismo(client):
    response = client.delete("/api/v1/usuarios/1")
    assert response.status_code == 400


def test_admin_no_puede_cambiar_su_propio_rol(client):
    response = client.put("/api/v1/usuarios/1", json={"rol_id": 2, "activo": True})
    assert response.status_code == 400
    assert "propio rol" in response.get_json()["error"]


def test_vendedor_no_puede_administrar_usuarios(app):
    client = app.test_client()
    response = client.get(
        "/api/v1/usuarios",
        headers=_headers(app, rol="VENDEDOR", usuario_id=2),
    )
    assert response.status_code == 403
