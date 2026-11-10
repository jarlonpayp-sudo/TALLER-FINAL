# Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)

## Ingeniería de Sistemas — Ingeniería de Software II

### Periodo Académico: 2026-2 | Docente: Felipe Gutiérrez Isaza

### Proyecto Final: Sistema de Gestión Comercial de Repuestos y Accesorios para Motocicletas «AllQuality»

**Estado del Entregable:** Seguimiento 2 / Consolidación de Calidad y Mantenimiento  
**Rama Oficial de Trabajo:** `main` | **Tags de Entrega:** `entrega-s1`, `entrega-s2`, `entrega-final`  
**Modalidad de Despliegue:** 100% Local y Nativo (Sin contenedores / Sin Docker)

---

## 1. Descripción del Proyecto y Arquitectura Técnica

«**AllQuality**» es una solución integral de software diseñada para la administración comercial y control operativo de establecimientos dedicados a la comercialización de repuestos, accesorios, lubricantes y consumibles para motocicletas. El sistema optimiza las operaciones en mostrador y bodega, garantizando consistencia transaccional estricta, validación de existencias en tiempo real, alertas preventivas ante agotamiento de inventario, auditoría de ventas y seguridad perimetral basada en roles.

### Problema que Resuelve
En el sector comercial minorista de autopartes y repuestos para motocicletas, los negocios frecuentemente enfrentan descuadres de caja, ventas de productos agotados por falta de sincronización entre el mostrador y la bodega, pérdidas por diferencias de precios y carencia de trazabilidad sobre las compras y devoluciones. **AllQuality** resuelve este problema mediante un flujo transaccional desacoplado y atómico, donde cada operación de venta descuenta de forma irreversible las existencias reales validadas por el motor de base de datos.

### Stack Tecnológico (100% Local / Sin Docker)

* **Backend:** **Python 3.12+ con Flask**. Arquitectura modular por capas (Rutas/Controladores, Servicios de Dominio, Repositorios/Acceso a Datos y Modelos). Implementa API RESTful con respuestas JSON estandarizadas, manejo centralizado de excepciones y validación de tipos.
* **Frontend:** **React 18 con Vite y Tailwind CSS**. Interfaz de usuario reactiva, ergonómica y de alto contraste optimizada para terminales de punto de venta (POS) y mostradores comerciales. Incluye buscador reactivo de repuestos con debounce, carrito de venta dinámico y alertas visuales de inventario bajo.
* **Persistencia de Datos:** **MySQL 8.0+ / MariaDB** (utilizable mediante XAMPP, Laragon o servicio local nativo). Motor relacional InnoDB con integridad referencial estricta, índices compuestos para acelerar búsquedas por referencia/código OEM y transacciones ACID que previenen sobreventas o inventarios negativos.
* **Estándar de Calidad:** Asegurado bajo el estándar internacional **ISO/IEC 25010** (Adecuación funcional, Eficiencia de desempeño, Fiabilidad, Seguridad, Usabilidad y Mantenibilidad), pruebas bajo directrices **ISO/IEC/IEEE 29119** y mantenimiento conforme a **ISO/IEC 14764**.

---

## 2. Integrantes y Asignación de Roles del Equipo

Conforme a las directrices de la asignatura, el equipo de trabajo está conformado por cuatro integrantes con responsabilidades orientadas pero corresponsabilidad total sobre el código y la sustentación:

| Nombre del Integrante | Rol Oficial en el Proyecto | Responsabilidades Principales |
| :--- | :--- | :--- |
| **Alejandro Londoño** | **Líder Técnico** | Coordina la arquitectura cliente-servidor (Flask + React), define contratos de interfaces REST, supervisa la integración continua en Git y lidera la modelación del esquema relacional en MySQL. |
| **Cristian Carabalí** | **Responsable de Pruebas (QA / Testing Lead)** | Diseña las estrategias de verificación bajo ISO/IEC/IEEE 29119 (Partición de Equivalencia y Valores Límite), implementa la suite automatizada con `pytest` y lidera las pruebas de integración transaccional. |
| **Steven Rendón** | **Responsable de Calidad** | Evalúa el cumplimiento de las características ISO/IEC 25010, conduce las revisiones de código (Code Reviews), gestiona la bitácora de defectos (DEF-01 a DEF-04) y propone mejoras de refactorización y mantenimiento. |
| **Santiago Calvo** | **Responsable de Documentación** | Mantiene actualizado el `README.md`, centraliza los documentos técnicos en `docs/` (`especificacion.md`, `plan-de-pruebas.md`, `informe-calidad.md`) y coordina las evidencias y sincronización con Trello. |

