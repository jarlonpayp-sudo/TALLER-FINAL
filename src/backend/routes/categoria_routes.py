from flask import Blueprint, jsonify
from auth_utils import require_auth
from services.categoria_service import CategoriaService

categoria_bp = Blueprint("categorias", __name__, url_prefix="/api/v1/categorias")


@categoria_bp.route("", methods=["GET"])
@require_auth
def listar_categorias():
    categorias = CategoriaService.listar()
    return jsonify({"total": len(categorias), "categorias": categorias}), 200
