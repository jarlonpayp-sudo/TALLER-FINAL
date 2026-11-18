# Verificación de Requisitos — Entrega final

## Sistema de Gestión Comercial «AllQuality»

**Asignatura:** Ingeniería de Software II  
**Institución:** Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)  
**Periodo Académico:** 2026-2  
**Alcance:** estado funcional y documental del repositorio para la **entrega final**

**Fecha de verificación:** 18 de noviembre de 2026

---

## 1. Propósito y alcance

Este documento responde una pregunta concreta: **qué requisitos están realmente implementados y comprobados en la entrega final**, sin confundirlos con los que permanecen en el backlog.

La verificación se hizo sobre el código del repositorio, la suite automatizada y una instancia real de **MariaDB 10.4.32 de XAMPP**. No se declaran como terminados los módulos que todavía no existen.

### 1.1. Resumen ejecutivo

| Grupo | Resultado |
| :--- | :--- |
| Requisitos **Must Have** implementados | **12 de 12** (RF-01 a RF-07, RF-11, RF-12, RF-13, RF-17 y RF-18). |
| Requisitos **Should Have** | RF-09 queda **parcial** mediante ajuste manual auditado; RF-08, RF-10 y RF-16 permanecen **no implementados (backlog)**. |
| Requisitos **Could Have** | RF-14 y RF-15 permanecen **no implementados (backlog)**. |
| Pruebas automatizadas | **49 aprobadas, 0 fallidas**. |
| Cobertura de código | **90%** con `pytest-cov`. |
| Catálogo de prueba | **25 productos** (24 activos, 2 agotados, 2 con stock bajo y 1 inactivo) en **5 categorías**. |
| Frontend | Compila con Vite y los flujos principales se recorrieron con Playwright y Chrome. |
| Capturas finales | `docs/capturas/panel-principal.png`, `productos.png`, `inventario.png` y `nueva-venta.png` | Panel con 24 productos activos y 4 alertas, catálogo, inventario y pantalla de nueva venta verificados el 18/11/2026. |
| Base de datos real | MariaDB 10.4.32 de XAMPP con 25 productos, 5 categorías, 3 usuarios semilla + 1 usuario de prueba local y ventas de prueba; catálogo y auditoría verificados manualmente. |

> **Conclusión honesta:** la entrega final cubre todos los requisitos Must Have definidos en la especificación. No implementa los módulos de compras, anulación de ventas, reportes ni respaldo/restauración integrados; esos puntos se documentan como backlog y no se presentan como funcionalidades terminadas.

---

## 2. Evidencia utilizada

| Evidencia | Comando / ubicación | Resultado |
| :--- | :--- | :--- |
| Suite automatizada | `python -m pytest tests/backend -q --cov=src/backend --cov-report=term-missing` | 49 passed; 90% total |
| Compilación del frontend | `cd src/frontend && npm run build` | `vite build` sin errores |
| Verificación de interfaz | Playwright + Google Chrome contra Vite | Login, panel, catálogo, inventario, ventas, usuarios y cierre de sesión sin errores de consola |
| Verificación de API real | Script temporal contra `127.0.0.1:5000` + MariaDB XAMPP | Login, catálogo de 25 productos (24 activos), venta, rollback, auditoría y usuarios comprobados |
| Estado de la base local | `allquality_db` actualizada desde `schema.sql` y datos de prueba | 25 repuestos (24 activos, 2 agotados, 2 con stock bajo y 1 inactivo), 5 categorías, 3 usuarios semilla + 1 usuario de prueba local y 2 ventas de prueba |
| Diagramas | `docs/diagramas/` y `docs/diagramas.md` | 7 imágenes PNG y código Mermaid plegable |
| Documentación | `README.md`, `docs/especificacion.md`, `docs/plan-de-pruebas.md`, `docs/informe-calidad.md`, `docs/modelo-datos.md` | Enlaces y cifras alineadas con la verificación final |

### 2.1. Pruebas por archivo

| Archivo | Pruebas | Propósito |
| :--- | :---: | :--- |
| `tests/backend/test_auth.py` | 3 | Login válido, contraseña incorrecta y usuario inexistente. |
| `tests/backend/test_auth_roles.py` | 6 | Token ausente o inválido, lectura autenticada y rechazo de escrituras por rol. |
| `tests/backend/test_productos.py` | 7 | Listado y búsqueda del catálogo de 25 productos, creación, stock obligatorio, duplicados, precios límite y desactivación. |
| `tests/backend/test_inventario_s1.py` | 5 | Alertas del catálogo ampliado, ajuste, stock negativo, venta atómica y anti-sobreventa. |
| `tests/backend/test_api_extra.py` | 20 | Health, errores HTTP, 5 categorías, actualización, historial y detalle de ventas. |
| `tests/backend/test_usuarios.py` | 8 | Alta, roles, correo único, suspensión, revocación de sesión y restricción a `ADMIN`. |
| **Total** | **49** | Flujos funcionales y de seguridad de la entrega final. |

