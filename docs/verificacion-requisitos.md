# Verificación de Requisitos — Entrega 2

## Sistema de Gestión Comercial «AllQuality»

**Asignatura:** Ingeniería de Software II  
**Institución:** Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)  
**Periodo Académico:** 2026-2  
**Alcance:** estado funcional y documental del repositorio para la **Entrega 2**  
**Fecha de verificación:** 10 de noviembre de 2026

---

## 1. Propósito y alcance

Este documento responde una pregunta concreta: **qué requisitos están realmente implementados y comprobados en la Entrega 2**, sin confundirlos con los que se pueden incorporar en la entrega final.

La verificación se hizo sobre el código del repositorio, la suite automatizada y una instancia real de **MariaDB 10.4.32 de XAMPP**. No se declaran como terminados los módulos que todavía no existen.

### 1.1. Resumen ejecutivo

| Grupo | Resultado |
| :--- | :--- |
| Requisitos **Must Have** implementados | **12 de 12** (RF-01 a RF-07, RF-11, RF-12, RF-13, RF-17 y RF-18). |
| Requisitos **Should Have** | RF-09 queda **parcial** mediante ajuste manual auditado; RF-08, RF-10 y RF-16 se reservan para la entrega final. |
| Requisitos **Could Have** | RF-14 y RF-15 no tienen flujo integrado; pueden abordarse en la entrega final. |
| Pruebas automatizadas | **49 aprobadas, 0 fallidas**. |
| Cobertura de código | **90%** con `pytest-cov`. |
| Frontend | Compila con Vite y los flujos principales se recorrieron con Playwright y Chrome. |
| Base de datos real | MariaDB 10.4.32 de XAMPP, esquema importado, venta y auditoría verificadas manualmente. |

> **Conclusión honesta:** la Entrega 2 cubre todos los requisitos Must Have definidos en la especificación. No cubre todavía los módulos de compras, anulación de ventas, reportes ni respaldo/restauración integrados; esos puntos se documentan como pendientes para la entrega final y no se presentan como funcionalidades terminadas.

---

## 2. Evidencia utilizada

| Evidencia | Comando / ubicación | Resultado |
| :--- | :--- | :--- |
| Suite automatizada | `python -m pytest tests/backend -q --cov=src/backend --cov-report=term-missing` | 49 passed; 90% total |
| Compilación del frontend | `cd src/frontend && npm run build` | `vite build` sin errores |
| Verificación de interfaz | Playwright + Google Chrome contra Vite | Login, panel, catálogo, inventario, ventas, usuarios y cierre de sesión sin errores de consola |
| Verificación de API real | Script temporal contra `127.0.0.1:5000` + MariaDB XAMPP | Login, catálogo, venta, rollback, auditoría y usuarios comprobados |
| Estado de la base | `allquality_db` importada desde `src/backend/database/schema.sql` | 5 categorías, 5 repuestos y 3 usuarios semilla |
| Diagramas | `docs/diagramas/` y `docs/diagramas.md` | 7 imágenes PNG y código Mermaid plegable |
| Documentación | `README.md`, `docs/especificacion.md`, `docs/plan-de-pruebas.md`, `docs/informe-calidad.md` | Enlaces y cifras alineadas con la verificación |

### 2.1. Pruebas por archivo

| Archivo | Pruebas | Propósito |
| :--- | :---: | :--- |
| `tests/backend/test_auth.py` | 3 | Login válido, contraseña incorrecta y usuario inexistente. |
| `tests/backend/test_auth_roles.py` | 6 | Token ausente o inválido, lectura autenticada y rechazo de escrituras por rol. |
| `tests/backend/test_productos.py` | 7 | Listado, búsqueda, creación, stock obligatorio, duplicados, precios límite y desactivación. |
| `tests/backend/test_inventario_s1.py` | 5 | Alertas, ajuste, stock negativo, venta atómica y anti-sobreventa. |
| `tests/backend/test_api_extra.py` | 20 | Health, errores HTTP, categorías, actualización, historial y detalle de ventas. |
| `tests/backend/test_usuarios.py` | 8 | Alta, roles, correo único, suspensión, revocación de sesión y restricción a `ADMIN`. |
| **Total** | **49** | Flujos funcionales y de seguridad de la Entrega 2. |

