from functools import wraps

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database.connection import get_db


def _serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="allquality-session",
    )


def create_token(usuario):
    """Genera un token firmado con el identificador y el rol del usuario."""
    return _serializer().dumps({
        "id": usuario["id"],
        "rol": usuario["rol"],
    })


def _validar_sesion():
    """Valida el token Bearer y carga el usuario en ``g``.

    Devuelve ``None`` cuando la sesión es válida o una respuesta JSON de error
    cuando falta el token, expiró o no tiene una firma válida.
    """
    header = request.headers.get("Authorization", "").strip()
    if not header.startswith("Bearer "):
        return jsonify({"error": "Sesión requerida. Inicie sesión nuevamente."}), 401

    token = header[7:].strip()
    if not token:
        return jsonify({"error": "Sesión requerida. Inicie sesión nuevamente."}), 401

    try:
        payload = _serializer().loads(
            token,
            max_age=int(current_app.config.get("TOKEN_MAX_AGE", 28800)),
        )
    except SignatureExpired:
        return jsonify({"error": "La sesión ha expirado. Inicie sesión nuevamente."}), 401
    except BadSignature:
        return jsonify({"error": "Token de sesión inválido."}), 401

    if not payload.get("id") or not payload.get("rol"):
        return jsonify({"error": "Token de sesión inválido."}), 401

    # El token demuestra la identidad, pero el estado y el rol se consultan de
    # nuevo para que una suspensión o un cambio de rol tengan efecto inmediato.
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.activo, u.rol_id, r.nombre AS rol
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE u.id = %s
        """,
        (payload["id"],),
    )
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if not usuario or not usuario.get("activo"):
        return jsonify({
            "error": "La sesión ya no está activa. Inicie sesión nuevamente."
        }), 401

    g.usuario = {
        "id": payload["id"],
        "rol_id": usuario["rol_id"],
        "rol": usuario["rol"],
    }
    return None


def require_auth(fn):
    """Exige una sesión válida antes de ejecutar la ruta."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        error = _validar_sesion()
        if error is not None:
            return error
        return fn(*args, **kwargs)

    return wrapper


def require_role(*roles):
    """Exige una sesión válida y uno de los roles indicados."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            error = _validar_sesion()
            if error is not None:
                return error
            if g.usuario.get("rol") not in roles:
                return jsonify({
                    "error": "No tiene permisos para realizar esta operación."
                }), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
