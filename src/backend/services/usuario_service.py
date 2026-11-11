import re

from werkzeug.security import generate_password_hash

from database.connection import get_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 8


class UsuarioService:
    @staticmethod
    def listar():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nombre, u.email, u.rol_id, u.activo, r.nombre AS rol, u.created_at
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            ORDER BY u.nombre ASC
        """)
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return usuarios

    @staticmethod
    def listar_roles():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion
            FROM roles
            ORDER BY id ASC
        """)
        roles = cursor.fetchall()
        cursor.close()
        conn.close()
        return roles

    @staticmethod
    def _validar_datos(data, actualizando=False):
        nombre = str(data.get("nombre", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        rol_id = data.get("rol_id")
        password = str(data.get("password", ""))

        if not actualizando or "nombre" in data:
            if not nombre:
                raise ValueError("El nombre del colaborador es obligatorio.")
        if not actualizando or "email" in data:
            if not email:
                raise ValueError("El correo electrónico es obligatorio.")
            if not EMAIL_RE.match(email):
                raise ValueError("El correo electrónico no tiene un formato válido.")
        if not actualizando or "rol_id" in data:
            try:
                rol_id = int(rol_id)
            except (TypeError, ValueError):
                raise ValueError("Debe seleccionar un rol válido.")
        if not actualizando and not password:
            raise ValueError("La contraseña inicial es obligatoria.")
        if password and len(password) < PASSWORD_MIN_LENGTH:
            raise ValueError(
                f"La contraseña debe tener al menos {PASSWORD_MIN_LENGTH} caracteres."
            )

        return nombre, email, rol_id, password

    @staticmethod
    def _existe_rol(cursor, rol_id):
        cursor.execute("SELECT id FROM roles WHERE id = %s", (rol_id,))
        return cursor.fetchone() is not None

    @staticmethod
    def _existe_email(cursor, email, excluir_id=None):
        if excluir_id is None:
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        else:
            cursor.execute(
                "SELECT id FROM usuarios WHERE email = %s AND id <> %s",
                (email, excluir_id),
            )
        return cursor.fetchone() is not None

    @staticmethod
    def _obtener_usuario(cursor, usuario_id):
        cursor.execute("""
            SELECT u.id, u.nombre, u.email, u.rol_id, u.activo, r.nombre AS rol, u.created_at
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.id = %s
        """, (usuario_id,))
        return cursor.fetchone()

    @staticmethod
    def crear(data):
        nombre, email, rol_id, password = UsuarioService._validar_datos(data)

        conn = get_db()
        cursor = conn.cursor()
        try:
            if not UsuarioService._existe_rol(cursor, rol_id):
                raise ValueError("El rol seleccionado no existe.")
            if UsuarioService._existe_email(cursor, email):
                raise KeyError("El correo electrónico ya se encuentra registrado.")

            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password_hash, rol_id, activo)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                nombre,
                email,
                generate_password_hash(password, method="pbkdf2:sha256"),
                rol_id,
                1,
            ))
            usuario_id = cursor.lastrowid
            conn.commit()
            usuario = UsuarioService._obtener_usuario(cursor, usuario_id)
            return usuario
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar(usuario_id, data):
        conn = get_db()
        cursor = conn.cursor()
        try:
            actual = UsuarioService._obtener_usuario(cursor, usuario_id)
            if not actual:
                raise LookupError(f"Usuario con ID {usuario_id} no encontrado.")

            nombre, email, rol_id, password = UsuarioService._validar_datos(
                {
                    **actual,
                    **data,
                },
                actualizando=True,
            )
            if not UsuarioService._existe_rol(cursor, rol_id):
                raise ValueError("El rol seleccionado no existe.")
            if UsuarioService._existe_email(cursor, email, excluir_id=usuario_id):
                raise KeyError("El correo electrónico ya se encuentra registrado.")

            activo = int(bool(data.get("activo", actual.get("activo", 1))))
            if password:
                cursor.execute("""
                    UPDATE usuarios
                    SET nombre = %s, email = %s, rol_id = %s, activo = %s, password_hash = %s
                    WHERE id = %s
                """, (
                    nombre,
                    email,
                    rol_id,
                    activo,
                    generate_password_hash(password, method="pbkdf2:sha256"),
                    usuario_id,
                ))
            else:
                cursor.execute("""
                    UPDATE usuarios
                    SET nombre = %s, email = %s, rol_id = %s, activo = %s
                    WHERE id = %s
                """, (nombre, email, rol_id, activo, usuario_id))
            conn.commit()
            return UsuarioService._obtener_usuario(cursor, usuario_id)
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def desactivar(usuario_id):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
            if cursor.fetchone() is None:
                return False
            cursor.execute(
                "UPDATE usuarios SET activo = 0 WHERE id = %s",
                (usuario_id,),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
