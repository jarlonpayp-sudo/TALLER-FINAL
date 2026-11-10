import pymysql
import pymysql.cursors
from config import Config

def get_db():
    """
    Retorna una conexión activa al motor de base de datos MySQL (InnoDB).
    Utiliza DictCursor para retornar filas como diccionarios.
    """
    try:
        return pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    except pymysql.MySQLError as e:
        raise ConnectionError(
            f"Error conectando al servidor MySQL ({Config.DB_HOST}:{Config.DB_PORT}) en la base '{Config.DB_NAME}'. "
            f"Verifique que el servicio de MySQL (XAMPP / Laragon) esté encendido. Detalle: {str(e)}"
        )