> **Compromiso Institucional:** Todos los integrantes del equipo conocen a fondo la totalidad de los módulos, las decisiones de diseño arquitectónico y las suites de pruebas automatizadas, estando plenamente capacitados para su defensa y explicación individual en la sustentación presencial.

---

## 3. Gestión del Proyecto en Trello

El flujo de trabajo, la priorización de funcionalidades y la trazabilidad del ciclo de vida se gestionan activamente en el tablero oficial:

* **Enlace al Tablero:** [Tablero de Trello — Proyecto Final AllQuality](https://trello.com/invite/b/6ae20964673dd65bcfef559f/ATTI90fd9b632977854e57ae366056873e0d6B0BC26B/proyecto-final)

### Estructura de Listas Operativas
1. **Por hacer (Backlog):** Requisitos funcionales (RF-01 a RF-18) priorizados mediante técnica MoSCoW, modelado de entidades y diseño de contratos REST.
2. **En curso (In Progress):** Desarrollo activo de módulos de backend en Flask, componentes en React o esquemas de base de datos asignados a un responsable con fecha límite.
3. **En revisión (In Review):** Inspección de código cruzada, verificación de cumplimiento de estándares de codificación y comprobación de pruebas unitarias locales.
4. **Hecho (Done):** Tareas finalizadas que cuentan con pruebas automatizadas aprobadas (100% pass), enlace explícito al commit o pull request de GitHub y documentación al día.

### Etiquetas de Seguimiento (Etapas)
* `Planeación` — Definición de alcance, arquitectura, historias de usuario y configuración del repositorio.
* `Seguimiento 1` — CRUD de productos/repuestos, esquema base MySQL, primeras pruebas automatizadas en `pytest`.
* `Seguimiento 2` — Registro transaccional de ventas, validación atómica de existencias, control de inventario, alertas de stock mínimo e informe de calidad ISO/IEC 25010.
* `Entrega final` — Sistema completamente funcional, suite de pruebas automatizadas completa, manuales de usuario/despliegue y preparación para sustentación.

---

## 4. Requisitos del Sistema

### 4.1. Requisitos Funcionales (Priorización MoSCoW)

| Código | Nombre del Requisito | Descripción Detallada | Prioridad MoSCoW | Caso de Uso |
| :--- | :--- | :--- | :---: | :---: |
| **RF-01** | Autenticación y Control de Sesión | Inicio de sesión seguro con usuario/contraseña, verificación de credenciales con hashing seguro (Bcrypt/PBKDF2) y control de acceso basado en roles (`ADMIN`, `VENDEDOR`, `INVENTARIO`). | **Must Have** | CU-01 |
| **RF-02** | Gestión del Catálogo de Repuestos | Registro, consulta, edición y desactivación lógica de productos con atributos: código/referencia única, código OEM, nombre comercial, marca/compatibilidad de motocicleta, categoría, precio de compra, precio de venta, existencia actual y stock mínimo. | **Must Have** | CU-02 |
| **RF-03** | Búsqueda y Filtrado Multicriterio | Localización inmediata de repuestos por texto parcial en nombre, código de referencia exacto, categoría (frenos, motor, transmisión, accesorios, lubricantes) o modelo de moto compatible. | **Must Have** | CU-10 |
| **RF-04** | Consulta de Inventario y Alertas de Stock Bajo | Visualización en tiempo real del saldo de existencias. Generación automática de alertas visuales cuando el inventario disponible sea menor o igual al umbral de stock mínimo parametrizado. | **Must Have** | CU-03 |
| **RF-05** | Registro Transaccional de Ventas (POS) | Módulo de mostrador que permite seleccionar múltiples repuestos, asignar cantidades, calcular subtotales, aplicar impuestos/descuentos parametrizados y calcular el total de la transacción. | **Must Have** | CU-04 |
| **RF-06** | Actualización Atómica de Inventario | Descuento automático de existencias físicas en el momento exacto en que la venta es confirmada, ejecutado bajo transacción ACID para garantizar consistencia. | **Must Have** | CU-04 |
| **RF-07** | Validación de Disponibilidad y Anti-Sobrevanta | Bloqueo absoluto de ventas cuando la cantidad requerida supera la existencia disponible en bodega, impidiendo que el stock caiga en valores negativos (`stock < 0`). | **Must Have** | CU-04 |
| **RF-08** | Gestión de Compras y Proveedores | Registro de órdenes de compra asociadas a proveedores comerciales de repuestos, documentando costos unitarios y cantidades adquiridas. | **Should Have** | CU-05 |
| **RF-09** | Entrada y Recepción de Mercancía | Incremento en existencias de bodega condicionado exclusivamente a la confirmación de mercancía efectivamente recibida e inspeccionada. | **Should Have** | CU-05 |
| **RF-10** | Anulación Autorizada de Ventas | Permite a roles autorizados (`ADMIN`) cancelar una venta previa, reintegrando las unidades al inventario sin duplicar movimientos y registrando el motivo. | **Should Have** | CU-06 |
| **RF-11** | Reportes de Ventas y Movimientos | Generación de balances de ventas por rango de fechas, productos de mayor rotación comercial e historial de entradas/salidas de inventario. | **Could Have** | CU-07 |
| **RF-12** | Administración de Usuarios y Permisos | Creación, suspensión y asignación de roles a los colaboradores del establecimiento desde el panel administrativo. | **Must Have** | CU-08 |
| **RF-13** | Trazabilidad y Bitácora de Auditoría | Registro inmutable de transacciones críticas (ventas, anulaciones, ajustes manuales de stock) con ID de usuario, fecha/hora, acción y registro afectado. | **Must Have** | CU-08 |

### 4.2. Requisitos No Funcionales (Alineados a ISO/IEC 25010)

| Código | Característica ISO 25010 | Criterio de Aceptación y Métrica |
| :--- | :--- | :--- |
| **RNF-01** | **Eficiencia de Desempeño** | El percentil 95 ($p95$) del tiempo de respuesta en búsquedas de catálogo y consultas de inventario debe ser $\le 1.5$ segundos bajo una base de datos de al menos 1,000 repuestos. |
| **RNF-02** | **Eficiencia de Desempeño** | El registro y confirmación de una venta completa (transacción ACID con 1 a 10 productos) debe completarse en $\le 2.0$ segundos en entorno local. |
| **RNF-03** | **Fiabilidad (Consistencia)** | Cero inconsistencias en inventario. Dos ventas concurrentes sobre la última unidad de un repuesto deben resultar en una venta aprobada y una rechazada limpiamente por falta de stock. |
| **RNF-04** | **Seguridad** | Las contraseñas se almacenan mediante hash irreversible con sal. Endpoints protegidos mediante tokens o validación de sesión de usuario; usuarios con rol `VENDEDOR` tienen acceso restringido a funciones administrativas. |
| **RNF-05** | **Usabilidad (Interacción)** | La interfaz de ventas en mostrador debe permitir registrar una transacción en menos de 4 pasos o clics, con validaciones inmediatas en campos numéricos y mensajes de error claros y accionables. |
| **RNF-06** | **Mantenibilidad** | Código fuente modular estructurado por capas en Flask y componentes reutilizables en React. Suite de pruebas automatizadas que cubra los casos de uso críticos de negocio. |
| **RNF-07** | **Portabilidad y Simplicidad** | Despliegue nativo ejecutable en cualquier máquina estándar con Windows/Linux utilizando Python 3.12, Node.js y MySQL local (XAMPP/Laragon) sin requerir virtualización Docker. |
| **RNF-08** | **Integridad y Trazabilidad** | Todas las entradas inválidas en formularios (cantidades negativas, precios en cero, caracteres alfabéticos en campos monetarios) deben ser rechazadas con código HTTP 400/422. |

---

## 5. Arquitectura del Software

El sistema adopta una **Arquitectura Cliente-Servidor Desacoplada** basada en servicios RESTful:

```
+-------------------------------------------------------------+
|                CAPA CLIENTE (FRONTEND)                      |
|  React 18 + Vite + Tailwind CSS + Lucide Icons              |
|  - Pantalla Catálogo y Búsqueda Rápida con Filtros          |
|  - Módulo Punto de Venta (POS) / Carrito de Mostrador       |
|  - Panel de Alertas de Stock Bajo y Movimientos             |
+------------------------------+------------------------------+
                               |
                   Peticiones HTTP / JSON REST
                               |
+------------------------------v------------------------------+
|                CAPA SERVIDOR (BACKEND API)                  |
|  Python 3.12 + Flask                                        |
|  ├── Rutas y Controladores (/api/v1/productos, /ventas...)  |
|  ├── Servicios de Negocio (Lógica de inventario y ventas)   |
|  ├── Validadores y Middlewares (Roles, autenticación)       |
|  └── Capa de Persistencia / Repositorios                     |
+------------------------------+------------------------------+
                               |
                       Consultas SQL / TCP
                               |
+------------------------------v------------------------------+
|                CAPA DE DATOS (PERSISTENCIA)                 |
|  MySQL 8.0 / MariaDB (Motor InnoDB)                         |
|  - Tablas: usuarios, roles, categorias, repuestos,           |
|            ventas, detalle_ventas, auditoria                |
|  - Restricciones CHECK (stock >= 0, precio > 0)             |
|  - Transacciones ACID (BEGIN, COMMIT, ROLLBACK)             |
+-------------------------------------------------------------+
```

### Modelo Relacional Simplificado de Base de Datos
* **`roles`**: `id`, `nombre` (`ADMIN`, `VENDEDOR`, `INVENTARIO`), `descripcion`.
* **`usuarios`**: `id`, `rol_id` (FK), `nombre`, `email` (UK), `password_hash`, `activo`, `created_at`.
* **`categorias`**: `id`, `nombre` (UK), `descripcion`.
* **`repuestos`**: `id`, `categoria_id` (FK), `codigo_referencia` (UK), `codigo_oem`, `nombre`, `marca_moto`, `precio_compra`, `precio_venta`, `stock_actual`, `stock_minimo`, `activo`.
* **`ventas`**: `id`, `usuario_id` (FK), `numero_factura` (UK), `subtotal`, `iva`, `total`, `estado` (`COMPLETADA`, `ANULADA`), `created_at`.
* **`detalle_ventas`**: `id`, `venta_id` (FK), `repuesto_id` (FK), `cantidad`, `precio_unitario`, `subtotal`.
* **`auditoria_movimientos`**: `id`, `repuesto_id` (FK), `usuario_id` (FK), `tipo_movimiento` (`VENTA`, `COMPRA`, `ANULACION`, `AJUSTE`), `cantidad`, `stock_anterior`, `stock_nuevo`, `created_at`.

---

## 6. Estructura Oficial del Repositorio

La disposición de archivos sigue con exactitud la pauta obligatoria del curso:

```text
TALLER-FINAL-main/
├── README.md                      # Presentación institucional, roles, arquitectura y guía de uso
├── .gitignore                     # Exclusión de entornos virtuales (venv), node_modules y credenciales
├── docs/
│   ├── especificacion.md          # Requisitos RF/RNF formales y criterios de aceptación BDD (Gherkin)
│   ├── plan-de-pruebas.md         # Casos CP-01 a CP-18, técnicas BVA/EP y matriz de trazabilidad RTM
│   └── informe-calidad.md         # Evaluación ISO/IEC 25010, bitácora de defectos (DEF-01..04) y mantenimiento
├── src/
│   ├── backend/                   # API REST en Python Flask
│   │   ├── app.py                 # Punto de entrada de la aplicación Flask
│   │   ├── config.py              # Variables de configuración (BD, puerto, secretos)
│   │   ├── requirements.txt       # Dependencias de Python (Flask, Flask-CORS, PyMySQL, etc.)
│   │   ├── database/
│   │   │   ├── connection.py      # Conector y pool a MySQL con fallback de pruebas
│   │   │   └── schema.sql         # DDL oficial con tablas, llaves foráneas y datos semilla
│   │   ├── routes/                # Controladores HTTP (/auth, /productos, /ventas, /reportes)
│   │   ├── services/              # Lógica de negocio (ventas atómicas, control de stock)
│   │   └── models/                # Estructuras de datos y mapeos
│   └── frontend/                  # Cliente Web en React 18
│       ├── package.json           # Dependencias npm (react, react-dom, lucide-react, vite)
│       ├── vite.config.js         # Configuración del servidor de desarrollo Vite
│       ├── tailwind.config.js     # Configuración de estilos y tokens visuales
│       ├── index.html             # Punto de entrada HTML
│       └── src/
│           ├── main.jsx           # Montaje de la aplicación React
│           ├── App.jsx            # Enrutador principal y componentes globales
│           ├── components/        # Componentes UI reutilizables (Navbar, Alertas, Modal)
│           ├── screens/           # Pantallas: Catalogo, VentasPOS, Inventario, Login
│           └── services/          # Cliente HTTP (`api.js`) para consumir el backend Flask
└── tests/
    ├── backend/                   # Pruebas automatizadas en Python (pytest)
    │   ├── test_productos.py      # Pruebas de CRUD, validaciones y filtros
    │   ├── test_ventas_stock.py   # Pruebas críticas de consistencia y anti-sobreventa
    │   └── conftest.py            # Fixtures y base de datos de prueba en memoria/transaccional
    └── frontend/                  # Pruebas de componentes interfaz (Vitest)
```

---

## 7. Guía de Instalación y Ejecución Local (Paso a Paso)

Este proyecto no requiere Docker. Se ejecuta directamente sobre el sistema operativo del estudiante o evaluador.

### 7.1. Requisitos Previos
* **Python 3.12+** instalado en el sistema.
* **Node.js (v18+) y npm** instalados.
* **Servidor MySQL activo:** Puede utilizarse **XAMPP** (iniciando el módulo MySQL desde el panel de control), **Laragon** o una instancia nativa de MySQL Server en el puerto estándar `3306`.

---

### 7.2. Paso 1: Configurar la Base de Datos (MySQL)
1. Inicie su motor de MySQL (por ejemplo, desde el panel de **XAMPP** haciendo clic en **Start** en MySQL).
2. Abra su cliente preferido (phpMyAdmin en `http://localhost/phpmyadmin`, MySQL Workbench, DBeaver o la consola de MySQL).
3. Ejecute el script DDL de creación ubicado en `src/backend/database/schema.sql`:
   ```sql
   CREATE DATABASE IF NOT EXISTS allquality_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   USE allquality_db;
   SOURCE src/backend/database/schema.sql;
   ```
   *(Este script crea las tablas de catálogo, usuarios por defecto y datos semilla de repuestos de prueba).*

---

### 7.3. Paso 2: Poner en Marcha el Backend (Flask)
Abra una terminal de comandos en la carpeta raíz del proyecto:

```powershell
# 1. Navegar a la carpeta del backend
cd src/backend

# 2. Crear el entorno virtual de Python
python -m venv venv

# 3. Activar el entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# (O si usa Command Prompt clásico: .\venv\Scripts\activate.bat)

# 4. Instalar las dependencias requeridas
pip install -r requirements.txt

# 5. Iniciar el servidor Flask
python app.py
```

*El backend iniciará escuchando en `http://127.0.0.1:5000` con la API REST disponible en `http://127.0.0.1:5000/api/v1`.*

---

### 7.4. Paso 3: Poner en Marcha el Frontend (React)
Abra **otra terminal independiente** en la raíz del proyecto:

```powershell
# 1. Navegar a la carpeta del frontend
cd src/frontend

# 2. Instalar los paquetes npm
npm install

# 3. Iniciar el servidor de desarrollo Vite
npm run dev
```

*Abra su navegador en **`http://localhost:5173`** para interactuar con la aplicación comercial.*

---

## 8. Ejecución de Pruebas Automatizadas

El proyecto cuenta con suites de pruebas automatizadas diseñadas con técnicas de **Caja Negra** (Análisis de Valores Límite y Partición de Equivalencia) para certificar la fiabilidad y consistencia del inventario:

### Ejecutar Pruebas del Backend (Python / pytest)
Desde la carpeta raíz o `src/backend` con el entorno virtual activo:

```powershell
# Ejecutar todas las pruebas automatizadas con reporte detallado
pytest tests/backend -v

# Ejecutar únicamente las pruebas críticas de concurrencia y validación de stock
pytest tests/backend/test_ventas_stock.py -v
```

### Ejecutar Pruebas del Frontend (si aplica)
```powershell
cd src/frontend
npm test
```

---

## 9. Resumen de Calidad y Registro de Defectos (Seguimiento 2)

Durante las iteraciones de aseguramiento de calidad (lideradas por **Steven Rendón** y verificadas por **Cristian Carabalí**), se detectaron, corrigieron y blindaron los siguientes defectos críticos de ingeniería:

| ID Defecto | Descripción del Fallo Detectado | Severidad | Causa Raíz | Solución y Blindaje Aplicado | Estado |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **DEF-01** | **Venta de repuestos con stock insuficiente (Stock Negativo)** | Crítica | La verificación de existencias se ejecutaba en memoria sin bloqueo transaccional previo al guardado. | Se implementó transacción atómica en MySQL con validación estricta y restricción `CHECK (stock_actual >= 0)`. | **Mitigado y Probado** |
| **DEF-02** | **Venta duplicada por reintento rápido en mostrador** | Alta | La interfaz no deshabilitaba el botón de confirmación durante la petición HTTP, enviando dos solicitudes consecutivas. | Se incorporó token de idempotencia en la venta y bloqueo visual en React con estado de carga `isSubmitting`. | **Mitigado y Probado** |
| **DEF-03** | **Discrepancia en cálculo de subtotales con decimales** | Media | Inconsistencia de tipo de dato flotante (`float`) al calcular precios unitarios y porcentajes de descuento. | Se estandarizó el uso de tipos decimales de precisión fija (`DECIMAL(12,2)`) tanto en base de datos como en Python (`Decimal`). | **Mitigado y Probado** |
| **DEF-04** | **Bypass de permisos en anulación de ventas** | Alta | La ruta de anulación permitía el consumo directo con rol `VENDEDOR` sin solicitar elevación de privilegios. | Implementación de decorador de seguridad `@require_role('ADMIN')` en los endpoints protegidos de Flask. | **Mitigado y Probado** |

---

## 10. Referencia de Endpoints de la API REST (`/api/v1`)

| Método | Endpoint | Rol Requerido | Descripción |
| :---: | :--- | :---: | :--- |
| `POST` | `/api/v1/auth/login` | Público | Autenticación de usuarios; retorna datos de sesión y rol. |
| `GET` | `/api/v1/productos` | Todos | Listado de repuestos con soporte de paginación y búsqueda (`?q=`, `?cat=`). |
| `POST` | `/api/v1/productos` | `ADMIN`, `INVENTARIO` | Registro de un nuevo repuesto con validación de código único. |
| `PUT` | `/api/v1/productos/<id>` | `ADMIN`, `INVENTARIO` | Actualización de precios, stock mínimo y descripción. |
| `GET` | `/api/v1/inventario/alertas` | Todos | Consulta de productos que han alcanzado o superado el stock mínimo. |
| `POST` | `/api/v1/ventas` | `VENDEDOR`, `ADMIN` | Registro transaccional de venta y descuento atómico de inventario. |
| `GET` | `/api/v1/ventas/<id>` | `VENDEDOR`, `ADMIN` | Consulta detallada de una venta y sus ítems de repuestos. |
| `POST` | `/api/v1/ventas/<id>/anular` | `ADMIN` | Anulación formal de venta y reintegro controlado de unidades al stock. |
| `GET` | `/api/v1/reportes/ventas` | `ADMIN` | Consulta de totales de ventas agrupados por periodos de tiempo. |

---

## 11. Guía de Trazabilidad y Gestión de Commits con Trello

Para cumplir estrictamente con los criterios de evaluación del profesor **Felipe Gutiérrez Isaza**, el equipo sigue una política rigurosa de control de versiones:

### Formato Estándar de Mensajes de Commit (Conventional Commits)
Cada commit debe reflejar una tarea concreta y contener el rol o contexto del autor:
* `docs: estructurar README maestro con roles, arquitectura Flask+React y guía local`
* `feat(backend): agregar modelo de repuestos y conexión a MySQL`
* `feat(frontend): crear interfaz de mostrador para registro de ventas`
* `test(backend): automatizar pruebas con pytest para validación de stock negativo`
* `fix(ventas): corregir condición de carrera en descuento simultáneo de inventario`

### Procedimiento de Sincronización con Trello:
1. Al iniciar una tarea, mueva la tarjeta correspondiente de la lista **"Por hacer"** a **"En curso"**.
2. Al finalizar el código y sus pruebas locales, mueva la tarjeta a **"En revisión"** y agregue en la descripción el hash del commit de Git (ej. `Commit: abc1234`).
3. Tras la revisión del líder técnico o responsable de calidad, la tarjeta pasa a **"Hecho"**.
4. Cada entrega formal se sella en Git mediante una etiqueta (tag) inmutable:
   ```powershell
   git tag entrega-s1
   git push origin entrega-s1
   ```
