# Informe de Calidad del Producto (ISO/IEC 25010) y Mantenimiento

## Sistema de Gestión Comercial «AllQuality»
**Asignatura:** Ingeniería de Software II  
**Institución:** Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)  
**Periodo Académico:** 2026-2  
**Docente Titular:** Ing. Felipe Gutiérrez Isaza  
**Responsable de Calidad:** Steven Rendón  
**Versión evaluada:** Entrega final — 18 de noviembre de 2026

---

## 1. Introducción y Marco de Evaluación

El presente informe consolida el marco de evaluación de calidad de software aplicado al sistema **AllQuality**, fundamentado en el estándar internacional **ISO/IEC 25010** (Modelo de Calidad del Producto) y las directrices de mantenimiento de **ISO/IEC 14764**.

Este documento establece las métricas de calidad objetivas, los umbrales de aceptación y la bitácora de defectos técnicos detectados durante la construcción y verificación del software. El alcance evaluado corresponde a la **entrega final**; los requisitos de compras, anulación de ventas, reportes y respaldo integrado **no forman parte del alcance implementado** y se documentan como backlog en la [verificación de requisitos](verificacion-requisitos.md).

---

## 2. Evaluación de Características de Calidad (ISO/IEC 25010)

| Característica ISO/IEC 25010 | Métrica Evaluada | Meta de Calidad | Método de Verificación | Resultado |
| :--- | :--- | :---: | :--- | :---: |
| **1. Adecuación Funcional** | Porcentaje de pruebas automatizadas aprobadas | 100% | Ejecución automatizada con `pytest` | **100% de pruebas aprobadas (49/49); cobertura 90%; catálogo de prueba con 25 productos (24 activos)** |
| **2. Eficiencia de Desempeño** | Latencia en consultas de búsqueda y catálogo | $\le 1.5\text{ s}$ | Pruebas locales; benchmark formal pendiente | **Parcial: respuestas locales rápidas, sin benchmark con 1.000 repuestos** |
| **3. Compatibilidad** | Intercambio de datos JSON y compatibilidad SQL | 100% | API REST estandarizada y cliente React conectado | **Conforme (React + API JSON + MariaDB 10.4.32)** |
| **4. Capacidad de Interacción** | Claridad en códigos de error y respuestas HTTP | Códigos 200, 201, 400, 401, 403, 404, 409, 422 | Manejo centralizado de excepciones y mensajes en la interfaz | **Conforme (API + interfaz React)** |
| **5. Fiabilidad** | Cero inventarios negativos y consistencia de stock | 0 sobreventas | Validación en servicios, transacción `FOR UPDATE` y `CHECK` en MariaDB | **Parcial: venta atómica y rollback manual verificados; concurrencia real pendiente** |
| **6. Seguridad** | Hash de contraseñas, token firmado y roles en servidor | 100% pruebas de acceso | `werkzeug.security`, `itsdangerous`, `@require_auth` y `@require_role` | **Conforme; queda endurecer `SECRET_KEY`, HTTPS y CORS para producción** |
| **7. Mantenibilidad** | Modularidad de código y desacoplamiento | Capas separadas | Arquitectura en Rutas, Servicios y Base de datos | **Conforme (49 pruebas, 90% de cobertura)** |
| **8. Flexibilidad / Portabilidad** | Ejecución nativa sin dependencias de virtualización | Cero Docker | Python 3.11.9 + MariaDB (InnoDB) + Vite | **Conforme** |

> **Limitación de la medición:** la suite usa una conexión MySQL simulada (`FakeMySQLConnection`), por lo que los resultados de concurrencia y rendimiento no sustituyen una prueba contra el motor real. La aplicación se validó manualmente contra **MariaDB 10.4.32 de XAMPP**, incluida una venta real, el rollback multiítem, la auditoría y la administración de usuarios; el frontend se compiló con Vite y se recorrió con Playwright. La prueba automatizada de integración contra MariaDB/MySQL real queda como mejora prevista (backlog).

---

## 3. Bitácora de Defectos Técnicos (Bug Log - DEF-01 a DEF-05)

Durante las sesiones de inspección de código y pruebas tempranas, el responsable de calidad (**Steven Rendón**) y el responsable de pruebas (**Cristian Carabalí**) registraron y resolvieron los siguientes defectos:

