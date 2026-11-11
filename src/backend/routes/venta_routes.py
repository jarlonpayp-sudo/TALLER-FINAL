from flask import Blueprint, request, jsonify
from auth_utils import require_auth, require_role
from services.venta_service import VentaService

venta_bp = Blueprint("ventas", __name__, url_prefix="/api/v1/ventas")

@venta_bp.route("", methods=["POST"])
@require_role("ADMIN", "VENDEDOR", "INVENTARIO")
def registrar_venta():
    data = request.get_json() or {}
    items = data.get("items")
    usuario_id = data.get("usuario_id", 2) # Por defecto vendedor
    notas = data.get("notas", "")

    if not items:
        return jsonify({"error": "Debe incluir al menos un producto en la venta."}), 400

    try:
        resultado = VentaService.registrar_venta(
            usuario_id=usuario_id,
            items=items,
            notas=notas
        )
        return jsonify({
            "mensaje": "Venta registrada e inventario actualizado exitosamente.",
            "venta": resultado
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al procesar la venta: {str(e)}"}), 500

@venta_bp.route("", methods=["GET"])
@require_auth
def listar_ventas():
    limite = request.args.get("limit", 50)
    try:
        limite = int(limite)
    except (TypeError, ValueError):
        limite = 50
    limite = max(1, min(limite, 200))
    ventas = VentaService.listar_ventas(limite)
    return jsonify({"total": len(ventas), "ventas": ventas}), 200


@venta_bp.route("/<int:venta_id>", methods=["GET"])
@require_auth
def obtener_venta(venta_id):
    venta = VentaService.obtener_venta(venta_id)
    if not venta:
        return jsonify({"error": f"Venta con ID {venta_id} no encontrada."}), 404
    return jsonify(venta), 200

