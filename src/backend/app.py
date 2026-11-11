import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.auth_routes import auth_bp
from routes.producto_routes import producto_bp
from routes.categoria_routes import categoria_bp
from routes.inventario_routes import inventario_bp
from routes.venta_routes import venta_bp
from routes.usuario_routes import usuario_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # Habilitar CORS para integración con React (puerto 5173 por defecto)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar Blueprints de la API REST
    app.register_blueprint(auth_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(venta_bp)
    app.register_blueprint(usuario_bp)

    @app.route("/api/v1/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "online",
            "sistema": "AllQuality - Gestión Comercial de Repuestos para Motocicletas",
            "version": "1.0.0",
            "motor_bd": "MySQL (InnoDB)"
        }), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[*] Iniciando servidor AllQuality API en http://127.0.0.1:{port}...")
    print(f"[*] Conectando a MySQL en {Config.DB_HOST}:{Config.DB_PORT} (Base: {Config.DB_NAME})")
    app.run(host="0.0.0.0", port=port, debug=True)
