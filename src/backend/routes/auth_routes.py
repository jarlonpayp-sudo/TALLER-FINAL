from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

from auth_utils import create_token
from database.connection import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Debe suministrar correo y contraseña."}), 400

    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT u.id, u.nombre, u.email, u.password_hash, u.activo, r.nombre as rol FROM usuarios u JOIN roles r ON u.rol_id = r.id WHERE u.email = %s"

    cursor.execute(query, (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "Credenciales inválidas."}), 401

    if not user.get("activo"):
        return jsonify({"error": "La cuenta se encuentra inactiva."}), 403

    password_hash = user.get("password_hash") or ""
    if not password_hash or not check_password_hash(password_hash, password):
        return jsonify({"error": "Credenciales inválidas."}), 401

    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "usuario": {
            "id": user["id"],
            "nombre": user["nombre"],
            "email": user["email"],
            "rol": user["rol"]
        },
        "token": create_token(user)
    }), 200
