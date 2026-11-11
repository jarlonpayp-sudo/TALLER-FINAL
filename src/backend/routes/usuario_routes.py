from flask import Blueprint, g, jsonify, request

from auth_utils import require_role
from services.usuario_service import UsuarioService

usuario_bp = Blueprint("usuarios", __name__, url_prefix="/api/v1/usuarios")


@usuario_bp.route("", methods=["GET"])
@require_role("ADMIN")
def listar_usuarios():
    usuarios = UsuarioService.listar()
    roles = UsuarioService.listar_roles()
    return jsonify({
        "total": len(usuarios),
        "usuarios": usuarios,
        "roles": roles,
    }), 200


@usuario_bp.route("", methods=["POST"])
@require_role("ADMIN")
def crear_usuario():
    data = request.get_json() or {}
    try:
        usuario = UsuarioService.crear(data)
        return jsonify({
            "mensaje": "Colaborador registrado correctamente.",
            "usuario": usuario,
        }), 201
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 409
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Error interno al crear el usuario: {str(e)}"}), 500


@usuario_bp.route("/<int:usuario_id>", methods=["PUT"])
@require_role("ADMIN")
def actualizar_usuario(usuario_id):
    data = request.get_json() or {}
    if usuario_id == g.usuario.get("id") and data.get("activo") is False:
        return jsonify({"error": "No puede suspender su propia cuenta."}), 400
    if usuario_id == g.usuario.get("id") and "rol_id" in data:
        try:
            nuevo_rol = int(data.get("rol_id"))
        except (TypeError, ValueError):
            nuevo_rol = None
        if nuevo_rol != g.usuario.get("rol_id"):
            return jsonify({"error": "No puede cambiar su propio rol."}), 400

    try:
        usuario = UsuarioService.actualizar(usuario_id, data)
        return jsonify({
            "mensaje": "Usuario actualizado correctamente.",
            "usuario": usuario,
        }), 200
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 409
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Error interno al actualizar el usuario: {str(e)}"}), 500


@usuario_bp.route("/<int:usuario_id>", methods=["DELETE"])
@require_role("ADMIN")
def desactivar_usuario(usuario_id):
    if usuario_id == g.usuario.get("id"):
        return jsonify({"error": "No puede suspender su propia cuenta."}), 400

    try:
        exito = UsuarioService.desactivar(usuario_id)
        if not exito:
            return jsonify({"error": f"Usuario con ID {usuario_id} no encontrado."}), 404
        return jsonify({"mensaje": "Usuario suspendido correctamente."}), 200
    except Exception as e:
        return jsonify({"error": f"Error interno al suspender el usuario: {str(e)}"}), 500
