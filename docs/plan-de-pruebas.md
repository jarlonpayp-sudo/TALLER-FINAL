# Plan de Pruebas de Software (ISO/IEC/IEEE 29119)

## Sistema de Gestión Comercial «AllQuality»
**Asignatura:** Ingeniería de Software II  
**Institución:** Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)  
**Periodo Académico:** 2026-2  
**Docente Titular:** Ing. Felipe Gutiérrez Isaza  
**Responsable de Pruebas (QA Lead):** Cristian Carabalí  
**Versión evaluada:** Entrega final — 18 de noviembre de 2026

---

## 1. Introducción y Propósito

El presente documento constituye el **Plan Maestro de Pruebas** para el sistema comercial **AllQuality**, estructurado bajo los lineamientos del estándar internacional **ISO/IEC/IEEE 29119** (Software Testing) y alineado a los criterios de calidad de la norma **ISO/IEC 25010**.

El propósito fundamental de este plan es guiar, diseñar, parametrizar y automatizar las actividades de verificación y validación del software. La versión actual —correspondiente a la **entrega final**— incorpora una suite de **49 pruebas**, una cobertura total del **90%**, validaciones transaccionales de inventario y ventas, control de permisos por rol, verificación del cliente React y un catálogo de prueba de **25 productos** distribuidos en 5 categorías.

---

## 2. Alcance de las Pruebas

### Módulos incluidos en el alcance:
1. **Módulo de Autenticación y Control de Acceso:** Inicio de sesión con contraseñas hash, token firmado, restricciones de rol (`ADMIN`, `VENDEDOR`, `INVENTARIO`) y revocación por suspensión.
2. **Módulo de Catálogo de Repuestos y Accesorios:** Creación, edición, consulta, desactivación lógica y búsqueda por código OEM, nombre y categoría.
3. **Módulo de Control de Inventario:** Consulta de saldos, validación de stock mínimo, alertas y ajustes auditados.
4. **Módulo de Ventas:** Registro transaccional, historial, consulta de factura y descuento atómico de existencias.
5. **Módulo de Administración de Usuarios:** Alta de colaboradores, cambio de rol, suspensión y reactivación por parte del `ADMIN`.
6. **Validaciones de Integridad de Datos:** Reglas de negocio que prohíben precios $\le 0$, existencias $< 0$ y códigos duplicados.
7. **Catálogo de prueba ampliado:** 25 productos (24 activos y 1 inactivo), 5 categorías, 2 productos con stock bajo y 2 agotados.
8. **Cliente web React:** Navegación, formularios, búsqueda, carrito, mensajes de error y diseño responsivo.

---

## 3. Estrategia y Niveles de Prueba

La estrategia de verificación implementa el modelo de la **Pirámide de Pruebas**:

```
           / \
          / E2E \         Pruebas de Interfaz / Flujos de Usuario (React)
         /-------\
        /  Integ. \       Pruebas de Integración API REST (Flask + MySQL)
       /-----------\
      /  Unitarias  \     Pruebas Unitarias Automatizadas (pytest)
     /_______________\    - Validación de entidades, cálculos de stock y BVA/EP
```

* **Pruebas Unitarias (Caja Blanca / Lógica de Dominio):** Verificación de métodos de cálculo, validadores de modelos y reglas de stock usando `pytest`.
* **Pruebas de Integración (Caja Negra / API REST):** Comprobación de endpoints HTTP (`POST /api/v1/productos`, `GET /api/v1/productos/buscar`), códigos de estado HTTP (`200`, `201`, `400`, `404`, `422`) y estructura de respuestas JSON.
* **Pruebas de Seguridad y Permisos:** Restricción de operaciones de modificación a usuarios autorizados.

---

## 4. Técnicas Formales de Diseño de Casos de Prueba

Para maximizar la cobertura de pruebas reduciendo la redundancia, el responsable de pruebas (**Cristian Carabalí**) aplicó formalmente dos técnicas de diseño de **Caja Negra**:

### 4.1. Partición de Clases de Equivalencia (Equivalence Partitioning - EP)

