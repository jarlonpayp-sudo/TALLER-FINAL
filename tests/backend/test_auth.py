def test_login_exitoso(client):
    """
    CP-01: Autenticación exitosa con credenciales válidas
    """
    response = client.post("/api/v1/auth/login", json={
        "email": "vendedor@allquality.com",
        "password": "Admin123*"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert data["usuario"]["email"] == "vendedor@allquality.com"
    assert data["usuario"]["rol"] == "VENDEDOR"

def test_login_credenciales_incorrectas(client):
    """
    CP-01: Rechazo de autenticación con contraseña incorrecta (HTTP 401)
    """
    response = client.post("/api/v1/auth/login", json={
        "email": "vendedor@allquality.com",
        "password": "clave_totalmente_errada"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data

def test_login_usuario_inexistente(client):
    """
    CP-01: Rechazo de autenticación con usuario inexistente (HTTP 401 sin revelar existencia)
    """
    response = client.post("/api/v1/auth/login", json={
        "email": "noexiste@allquality.com",
        "password": "Admin123*"
    })
    assert response.status_code == 401