### DEF-01: Aceptación de Precios Cero o Negativos en Creación de Repuesto
* **Severidad:** Alta | **Módulo:** `src/backend/services/producto_service.py`
* **Causa Raíz:** Ausencia de validación de valor límite ($P \le 0$) en la capa de servicios antes de insertar en base de datos.
* **Solución Aplicada:** Incorporación de validación estricta que emite `ValueError("El precio de venta debe ser un número estrictamente mayor a 0.")` con código HTTP 422.
* **Prueba Asociada:** `test_productos.py::test_rechazo_precio_limite_invalido_bva`.

### DEF-02: Colisión de Códigos de Referencia Duplicados
* **Severidad:** Alta | **Módulo:** `src/backend/services/producto_service.py`
* **Causa Raíz:** No se verificaba la unicidad de `codigo_referencia` a nivel de servicio, arrojando errores 500 no controlados del motor de base de datos.
* **Solución Aplicada:** Verificación previa de unicidad con emisión de código HTTP 409 Conflict y mensaje descriptivo.
* **Prueba Asociada:** `test_productos.py::test_rechazo_codigo_duplicado`.

### DEF-03: Posibilidad de Saldo Negativo en Ajustes Manuales de Existencias
* **Severidad:** Crítica | **Módulo:** `src/backend/services/inventario_service.py`
* **Causa Raíz:** El cálculo de ajuste no comprobaba si `stock_actual + cantidad_cambio < 0`.
* **Solución Aplicada:** Guardia de validación anti-sobreventa que rechaza ajustes con saldo negativo con código HTTP 400.
* **Prueba Asociada:** `test_inventario_s1.py::test_bloqueo_ajuste_stock_negativo`.

### DEF-04: Transacción No Atómica en Venta con Múltiples Productos
* **Severidad:** Crítica | **Módulo:** `src/backend/services/venta_service.py`
* **Causa Raíz:** Si el segundo repuesto no tenía stock suficiente, el primer repuesto ya había sido descontado sin reversión (Rollback).
* **Solución Aplicada:** Transacción atómica en dos fases: validación total de stock previo a la deducción y bloque `try/except` con `conn.rollback()` ante cualquier falla.
* **Prueba Asociada:** `test_inventario_s1.py::test_bloqueo_sobreventa_stock_insuficiente` y verificación manual multiítem contra MariaDB.

### DEF-05: Autenticación Simulada y Roles Solo en la Interfaz
* **Severidad:** Crítica | **Módulo:** `auth_utils.py`, `routes/auth_routes.py`, rutas de negocio
* **Causa Raíz:** El token no estaba firmado y el backend no verificaba el rol antes de ejecutar operaciones administrativas; ocultar botones en React no impedía llamar la API directamente.
* **Solución Aplicada:** Contraseñas con `pbkdf2:sha256`, token firmado con `itsdangerous`, expiración de 8 horas, decoradores `@require_auth`/`@require_role` y verificación del estado activo en cada petición.
* **Prueba Asociada:** `test_auth_roles.py`, `test_usuarios.py` y verificación manual con Playwright.

---

## 4. Acciones de Mantenimiento (ISO/IEC 14764)

* **Mantenimiento Correctivo:** Corrección de validaciones de límites numéricos (precios, stock) y manejo centralizado de errores HTTP 400, 409 y 422.
* **Mantenimiento Preventivo:** Estandarización de tipos numéricos (`float`/`int`) y exclusión estricta de archivos temporales mediante `.gitignore`.
* **Mantenimiento Perfectivo:** Desacoplamiento de la lógica de negocio en clases de servicio (`ProductoService`, `CategoriaService`, `InventarioService`, `UsuarioService`, `VentaService`), incorporación de un cliente React 18 + Vite con diseño blanco y negro, autenticación firmada y administración de usuarios.
* **Backlog evolutivo (no implementado en esta entrega):** compras/recepción de mercancía, anulación de ventas, reportes comerciales, respaldo/restauración integrados, pruebas de concurrencia e integración automatizada con MariaDB.

---

**Aprobado por:**  
**Steven Rendón**  
*Responsable de Calidad*  
*Ingeniería de Software II — COTECNOVA 2026-2*