#### A. Precio Unitario de Venta ($P$)
* $CE_1$ (Inválida Inferior): $(-\infty, 0] \rightarrow$ Rechazo con HTTP 422 (`"El precio debe ser mayor a cero"`).
* $CE_2$ (Válida Estándar): $(0, 50'000.000] \rightarrow$ Registro exitoso.
* $CE_3$ (Inválida Superior / Desbordamiento): $> 50'000.000 \rightarrow$ Rechazo por valor fuera de rango comercial.

#### B. Existencias de Inventario ($S$)
* $CE_1$ (Inválida Negativa): $(-\infty, -1] \rightarrow$ Rechazo absoluto (`"El inventario no puede ser negativo"`).
* $CE_2$ (Válida en Cero - Agotado): $S = 0 \rightarrow$ Válido; genera estado `AGOTADO` y alerta visual.
* $CE_3$ (Válida en Alerta de Stock Bajo): $1 \le S \le \text{stock\_minimo} \rightarrow$ Válido; genera estado `STOCK_BAJO`.
* $CE_4$ (Válida Abastecida): $S > \text{stock\_minimo} \rightarrow$ Válido; estado `DISPONIBLE`.

#### C. Código de Referencia / OEM
* $CE_1$ (Inválida - Vacía o solo espacios): `""`, `"   "` $\rightarrow$ Error de campo obligatorio (HTTP 400).
* $CE_2$ (Inválida - Duplicada en BD): Código existente $\rightarrow$ Error de unicidad (HTTP 409 Conflict).
* $CE_3$ (Válida): Código alfanumérico único (ej. `"KIT-ARR-YBR125"`) $\rightarrow$ Registro exitoso.

---

### 4.2. Análisis de Valores Límite (Boundary Value Analysis - BVA)

El análisis de frontera se concentra en los puntos donde los sistemas frecuentemente presentan defectos por operadores de comparación erróneos ($<$ en vez de $\le$):

| Variable Evaluada | Frontera Teórica | Valor Evaluado | Clase | Resultado Esperado |
| :--- | :---: | :---: | :---: | :--- |
| **Precio ($P$)** | Límite $0$ | $-0.01$ | Inválida | Rechazado con HTTP 422 |
| | Límite $0$ | $0.00$ | Inválida | Rechazado con HTTP 422 |
| | Límite $0$ | $+0.01$ | Válida | Aceptado como precio mínimo permitido |
| **Existencias ($S$)** | Límite $0$ | $-1$ | Inválida | Rechazado; no permite inventario negativo |
| | Límite $0$ | $0$ | Válida | Aceptado; producto registrado sin existencias |
| | Límite $0$ | $1$ | Válida | Aceptado; existencia física real |
| **Stock Mínimo ($Umbral$)** | Umbral $= 5$ | $4$ | Alerta | Activa alerta de reposición urgente |
| | Umbral $= 5$ | $5$ | Alerta | Activa alerta (umbral límite alcanzado) |
| | Umbral $= 5$ | $6$ | Normal | Sin alerta; estado óptimo |

---

## 5. Catálogo Detallado de Casos de Prueba (CP-01 a CP-13)

### CP-01: Autenticación con Credenciales Válidas e Inválidas
* **Requisito Asociado:** RF-01 | **Tipo:** Seguridad / Integración
* **Precondición:** Usuario registrado en base de datos (`vendedor@allquality.com` con clave hash).
* **Pasos:**
  1. Enviar petición `POST /api/v1/auth/login` con credenciales correctas.
  2. Enviar petición con contraseña incorrecta.
  3. Enviar petición con usuario inexistente.
* **Resultado Esperado:** Caso 1 retorna `200 OK` con token/sesión; Casos 2 y 3 retornan `401 Unauthorized` con mensaje genérico ("Credenciales inválidas").

### CP-02: Creación Exitosa de Repuesto en Catálogo
* **Requisito Asociado:** RF-02 | **Tipo:** Funcional / Caja Negra
* **Entradas:** Código: `"DISC-FR-NMAX155"`, Nombre: `"Disco de Freno Delantero NMAX 155"`, Categoría ID: 1, Precio: $78000.00, Stock: 10, Stock Mínimo: 2.
* **Resultado Esperado:** Código HTTP `201 Created`, producto persistido con ID autogenerado y existencias verificables.

### CP-03: Rechazo de Repuesto con Código Duplicado o Precios Inválidos
* **Requisito Asociado:** RF-02, RNF-08 | **Tipo:** Validación / BVA
* **Pasos:**
  1. Intentar registrar un repuesto con código `"PAST-FR-FZ16"` (ya registrado).
  2. Intentar registrar un repuesto con precio `$0` o negativo.
* **Resultado Esperado:** 
  - Paso 1 retorna `409 Conflict` ("El código de referencia ya se encuentra registrado").
  - Paso 2 retorna `422 Unprocessable Entity` ("El precio debe ser mayor a 0").

### CP-04: Búsqueda y Filtrado Multicriterio de Repuestos
* **Requisito Asociado:** RF-03 | **Tipo:** Funcional
* **Entradas:** Petición `GET /api/v1/productos?q=Yamaha&cat=1`
* **Resultado Esperado:** Retorna un arreglo JSON con los repuestos compatibles con "Yamaha" pertenecientes a la categoría dada; una búsqueda sin coincidencias retorna `200 OK` con lista vacía.

### CP-05: Verificación de Alertas de Stock Bajo
* **Requisito Asociado:** RF-11 | **Tipo:** Lógica de Dominio / BVA
* **Precondición:** El fixture de la suite contiene dos productos con stock bajo (IDs 2 y 5) y dos agotados (IDs 6 y 15); un producto con stock suficiente, como el ID 1, no debe aparecer.
* **Petición:** `GET /api/v1/inventario/alertas`
* **Resultado Esperado:** La respuesta contiene exactamente cuatro alertas: IDs 2 y 5 como `STOCK_BAJO`, e IDs 6 y 15 como `AGOTADO`.

### CP-06: Consulta y Actualización Controlada de Existencias
* **Requisito Asociado:** RF-09 (ajuste manual), RF-18 | **Tipo:** Integración
* **Pasos:** Modificar existencias mediante endpoint de ajuste administrativo autorizado.
* **Resultado Esperado:** El saldo en base de datos se actualiza exactamente por la cantidad indicada y genera registro de auditoría.

### CP-07: Bloqueo de Existencias Negativas
* **Requisito Asociado:** RF-06, RF-07, RNF-04 | **Tipo:** Fiabilidad / Robustez
* **Pasos:** Intentar vender 10 unidades sobre un repuesto con 4 disponibles y repetir una venta multiítem donde una línea no tiene stock.
* **Resultado Esperado:** Rechazo con `400 Bad Request` y mensaje con las unidades disponibles; ninguna línea descuenta stock si falla la transacción.

### CP-08: Desactivación Lógica de Repuesto
* **Requisito Asociado:** RF-04 | **Tipo:** Integridad Referencial
* **Pasos:** Enviar `DELETE /api/v1/productos/1`.
* **Resultado Esperado:** El registro no se elimina físicamente de la base de datos (se fija `activo = 0`). Queda oculto del mostrador de ventas pero preserva el historial comercial.

### CP-09: Actualización de Datos de Catálogo
* **Requisito Asociado:** RF-04 | **Tipo:** Funcional / Integración
* **Pasos:** Enviar `PUT /api/v1/productos/1` con nombre, categoría, códigos y precios válidos; repetir con un código de otro producto y con precio cero.
* **Resultado Esperado:** La actualización válida retorna `200 OK` y conserva el stock; el código duplicado retorna `409 Conflict`; el precio inválido retorna `422 Unprocessable Entity`.

### CP-10: Historial y Consulta de Ventas
* **Requisito Asociado:** RF-05 | **Tipo:** Funcional / Integración
* **Pasos:** Registrar una venta y consultar `GET /api/v1/ventas?limit=10`; abrir `GET /api/v1/ventas/{id}`.
* **Resultado Esperado:** El historial retorna las facturas con vendedor, fecha, estado y total; el detalle incluye las líneas con cantidad, precio histórico y subtotal.

### CP-11: Control de Permisos por Rol
* **Requisito Asociado:** RF-13 | **Tipo:** Seguridad / Integración
* **Pasos:** Solicitar un endpoint protegido sin token, con token inválido y con token de `VENDEDOR`; intentar crear un producto y ajustar inventario con el rol `VENDEDOR`; ajustar stock con el rol `INVENTARIO`.
* **Resultado Esperado:** Sin token o con token inválido se retorna `401`; las escrituras no autorizadas retornan `403`; `VENDEDOR` conserva acceso de lectura y `INVENTARIO` puede ajustar stock.

### CP-12: Administración de Usuarios y Roles
* **Requisito Asociado:** RF-12 | **Tipo:** Funcional / Seguridad
* **Pasos:** Como `ADMIN`, listar usuarios y roles, crear un colaborador, iniciar sesión con él, cambiar su rol, suspenderlo y reactivarlo. Intentar las mismas operaciones con `VENDEDOR`.
* **Resultado Esperado:** `ADMIN` completa el ciclo; el nuevo colaborador puede iniciar sesión mientras esté activo; la suspensión revoca el acceso y su token anterior; `VENDEDOR` recibe `403`.

### CP-13: Credenciales Seguras y Revocación de Sesión
* **Requisito Asociado:** RF-01, RNF-02 | **Tipo:** Seguridad
* **Pasos:** Iniciar sesión con credenciales válidas e inválidas, usar un token firmado, suspender una cuenta y reutilizar el token emitido.
* **Resultado Esperado:** Las credenciales válidas retornan `200 OK` con token; las inválidas, `401`; un token inválido o de una cuenta suspendida, `401`; la contraseña no se devuelve en ninguna respuesta.

---

## 6. Matriz de Trazabilidad de Requisitos (RTM)

| Código | Requisito | Caso | Evidencia automatizada / manual | Estado entrega final |
| :---: | :--- | :---: | :--- | :---: |
| **RF-01** | Autenticación y sesión | CP-01, CP-13 | `test_auth.py`; `test_auth_roles.py`; verificación manual de login | Cumple |
| **RF-02** | Crear y administrar catálogo | CP-02, CP-03, CP-09 | `test_productos.py`; `test_api_extra.py` | Cumple |
| **RF-03** | Consultar y buscar productos | CP-04 | `test_productos.py`, `test_api_extra.py` | Cumple |
| **RF-04** | Editar o desactivar repuesto | CP-08, CP-09 | `test_productos.py`, `test_api_extra.py` | Cumple |
| **RF-05** | Registrar venta | CP-10 | `test_inventario_s1.py`, `test_api_extra.py`, venta manual en MariaDB | Cumple |
| **RF-06** | Actualización atómica de inventario | CP-07, CP-10 | `test_venta_descuenta_inventario_atomicamente`; rollback multiítem manual | Cumple |
| **RF-07** | Anti-sobreventa | CP-07 | `test_bloqueo_sobreventa_stock_insuficiente`; verificación manual | Cumple |
| **RF-08** | Compras a proveedores | — | Sin módulo de compras | No implementado (backlog) |
| **RF-09** | Entrada y confirmación de mercancía | CP-06 | Ajuste manual auditado; no existe recepción de compras | Parcial |
| **RF-10** | Anulación de ventas | — | Sin endpoint de anulación | No implementado (backlog) |
| **RF-11** | Alertas de stock bajo | CP-05 | `test_inventario_s1.py` | Cumple |
| **RF-12** | Administrar usuarios y roles | CP-12 | `test_usuarios.py`; verificación con Playwright | Cumple |
| **RF-13** | Control de permisos por rol | CP-11 | `test_auth_roles.py`; verificación con Playwright | Cumple |
| **RF-14** | Copias de seguridad | — | Solo disponible el procedimiento manual de `mysqldump` | No implementado (backlog) |
| **RF-15** | Restauración de datos | — | Sin flujo integrado | No implementado (backlog) |
| **RF-16** | Reportes comerciales | — | Sin reportes por periodo ni rotación | No implementado (backlog) |
| **RF-17** | Cálculo exacto de totales | CP-02, CP-10 | Columnas `DECIMAL(12,2)` verificadas en MariaDB | Cumple |
| **RF-18** | Historial de auditoría | CP-06, CP-07, CP-10 | Registros de venta y ajuste verificados en MariaDB | Cumple |
| **RNF-01** | Rendimiento p95 ≤ 1.5 s | — | Benchmark formal pendiente | Parcial |
| **RNF-02** | Hash de contraseñas y roles en servidor | CP-13 | `werkzeug.security`, token firmado y pruebas 401/403 | Cumple |
| **RNF-03** | Usabilidad y flujo de venta | CP-10 | Verificación manual en Chrome | Cumple |
| **RNF-04** | ACID y cero sobreventas | CP-07 | `FOR UPDATE`, `rollback`; concurrencia real pendiente | Parcial |
| **RNF-05** | Compatibilidad de navegadores | — | Chrome verificado; Firefox y Edge pendientes | Parcial |
| **RNF-06** | Mantenibilidad y suite automatizada | — | 49 pruebas, cobertura 90%, catálogo de 25 productos y arquitectura por capas | Cumple |
| **RNF-07** | Despliegue local nativo | — | XAMPP MariaDB 10.4.32 + Flask + Vite | Cumple |
| **RNF-08** | Restricciones de integridad | CP-03, CP-07 | Validaciones de servicio y `CHECK` en el esquema | Cumple |

---

## 7. Guía de Ejecución de Pruebas Automatizadas

Las pruebas están automatizadas con el framework **pytest** de Python:

```powershell
# 1. Asegurar entorno virtual activo (opcional si ya está activo)
cd src/backend
.\venv\Scripts\Activate.ps1

# 2. Ejecutar la suite completa desde la raíz del repositorio
cd ../..
python -m pytest -q

# 3. Ejecutar con reporte de cobertura de código
python -m pytest --cov=src/backend --cov-report=term-missing -q
```

### 7.1. Distribución de la suite

| Archivo | Pruebas | Cobertura funcional |
| :--- | :---: | :--- |
| `tests/backend/test_auth.py` | 3 | Login exitoso, contraseña incorrecta y usuario inexistente. |
| `tests/backend/test_auth_roles.py` | 6 | Token ausente/inválido, lectura autorizada y escrituras rechazadas por rol. |
| `tests/backend/test_productos.py` | 7 | Listado y búsqueda del catálogo de 25 productos, creación, stock obligatorio, duplicados, precios límite y desactivación. |
| `tests/backend/test_inventario_s1.py` | 5 | Alertas del catálogo ampliado, ajustes, stock negativo, venta atómica y anti-sobreventa. |
| `tests/backend/test_api_extra.py` | 20 | Health, errores HTTP, 5 categorías, actualización de producto, historial y detalle de ventas. |
| `tests/backend/test_usuarios.py` | 8 | Alta, roles, correo único, suspensión, revocación de sesión y restricción a `ADMIN`. |
| **Total** | **49** | **Cobertura total: 90%; catálogo de prueba: 25 productos (24 activos).** |

La suite usa una conexión MySQL simulada para ser determinista. La aplicación se validó manualmente contra **MariaDB 10.4.32 de XAMPP**, incluida una venta real, el descuento de stock, el rollback multiítem, la auditoría y la administración de usuarios; el frontend se compiló con Vite y se recorrió con Playwright. La prueba automatizada de integración contra MySQL/MariaDB real queda como mejora prevista (backlog), fuera del alcance automatizado de esta entrega.

### 7.2. Verificación manual del frontend

| Escenario | Resultado esperado | Estado |
| :--- | :--- | :---: |
| Compilación de producción | `npm run build` genera `dist/` sin errores. | Aprobado |
| Inicio de sesión | El usuario accede al panel con su nombre y rol. | Aprobado |
| Navegación | Las rutas de productos, inventario y ventas cargan sin errores de consola. | Aprobado |
| Roles | `VENDEDOR` no ve acciones de administración ni la ruta `/usuarios`; `ADMIN` sí. | Aprobado |
| Catálogo | Búsqueda, filtro, creación, edición y desactivación funcionan contra la API. | Aprobado |
| Inventario | El ajuste de stock actualiza la tabla y muestra el mensaje de éxito. | Aprobado |
| Venta | El carrito calcula el total, descuenta stock y muestra la factura. | Aprobado |
| Usuarios | `ADMIN` crea, edita el rol, suspende y reactiva un colaborador; el suspendido no puede ingresar. | Aprobado |
| Responsive | El menú lateral se convierte en panel desplegable en móvil. | Aprobado |

---

**Aprobado por:**  
**Cristian Carabalí**  
*Responsable de Pruebas (QA / Testing Lead)*  
*Ingeniería de Software II — COTECNOVA 2026-2*