---

## 3. Matriz de requisitos funcionales

Estados: **Cumple** = implementado y con evidencia; **Parcial** = existe una parte funcional, pero no todo el criterio; **No implementado (backlog)** = no forma parte del alcance de esta entrega.

| Código | Requisito | Prioridad | Estado | Evidencia y observación |
| :---: | :--- | :---: | :---: | :--- |
| **RF-01** | Autenticación y control de sesión | Must | **Cumple** | Login con contraseñas `pbkdf2:sha256`; token firmado con `itsdangerous`; vigencia de 8 horas; mensaje genérico para credenciales inválidas. Pruebas: `test_auth.py`, `test_auth_roles.py`. |
| **RF-02** | Crear y administrar repuestos | Must | **Cumple** | Alta con código, nombre, categoría, precio y stock obligatorios; código único (409), precios y stock inválidos (422). Pruebas: `test_productos.py`, `test_api_extra.py`. |
| **RF-03** | Consultar y buscar productos | Must | **Cumple** | Búsqueda parcial por nombre, referencia y OEM; filtro por categoría; lista vacía con 200. Pruebas de catálogo y API sobre 25 productos y 5 categorías. |
| **RF-04** | Editar o desactivar repuesto | Must | **Cumple** | `PUT /productos/{id}` y desactivación lógica (`activo = 0`) sin borrar historial. Pruebas: `test_actualizar_producto_*`, `test_desactivar_repuesto_logico`. |
| **RF-05** | Registrar venta | Must | **Cumple** | Venta de una o varias líneas, subtotales y total; carrito vacío rechazado. Verificado con venta real y pruebas de API. |
| **RF-06** | Actualización atómica de inventario | Must | **Cumple** | `FOR UPDATE`, transacción y `rollback`; verificación manual multiítem contra MariaDB (stock sin cambios si falla una línea). Prueba automatizada de descuento y sobreventa. |
| **RF-07** | Validación anti-sobreventa | Must | **Cumple** | Rechazo con 400 si `cantidad > stock`; mensaje con unidades disponibles; inventario sin valores negativos. Prueba `test_bloqueo_sobreventa_stock_insuficiente`. |
| **RF-08** | Registrar compras a proveedores | Should | **No implementado (backlog)** | No existe módulo de compras ni órdenes a proveedores. |
| **RF-09** | Entrada y confirmación de mercancía | Should | **Parcial** | El ajuste manual autorizado incrementa stock y deja auditoría; no existe recepción de compra ni inspección de mercancía. |
| **RF-10** | Anulación autorizada de ventas | Should | **No implementado (backlog)** | No existe endpoint ni interfaz de anulación/reintegro. |
| **RF-11** | Alertas de stock bajo | Must | **Cumple** | `GET /inventario/alertas` compara `stock_actual <= stock_minimo`; la suite valida 4 alertas sobre el catálogo de prueba. |
| **RF-12** | Administrar usuarios y roles | Must | **Cumple** | API y pantalla `/usuarios` solo para `ADMIN`: alta, cambio de rol, suspensión y reactivación. La suspensión invalida el token anterior. Pruebas: `test_usuarios.py`. |
| **RF-13** | Control de permisos por rol | Must | **Cumple** | Decoradores `@require_auth` y `@require_role` en categorías, productos, inventario, ventas y usuarios. Pruebas 401/403 y verificación Playwright. |
| **RF-14** | Copias de seguridad | Could | **No implementado (backlog)** | No hay botón ni endpoint de backup. Solo sería posible un `mysqldump` manual, que no cuenta como funcionalidad integrada. |
| **RF-15** | Restauración de datos | Could | **No implementado (backlog)** | No existe flujo de restauración desde la aplicación. |
| **RF-16** | Reportes comerciales | Should | **No implementado (backlog)** | No hay resúmenes por periodo ni productos de mayor rotación. |
| **RF-17** | Cálculo exacto de totales | Must | **Cumple** | Columnas monetarias `DECIMAL(12,2)` en ventas y detalle; subtotales calculados y verificados en MariaDB. |
| **RF-18** | Historial de auditoría | Must | **Cumple** | `auditoria_movimientos` guarda usuario, tipo, cantidad, stock anterior/nuevo, justificación y fecha para ventas y ajustes. Verificado manualmente. |

### 3.1. Lectura por prioridad MoSCoW

- **Must Have:** 12/12 implementados y con evidencia.
- **Should Have:** 1 parcial (RF-09) y 3 no implementados (RF-08, RF-10, RF-16).
- **Could Have:** 2 no implementados (RF-14, RF-15).

---

## 4. Matriz de requisitos no funcionales

