from flask import Blueprint, request, jsonify
from auth_utils import require_auth, require_role
from services.producto_service import ProductoService

producto_bp = Blueprint("productos", __name__, url_prefix="/api/v1/productos")

@producto_bp.route("", methods=["GET"])
@require_auth
def listar_productos():
    q = request.args.get("q")
    categoria_id = request.args.get("cat")
    try:
        if categoria_id:
            categoria_id = int(categoria_id)
    except ValueError:
        categoria_id = None

    productos = ProductoService.listar(q=q, categoria_id=categoria_id)
    return jsonify({"total": len(productos), "productos": productos}), 200

@producto_bp.route("/<int:producto_id>", methods=["GET"])
@require_auth
def obtener_producto(producto_id):
    producto = ProductoService.obtener_por_id(producto_id)
    if not producto:
        return jsonify({"error": f"Repuesto con ID {producto_id} no encontrado."}), 404
    return jsonify(producto), 200

@producto_bp.route("", methods=["POST"])
@require_role("ADMIN", "INVENTARIO")
def crear_producto():
    data = request.get_json() or {}
    try:
        nuevo_producto = ProductoService.crear(data)
        return jsonify({
            "mensaje": "Repuesto registrado correctamente en el catálogo.",
            "producto": nuevo_producto
        }), 201
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 409
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Error interno al crear el repuesto: {str(e)}"}), 500

@producto_bp.route("/<int:producto_id>", methods=["PUT"])
@require_role("ADMIN", "INVENTARIO")
def actualizar_producto(producto_id):
    data = request.get_json() or {}
    try:
        producto = ProductoService.actualizar(producto_id, data)
        return jsonify({
            "mensaje": "Repuesto actualizado correctamente.",
            "producto": producto
        }), 200
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 409
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Error interno al actualizar el repuesto: {str(e)}"}), 500


@producto_bp.route("/<int:producto_id>", methods=["DELETE"])
@require_role("ADMIN", "INVENTARIO")
def desactivar_producto(producto_id):
    exito = ProductoService.desactivar(producto_id)
    if not exito:
        return jsonify({"error": f"Repuesto con ID {producto_id} no encontrado."}), 404
    return jsonify({"mensaje": "Repuesto desactivado correctamente del mostrador."}), 200

