from database.connection import get_db


class CategoriaService:
    @staticmethod
    def listar():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion
            FROM categorias
            ORDER BY nombre ASC
        """)
        categorias = cursor.fetchall()
        cursor.close()
        conn.close()
        return categorias
