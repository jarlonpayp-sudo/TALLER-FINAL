# Informe de Calidad del Producto (ISO/IEC 25010) y Mantenimiento

## Sistema de Gestión Comercial «AllQuality»
**Asignatura:** Ingeniería de Software II  
**Institución:** Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)  
**Periodo Académico:** 2026-2  
**Docente Titular:** Ing. Felipe Gutiérrez Isaza  
**Responsable de Calidad:** Steven Rendón  
**Hito de Entrega:** Seguimiento 1 (`entrega-s1`) / Preparación para Seguimiento 2 (`entrega-s2`)  

---

## 1. Introducción y Marco de Evaluación

El presente informe consolida el marco de evaluación de calidad de software aplicado al sistema **AllQuality**, fundamentado en el estándar internacional **ISO/IEC 25010** (Modelo de Calidad del Producto) y las directrices de mantenimiento de **ISO/IEC 14764**.

Este documento establece las métricas de calidad objetivas, los umbrales de aceptación y la bitácora inicial de defectos técnicos detectados durante la construcción y verificación del software.

---

## 2. Evaluación de Características de Calidad (ISO/IEC 25010)

| Característica ISO/IEC 25010 | Métrica Evaluada | Meta de Calidad | Método de Verificación | Estado S1 |
| :--- | :--- | :---: | :--- | :---: |
| **1. Adecuación Funcional** | Porcentaje de pruebas de catálogo e inventario aprobadas | 100% | Ejecución automatizada con `pytest` | **100% (14/14 tests)** |
| **2. Eficiencia de Desempeño** | Latencia en consultas de búsqueda y catálogo | $\le 1.5\text{ s}$ | Pruebas de integración HTTP locales | **Conforme (< 50 ms)** |
| **3. Compatibilidad** | Intercambio de datos JSON y compatibilidad SQL | 100% | Contratos de API REST estandarizados | **Conforme** |
| **4. Capacidad de Interacción** | Claridad en códigos de error y respuestas HTTP | Códigos 200, 201, 400, 409, 422 | Manejo centralizado de excepciones | **Conforme** |
| **5. Fiabilidad** | Cero inventarios negativos y consistencia de stock | 0 sobreventas | Validación en base de datos (`CHECK stock >= 0`) y servicios | **Conforme** |
| **6. Seguridad** | Rechazo de credenciales inválidas y roles | 100% pruebas de acceso | Verificación de credenciales en `test_auth.py` | **Conforme** |
| **7. Mantenibilidad** | Modularidad de código y desacoplamiento | Capas separadas | Arquitectura en Rutas, Servicios y Base de datos | **Conforme** |
| **8. Flexibilidad / Portabilidad** | Ejecución nativa sin dependencias de virtualización | Cero Docker | Python 3.12 + MySQL (InnoDB) | **Conforme** |

---

## 3. Bitácora de Defectos Técnicos (Bug Log - DEF-01 a DEF-04)

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
* **Prueba Asociada:** `test_inventario_s1.py::test_bloqueo_sobreventa_stock_insuficiente`.

---

## 4. Acciones de Mantenimiento (ISO/IEC 14764)

* **Mantenimiento Correctivo:** Corrección de validaciones de límites numéricos (precios, stock) y manejo centralizado de errores HTTP 400, 409 y 422.
* **Mantenimiento Preventivo:** Estandarización de tipos numéricos (`float`/`int`) y exclusión estricta de archivos temporales mediante `.gitignore`.
* **Mantenimiento Perfectivo:** Desacoplamiento de la lógica de negocio en clases de servicio (`ProductoService`, `InventarioService`, `VentaService`), facilitando la integración con el cliente en React.

---

**Aprobado por:**  
**Steven Rendón**  
*Responsable de Calidad*  
*Ingeniería de Software II — COTECNOVA 2026-2*