---

## 3. Matriz de requisitos funcionales

Estados: **Cumple** = implementado y con evidencia; **Parcial** = existe una parte funcional, pero no todo el criterio; **Pendiente** = no implementado en esta entrega.

| Código | Requisito | Prioridad | Estado | Evidencia y observación |
| :---: | :--- | :---: | :---: | :--- |
| **RF-01** | Autenticación y control de sesión | Must | **Cumple** | Login con contraseñas `pbkdf2:sha256`; token firmado con `itsdangerous`; vigencia de 8 horas; mensaje genérico para credenciales inválidas. Pruebas: `test_auth.py`, `test_auth_roles.py`. |
| **RF-02** | Crear y administrar repuestos | Must | **Cumple** | Alta con código, nombre, categoría, precio y stock obligatorios; código único (409), precios y stock inválidos (422). Pruebas: `test_productos.py`, `test_api_extra.py`. |
| **RF-03** | Consultar y buscar productos | Must | **Cumple** | Búsqueda parcial por nombre, referencia y OEM; filtro por categoría; lista vacía con 200. Pruebas de catálogo y API. |
| **RF-04** | Editar o desactivar repuesto | Must | **Cumple** | `PUT /productos/{id}` y desactivación lógica (`activo = 0`) sin borrar historial. Pruebas: `test_actualizar_producto_*`, `test_desactivar_repuesto_logico`. |
| **RF-05** | Registrar venta | Must | **Cumple** | Venta de una o varias líneas, subtotales y total; carrito vacío rechazado. Verificado con venta real y pruebas de API. |
| **RF-06** | Actualización atómica de inventario | Must | **Cumple** | `FOR UPDATE`, transacción y `rollback`; verificación manual multiítem contra MariaDB (stock sin cambios si falla una línea). Prueba automatizada de descuento y sobreventa. |
| **RF-07** | Validación anti-sobreventa | Must | **Cumple** | Rechazo con 400 si `cantidad > stock`; mensaje con unidades disponibles; inventario sin valores negativos. Prueba `test_bloqueo_sobreventa_stock_insuficiente`. |
| **RF-08** | Registrar compras a proveedores | Should | **Pendiente** | No existe módulo de compras ni órdenes a proveedores. Reservado para la entrega final. |
| **RF-09** | Entrada y confirmación de mercancía | Should | **Parcial** | El ajuste manual autorizado incrementa stock y deja auditoría; no existe recepción de compra ni inspección de mercancía. |
| **RF-10** | Anulación autorizada de ventas | Should | **Pendiente** | No existe endpoint ni interfaz de anulación/reintegro. Reservado para la entrega final. |
| **RF-11** | Alertas de stock bajo | Must | **Cumple** | `GET /inventario/alertas` compara `stock_actual <= stock_minimo`; se muestra en el panel e inventario. Pruebas de inventario. |
| **RF-12** | Administrar usuarios y roles | Must | **Cumple** | API y pantalla `/usuarios` solo para `ADMIN`: alta, cambio de rol, suspensión y reactivación. La suspensión invalida el token anterior. Pruebas: `test_usuarios.py`. |
| **RF-13** | Control de permisos por rol | Must | **Cumple** | Decoradores `@require_auth` y `@require_role` en categorías, productos, inventario, ventas y usuarios. Pruebas 401/403 y verificación Playwright. |
| **RF-14** | Copias de seguridad | Could | **Pendiente** | No hay botón ni endpoint de backup. Solo sería posible un `mysqldump` manual, que no cuenta como funcionalidad integrada. |
| **RF-15** | Restauración de datos | Could | **Pendiente** | No existe flujo de restauración desde la aplicación. |
| **RF-16** | Reportes comerciales | Should | **Pendiente** | No hay resúmenes por periodo ni productos de mayor rotación. Reservado para la entrega final. |
| **RF-17** | Cálculo exacto de totales | Must | **Cumple** | Columnas monetarias `DECIMAL(12,2)` en ventas y detalle; subtotales calculados y verificados en MariaDB. |
| **RF-18** | Historial de auditoría | Must | **Cumple** | `auditoria_movimientos` guarda usuario, tipo, cantidad, stock anterior/nuevo, justificación y fecha para ventas y ajustes. Verificado manualmente. |

