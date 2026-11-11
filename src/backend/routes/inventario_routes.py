from flask import Blueprint, request, jsonify
from auth_utils import require_auth, require_role
from services.inventario_service import InventarioService

inventario_bp = Blueprint("inventario", __name__, url_prefix="/api/v1/inventario")

@inventario_bp.route("/alertas", methods=["GET"])
@require_auth
def obtener_alertas():
    alertas = InventarioService.obtener_alertas()
    return jsonify({
        "total_alertas": len(alertas),
        "productos_en_alerta": alertas
    }), 200

@inventario_bp.route("/ajuste", methods=["POST"])
@require_role("ADMIN", "INVENTARIO")
def ajustar_stock():
    data = request.get_json() or {}
    repuesto_id = data.get("repuesto_id")
    cantidad = data.get("cantidad")
    tipo = data.get("tipo", "AJUSTE")
    usuario_id = data.get("usuario_id", 1)
    justificacion = data.get("justificacion", "Ajuste manual de existencias")

    if not repuesto_id or cantidad is None:
        return jsonify({"error": "Debe especificar 'repuesto_id' y 'cantidad'."}), 400

    try:
        resultado = InventarioService.ajustar_stock(
            repuesto_id=int(repuesto_id),
            cantidad_cambio=int(cantidad),
            tipo_movimiento=tipo,
            usuario_id=usuario_id,
            justificacion=justificacion
        )
        return jsonify({
            "mensaje": "Inventario ajustado correctamente.",
            "resultado": resultado
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al procesar el ajuste de inventario: {str(e)}"}), 500