| Código | Requisito | Estado | Evidencia / límite actual |
| :---: | :--- | :---: | :--- |
| **RNF-01** | p95 de catálogo ≤ 1.5 s | **Parcial** | Respuestas locales rápidas, pero no se ejecutó un benchmark formal con 1.000 repuestos. |
| **RNF-02** | Hash de contraseñas y roles en servidor | **Cumple** | `werkzeug.security`, token firmado y decoradores de rol; faltan HTTPS, `SECRET_KEY` propia de producción y rate limiting. |
| **RNF-03** | Usabilidad y flujo de venta ≤ 4 clics | **Cumple** | Flujo de venta verificado en Chrome/Playwright; formularios con validación y mensajes claros. |
| **RNF-04** | Consistencia ACID y cero sobreventas | **Parcial** | Transacción, bloqueo `FOR UPDATE` y rollback verificados; no se ejecutaron pruebas de concurrencia con usuarios simultáneos. |
| **RNF-05** | Compatibilidad con navegadores modernos | **Parcial** | Chrome verificado con Playwright; Firefox y Edge no se probaron formalmente. |
| **RNF-06** | Mantenibilidad y suite automatizada | **Cumple** | Arquitectura por capas, 49 pruebas, 90% de cobertura y catálogo de 25 productos. |
| **RNF-07** | Despliegue local nativo sin Docker | **Cumple** | XAMPP MariaDB 10.4.32 + Flask + Vite en Windows; documentado en el README. |
| **RNF-08** | Restricciones de integridad en base de datos | **Cumple** | `CHECK` de precios/stock en el esquema y validaciones equivalentes en los servicios. |

---

## 5. Brechas y trabajo futuro (backlog)

Estas brechas **no forman parte del alcance implementado** en la entrega final. Se documentan para futuras iteraciones y para evitar presentarlas como funcionalidades terminadas:

1. **RF-08 / RF-09:** módulo de compras, recepción e inspección de mercancía, con incremento automático de stock y auditoría.
2. **RF-10:** anulación de venta por parte del administrador, con reintegro exacto de stock y justificación.
3. **RF-14 / RF-15:** respaldo y restauración desde la aplicación, con validación de la copia.
4. **RF-16:** reportes de ventas por periodo y productos de mayor rotación.
5. **RNF-01:** benchmark reproducible con un volumen de datos representativo.
6. **RNF-04:** pruebas de concurrencia sobre la última unidad disponible.
7. **RNF-05:** verificación en Firefox y Edge, además de Chrome.
8. **Integración automatizada:** suite contra MariaDB/MySQL real, además del doble de prueba actual.
9. **Endurecimiento de producción:** `SECRET_KEY` desde entorno, HTTPS, CORS restringido, rate limiting y recuperación de contraseña.
10. **Trazabilidad del equipo:** el tablero de Trello se mantiene fuera del repositorio; la evidencia de cada tarjeta debe estar disponible para la sustentación.

---

## 6. Cómo reproducir la verificación

Desde la raíz del repositorio:

```powershell
python -m pytest tests/backend -q --cov=src/backend --cov-report=term-missing
```

Compilación del frontend:

```powershell
cd src/frontend
npm run build
```

Base de datos local con XAMPP:

```powershell
C:\xampp\mysql\bin\mysql.exe -u root --default-character-set=utf8mb4 -e "source C:/ruta/al/proyecto/src/backend/database/schema.sql"
```

Comprobación rápida del catálogo:

```powershell
C:\xampp\mysql\bin\mysql.exe -u root --default-character-set=utf8mb4 -e "USE allquality_db; SELECT COUNT(*) AS total, SUM(activo = 1) AS activos FROM repuestos;"
```

Resultado esperado: **25 productos en total y 24 activos**.

Inicio del backend y del frontend:

```powershell
cd src/backend
python app.py

cd src/frontend
npm run dev
```

Credenciales de demostración:

| Rol | Correo | Contraseña |
| :--- | :--- | :--- |
| ADMIN | `admin@allquality.com` | `Admin123*` |
| VENDEDOR | `vendedor@allquality.com` | `Admin123*` |
| INVENTARIO | `bodega@allquality.com` | `Admin123*` |

> La suite automatizada usa `FakeMySQLConnection` para ser determinista. La verificación manual de esta entrega se realizó contra MariaDB 10.4.32; no se debe interpretar el 90% de cobertura como una prueba de concurrencia o de rendimiento real.

---

## 7. Control de cambios y cierre

- La entrega final se identifica con el tag `entrega-final`.
- La creación del commit, el tag y el push se realizan como último paso, previa autorización del equipo.
- El catálogo de prueba se amplió a 25 productos sin modificar los usuarios semilla ni las credenciales de demostración.
- Las pruebas y la documentación se actualizaron para reflejar el catálogo final, los 49 tests y la cobertura del 90%.

---

**Elaborado por:** Cristian Carabalí — Responsable de Pruebas (QA Lead)  
**Revisión de calidad:** Steven Rendón — Responsable de Calidad  
**Revisión de documentación:** Santiago Calvo — Responsable de Documentación  
**Aprobación de integración:** Alejandro Londoño — Líder Técnico