### 3.1. Lectura por prioridad MoSCoW

- **Must Have:** 12/12 implementados y con evidencia.
- **Should Have:** 1 parcial (RF-09) y 3 pendientes (RF-08, RF-10, RF-16).
- **Could Have:** 2 pendientes (RF-14, RF-15).

---

## 4. Matriz de requisitos no funcionales

| Código | Requisito | Estado | Evidencia / límite actual |
| :---: | :--- | :---: | :--- |
| **RNF-01** | p95 de catálogo ≤ 1.5 s | **Parcial** | Respuestas locales rápidas, pero no se ejecutó un benchmark formal con 1.000 repuestos. |
| **RNF-02** | Hash de contraseñas y roles en servidor | **Cumple** | `werkzeug.security`, token firmado y decoradores de rol; faltan HTTPS, `SECRET_KEY` propia de producción y rate limiting. |
| **RNF-03** | Usabilidad y flujo de venta ≤ 4 clics | **Cumple** | Flujo de venta verificado en Chrome/Playwright; formularios con validación y mensajes claros. |
| **RNF-04** | Consistencia ACID y cero sobreventas | **Parcial** | Transacción, bloqueo `FOR UPDATE` y rollback verificados; no se ejecutaron pruebas de concurrencia con usuarios simultáneos. |
| **RNF-05** | Compatibilidad con navegadores modernos | **Parcial** | Chrome verificado con Playwright; Firefox y Edge no se probaron formalmente. |
| **RNF-06** | Mantenibilidad y suite automatizada | **Cumple** | Arquitectura por capas, 49 pruebas y 90% de cobertura. |
| **RNF-07** | Despliegue local nativo sin Docker | **Cumple** | XAMPP MariaDB 10.4.32 + Flask + Vite en Windows; documentado en el README. |
| **RNF-08** | Restricciones de integridad en base de datos | **Cumple** | `CHECK` de precios/stock en el esquema y validaciones equivalentes en los servicios. |

---

## 5. Brechas y tareas para la entrega final

Estas brechas no bloquean la Entrega 2, pero deben resolverse antes de afirmar que el sistema cumple la especificación completa:

1. **RF-08 / RF-09:** módulo de compras, recepción e inspección de mercancía, con incremento automático de stock y auditoría.
2. **RF-10:** anulación de venta por parte del administrador, con reintegro exacto de stock y justificación.
3. **RF-14 / RF-15:** respaldo y restauración desde la aplicación, con validación de la copia.
4. **RF-16:** reportes de ventas por periodo y productos de mayor rotación.
5. **RNF-01:** benchmark reproducible con un volumen de datos representativo.
6. **RNF-04:** pruebas de concurrencia sobre la última unidad disponible.
7. **RNF-05:** verificación en Firefox y Edge, además de Chrome.
8. **Integración automatizada:** suite contra MariaDB/MySQL real, además del doble de prueba actual.
9. **Endurecimiento de producción:** `SECRET_KEY` desde entorno, HTTPS, CORS restringido, rate limiting y recuperación de contraseña.
10. **Trazabilidad del equipo:** la evidencia de Trello no pudo verificarse desde este entorno; debe adjuntarse antes de la entrega final.

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

## 7. Control de cambios

- No se ejecutó `git commit`, `git tag` ni `git push` durante esta verificación.
- Los cambios quedan en el árbol de trabajo para revisión del líder técnico y del responsable de documentación.
- La etiqueta y el envío al repositorio remoto requieren autorización expresa del equipo.

---

**Elaborado por:** Cristian Carabalí — Responsable de Pruebas (QA Lead)  
**Revisión de calidad:** Steven Rendón — Responsable de Calidad  
**Revisión de documentación:** Santiago Calvo — Responsable de Documentación  
**Aprobación de integración:** Alejandro Londoño — Líder Técnico
