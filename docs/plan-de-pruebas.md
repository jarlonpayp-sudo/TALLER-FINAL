# Plan de Pruebas de Software (ISO/IEC/IEEE 29119)

## Sistema de Gestión Comercial «AllQuality»
**Asignatura:** Ingeniería de Software II  
**Institución:** Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)  
**Periodo Académico:** 2026-2  
**Docente Titular:** Ing. Felipe Gutiérrez Isaza  
**Responsable de Pruebas (QA Lead):** Cristian Carabalí  
**Hito de Entrega:** Seguimiento 1 (`entrega-s1`)  

---

## 1. Introducción y Propósito

El presente documento constituye el **Plan Maestro de Pruebas** para el sistema comercial **AllQuality**, estructurado bajo los lineamientos del estándar internacional **ISO/IEC/IEEE 29119** (Software Testing) y alineado a los criterios de calidad de la norma **ISO/IEC 25010**.

El propósito fundamental de este plan es guiar, diseñar, parametrizar y automatizar las actividades de verificación y validación del software para el **Seguimiento 1 (S1)**, garantizando que el núcleo del catálogo de repuestos, el control de existencias y las validaciones de negocio cumplan con los criterios de aceptación antes de avanzar a la fase de integración transaccional avanzada.

---

## 2. Alcance de las Pruebas (Seguimiento 1)

### Módulos Incluidos en el Alcance de S1:
1. **Módulo de Autenticación y Control de Acceso:** Inicio de sesión y restricciones básicas por rol (`ADMIN`, `VENDEDOR`, `INVENTARIO`).
2. **Módulo de Catálogo de Repuestos y Accesorios:** Creación, edición, consulta, desactivación lógica y búsqueda por código OEM, nombre y categoría.
3. **Módulo de Control de Inventario Inicial:** Consulta de saldos, validación de stock mínimo y disparador de alertas.
4. **Validaciones de Integridad de Datos:** Reglas de negocio que prohíben precios $\le 0$, existencias $< 0$ y códigos duplicados.

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

## 5. Catálogo Detallado de Casos de Prueba (CP-01 a CP-08)

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
* **Entradas:** Código: `"PAST-FR-FZ16"`, Nombre: `"Pastillas de Freno Delanteras Yamaha FZ16"`, Categoría ID: 1, Precio: $35000.00, Stock: 15, Stock Mínimo: 3.
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
* **Requisito Asociado:** RF-03, RF-16 | **Tipo:** Desempeño / Funcional
* **Entradas:** Petición `GET /api/v1/productos?q=Yamaha&cat=1`
* **Resultado Esperado:** Retorna arreglo JSON con los repuestos compatibles con "Yamaha" pertenecientes a la categoría dada. Tiempo de respuesta $\le 300\text{ ms}$.

### CP-05: Verificación de Alertas de Stock Bajo
* **Requisito Asociado:** RF-04, RF-11 | **Tipo:** Lógica de Dominio / BVA
* **Precondición:** Producto A con `stock = 3`, `stock_minimo = 5`; Producto B con `stock = 10`, `stock_minimo = 5`.
* **Petición:** `GET /api/v1/inventario/alertas`
* **Resultado Esperado:** La respuesta incluye al Producto A con bandera `alerta_stock = true` y omite al Producto B.

### CP-06: Consulta y Actualización Controlada de Existencias
* **Requisito Asociado:** RF-03, RF-06 | **Tipo:** Integración
* **Pasos:** Modificar existencias mediante endpoint de ajuste administrativo autorizado.
* **Resultado Esperado:** El saldo en base de datos se actualiza exactamente por la cantidad indicada y genera registro de auditoría.

### CP-07: Bloqueo de Existencias Negativas
* **Requisito Asociado:** RF-07, RNF-03 | **Tipo:** Fiabilidad / Robustez
* **Pasos:** Intentar descontar 10 unidades sobre un repuesto con 4 unidades disponibles.
* **Resultado Esperado:** Rechazo con `400 Bad Request` ("Stock insuficiente para realizar la operación") y el inventario permanece inalterado en 4.

### CP-08: Desactivación Lógica de Repuesto
* **Requisito Asociado:** RF-02 | **Tipo:** Integridad Referencial
* **Pasos:** Enviar `DELETE /api/v1/productos/1`.
* **Resultado Esperado:** El registro no se elimina físicamente de la base de datos (se fija `activo = 0`). Queda oculto del mostrador de ventas pero preserva el historial comercial.

---

## 6. Matriz de Trazabilidad de Requisitos (RTM)

| Código Requisito | Descripción del Requisito | Caso de Prueba | Suite Automatizada (pytest) | Criterio de Calidad |
| :---: | :--- | :---: | :--- | :---: |
| **RF-01** | Autenticación y roles | **CP-01** | `test_auth.py::test_login_valido_invalido` | Seguridad |
| **RF-02** | Gestión de repuestos | **CP-02, CP-03, CP-08** | `test_productos.py::test_crear_producto_valido` | Adecuación Funcional |
| **RF-03** | Búsqueda y catálogo | **CP-04** | `test_productos.py::test_buscar_productos_filtros` | Usabilidad / Desempeño |
| **RF-04** | Alertas de stock bajo | **CP-05** | `test_inventario.py::test_alertas_stock_minimo` | Fiabilidad / Operación |
| **RF-06** | Actualización de stock | **CP-06** | `test_inventario.py::test_ajuste_inventario` | Consistencia de Datos |
| **RF-07** | Validación anti-sobreventa | **CP-07** | `test_inventario.py::test_bloqueo_stock_negativo` | Fiabilidad e Integridad |
| **RNF-01** | Tiempo respuesta $< 1.5$s | **CP-04** | `test_productos.py::test_rendimiento_busqueda` | Eficiencia de Desempeño |
| **RNF-08** | Validación de entradas | **CP-03, CP-07** | `test_productos.py::test_rechazo_valores_limite` | Adecuación Funcional |

---

## 7. Guía de Ejecución de Pruebas Automatizadas

Las pruebas están automatizadas con el framework **pytest** de Python:

```powershell
# 1. Asegurar entorno virtual activo
cd src/backend
.\venv\Scripts\Activate.ps1

# 2. Ejecutar la suite completa con reporte en consola
pytest ../../tests/backend -v

# 3. Ejecutar con reporte de cobertura de código
pytest ../../tests/backend --cov=src/backend -v
```

---

**Aprobado por:**  
**Cristian Carabalí**  
*Responsable de Pruebas (QA / Testing Lead)*  
*Ingeniería de Software II — COTECNOVA 2026-2*
