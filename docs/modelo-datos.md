# Modelo de Datos — AllQuality

**Proyecto:** Sistema de Gestión Comercial de Repuestos para Motocicletas  
**Base de datos:** `allquality_db`  
**Motor:** MariaDB 10.4.32 (XAMPP) — InnoDB; compatible con MySQL 8.0+  
**Versión evaluada:** Entrega 2 — Aplicación web funcional (backend Flask + frontend React)  
**Responsable de documentación:** Santiago Calvo

---

## 1. Convenciones

| Símbolo | Significado |
| :--- | :--- |
| `PK` | Llave primaria. |
| `FK` | Llave foránea. |
| `UK` | Restricción de unicidad. |
| `NN` | Campo obligatorio (`NOT NULL`). |
| `AI` | Autoincremental. |
| `DECIMAL(12,2)` | Valor monetario con 12 dígitos y 2 decimales. |
| `TIMESTAMP` | Fecha y hora. |
| `TINYINT(1)` | Booleano lógico: `1` activo, `0` inactivo. |

El diagrama entidad-relación completo está en [Diagramas — Base de datos](diagramas.md#base-datos).

---

## 2. Resumen de tablas

| # | Tabla | Propósito | Registros semilla |
| :---: | :--- | :--- | :---: |
| 1 | `roles` | Catálogo de roles del sistema. | 3 |
| 2 | `usuarios` | Cuentas de acceso y rol asignado. | 3 |
| 3 | `categorias` | Clasificación comercial de repuestos. | 5 |
| 4 | `repuestos` | Catálogo central y existencias. | 5 |
| 5 | `ventas` | Cabecera de facturas. | 0 |
| 6 | `detalle_ventas` | Líneas de cada factura. | 0 |
| 7 | `auditoria_movimientos` | Kardex de entradas y salidas. | 0 |

---

## 3. Diccionario de datos

### 3.1. Tabla `roles`

Almacena los roles disponibles para el control de acceso.

| Campo | Tipo | Nulo | Clave / Default | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INT` | No | `PK`, `AI` | Identificador único del rol. |
| `nombre` | `VARCHAR(50)` | No | `UK` | Nombre del rol: `ADMIN`, `VENDEDOR`, `INVENTARIO`. |
| `descripcion` | `VARCHAR(255)` | Sí | `NULL` | Descripción funcional del rol. |
| `created_at` | `TIMESTAMP` | No | `CURRENT_TIMESTAMP` | Fecha de creación del registro. |

**Datos semilla:**

| id | nombre | descripción |
| :---: | :--- | :--- |
| 1 | `ADMIN` | Administrador del sistema con control total. |
| 2 | `VENDEDOR` | Personal de mostrador para ventas y consulta de precios. |
| 3 | `INVENTARIO` | Encargado de recepción de mercancía y ajustes de bodega. |

---

### 3.2. Tabla `usuarios`

Cuentas que operan el sistema. Cada venta y cada movimiento de auditoría queda asociado a un usuario.

| Campo | Tipo | Nulo | Clave / Default | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INT` | No | `PK`, `AI` | Identificador único del usuario. |
| `rol_id` | `INT` | No | `FK` → `roles.id` | Rol asignado; define los permisos. |
| `nombre` | `VARCHAR(100)` | No | — | Nombre visible del colaborador. |
| `email` | `VARCHAR(120)` | No | `UK` | Correo de inicio de sesión; no se repite. |
| `password_hash` | `VARCHAR(255)` | No | — | Contraseña cifrada; nunca se almacena en texto plano. |
| `activo` | `TINYINT(1)` | No | `1` | `1` permite el acceso; `0` deshabilita la cuenta. |
| `created_at` | `TIMESTAMP` | No | `CURRENT_TIMESTAMP` | Fecha de creación de la cuenta. |

**Relación:** `rol_id` referencia `roles.id` con `ON UPDATE CASCADE`. No se usa `ON DELETE CASCADE` para no borrar usuarios si se elimina un rol.

**Datos semilla:** tres usuarios de demostración (administrador, vendedor y bodega). Los datos son de ejemplo y no deben usarse como credenciales reales.

---

### 3.3. Tabla `categorias`

Clasifica los repuestos por familia comercial.

| Campo | Tipo | Nulo | Clave / Default | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INT` | No | `PK`, `AI` | Identificador de la categoría. |
| `nombre` | `VARCHAR(80)` | No | `UK` | Nombre de la categoría. |
| `descripcion` | `VARCHAR(255)` | Sí | `NULL` | Detalle de los productos que agrupa. |
| `created_at` | `TIMESTAMP` | No | `CURRENT_TIMESTAMP` | Fecha de creación. |

**Datos semilla:** Frenos; Motor y Transmisión; Eléctrico; Lubricantes y Químicos; Accesorios.

---

### 3.4. Tabla `repuestos`

Tabla central del inventario. Representa cada producto físico y su saldo actual.

| Campo | Tipo | Nulo | Clave / Default | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INT` | No | `PK`, `AI` | Identificador interno del repuesto. |
| `categoria_id` | `INT` | No | `FK` → `categorias.id` | Categoría a la que pertenece. |
| `codigo_referencia` | `VARCHAR(50)` | No | `UK` | Código interno o SKU del negocio. Evita duplicados. |
| `codigo_oem` | `VARCHAR(50)` | Sí | `NULL` | Código original del fabricante; útil para equivalencias. |
| `nombre` | `VARCHAR(150)` | No | — | Descripción comercial del repuesto. |
| `marca_moto` | `VARCHAR(80)` | Sí | `NULL` | Motos compatibles o marca de referencia. |
| `precio_compra` | `DECIMAL(12,2)` | No | `0.00` | Costo de adquisición; sirve para margen y valoración. |
| `precio_venta` | `DECIMAL(12,2)` | No | — | Precio al público; debe ser mayor que cero. |
| `stock_actual` | `INT` | No | `0` | Unidades disponibles hoy; no puede ser negativo. |
| `stock_minimo` | `INT` | No | `3` | Umbral de alerta cuando el saldo es menor o igual. |
| `activo` | `TINYINT(1)` | No | `1` | `1` visible y vendible; `0` descontinuado. |
| `created_at` | `TIMESTAMP` | No | `CURRENT_TIMESTAMP` | Fecha de alta del producto. |
| `updated_at` | `TIMESTAMP` | No | `CURRENT_TIMESTAMP ON UPDATE` | Se actualiza automáticamente al modificar el registro. |

**Restricciones:**

- `precio_venta > 0` (`chk_precio_venta`).
- `stock_actual >= 0` (`chk_stock_actual`).
- `stock_minimo >= 0` (`chk_stock_minimo`).
- `categoria_id` referencia `categorias.id` con `ON UPDATE CASCADE`.
- El borrado es lógico mediante `activo = 0`; no se elimina el registro.

**Datos semilla:** cinco repuestos de ejemplo. Los productos con `stock_actual <= stock_minimo` aparecen automáticamente en las alertas.

---

### 3.5. Tabla `ventas`

Cabecera de cada factura. No guarda los productos; eso se hace en `detalle_ventas`.

| Campo | Tipo | Nulo | Clave / Default | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INT` | No | `PK`, `AI` | Identificador interno de la venta. |
| `usuario_id` | `INT` | No | `FK` → `usuarios.id` | Usuario que registró la venta. |
| `numero_factura` | `VARCHAR(50)` | No | `UK` | Número visible de la factura. |
| `subtotal` | `DECIMAL(12,2)` | No | `0.00` | Suma de las líneas antes de impuestos. |
| `iva` | `DECIMAL(12,2)` | No | `0.00` | Impuesto de la venta. En la implementación actual se guarda `0.00`. |
| `total` | `DECIMAL(12,2)` | No | `0.00` | Valor final de la factura. Hoy equivale al subtotal. |
| `estado` | `VARCHAR(20)` | No | `COMPLETADA` | Estado de la venta: `COMPLETADA` o `ANULADA`. |
| `notas` | `TEXT` | Sí | `NULL` | Observaciones libres de la venta. |
| `created_at` | `TIMESTAMP` | No | `CURRENT_TIMESTAMP` | Fecha y hora de la venta. |

**Relación:** `usuario_id` referencia `usuarios.id`. No se elimina la venta; se cambia su estado a `ANULADA` para conservar la trazabilidad.

**Observación:** el servicio actual genera el número de factura como `FAC-<timestamp>-<aleatorio>` y no calcula IVA ni descuentos.

---

### 3.6. Tabla `detalle_ventas`

Líneas de la factura. Es la tabla puente entre `ventas` y `repuestos`.

| Campo | Tipo | Nulo | Clave / Default | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INT` | No | `PK`, `AI` | Identificador de la línea. |
| `venta_id` | `INT` | No | `FK` → `ventas.id` | Factura a la que pertenece. `ON DELETE CASCADE`. |
| `repuesto_id` | `INT` | No | `FK` → `repuestos.id` | Producto vendido. |
| `cantidad` | `INT` | No | — | Unidades vendidas; debe ser mayor que cero. |
| `precio_unitario` | `DECIMAL(12,2)` | No | — | Precio congelado al momento de la venta. |
| `subtotal` | `DECIMAL(12,2)` | No | — | Resultado de `cantidad × precio_unitario`. |

**Restricción:** `cantidad > 0` (`chk_cantidad`).

**Diseño:** el precio se copia a la línea para que una factura antigua no cambie si el precio del repuesto se actualiza después.

---

### 3.7. Tabla `auditoria_movimientos`

Kardex del inventario. Registra cada entrada o salida con el usuario, el saldo anterior y el saldo nuevo.

| Campo | Tipo | Nulo | Clave / Default | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INT` | No | `PK`, `AI` | Identificador del movimiento. |
| `repuesto_id` | `INT` | No | `FK` → `repuestos.id` | Producto afectado. |
| `usuario_id` | `INT` | No | `FK` → `usuarios.id` | Usuario que ejecutó el movimiento. |
| `tipo_movimiento` | `VARCHAR(30)` | No | — | `VENTA`, `COMPRA`, `ANULACION` o `AJUSTE`. |
| `cantidad` | `INT` | No | — | Cambio aplicado con signo: negativo si sale, positivo si entra. |
| `stock_anterior` | `INT` | No | — | Existencias antes del movimiento. |
| `stock_nuevo` | `INT` | No | — | Existencias después del movimiento. |
| `justificacion` | `VARCHAR(255)` | Sí | `NULL` | Motivo o referencia del movimiento. |
| `created_at` | `TIMESTAMP` | No | `CURRENT_TIMESTAMP` | Fecha y hora del movimiento. |

**Relaciones:** `repuesto_id` → `repuestos.id`; `usuario_id` → `usuarios.id`.

**Invariante de negocio:** `stock_nuevo = stock_anterior + cantidad`. El servicio impide que `stock_nuevo` sea negativo.

**Observación:** el tipo de movimiento es texto libre; para la entrega final se recomienda convertirlo en `ENUM` o agregar un `CHECK` con los valores permitidos.

---

## 4. Relaciones y cardinalidades

| Relación | Cardinalidad | Llave foránea | Comportamiento |
| :--- | :---: | :--- | :--- |
| `roles` → `usuarios` | 1:N | `usuarios.rol_id` | `ON UPDATE CASCADE` |
| `categorias` → `repuestos` | 1:N | `repuestos.categoria_id` | `ON UPDATE CASCADE` |
| `usuarios` → `ventas` | 1:N | `ventas.usuario_id` | Sin cascada |
| `ventas` → `detalle_ventas` | 1:N | `detalle_ventas.venta_id` | `ON DELETE CASCADE` |
| `repuestos` → `detalle_ventas` | 1:N | `detalle_ventas.repuesto_id` | Sin cascada |
| `repuestos` → `auditoria_movimientos` | 1:N | `auditoria_movimientos.repuesto_id` | Sin cascada |
| `usuarios` → `auditoria_movimientos` | 1:N | `auditoria_movimientos.usuario_id` | Sin cascada |

### Relación muchos a muchos

`detalle_ventas` materializa la relación **N:M** entre `ventas` y `repuestos`. Una venta puede tener muchos repuestos y un repuesto puede aparecer en muchas ventas. Los atributos propios de la relación son `cantidad`, `precio_unitario` y `subtotal`.

---

## 5. Restricciones de integridad

### Llaves primarias

Todas las tablas usan `id INT AUTO_INCREMENT PRIMARY KEY`.

### Llaves únicas

| Tabla | Campo |
| :--- | :--- |
| `roles` | `nombre` |
| `usuarios` | `email` |
| `categorias` | `nombre` |
| `repuestos` | `codigo_referencia` |
| `ventas` | `numero_factura` |

### Llaves foráneas

| Nombre | Tabla origen | Tabla destino | Regla |
| :--- | :--- | :--- | :--- |
| `fk_usuarios_roles` | `usuarios.rol_id` | `roles.id` | `ON UPDATE CASCADE` |
| `fk_repuestos_categorias` | `repuestos.categoria_id` | `categorias.id` | `ON UPDATE CASCADE` |
| `fk_ventas_usuarios` | `ventas.usuario_id` | `usuarios.id` | Sin cascada |
| `fk_detalles_ventas` | `detalle_ventas.venta_id` | `ventas.id` | `ON DELETE CASCADE` |
| `fk_detalles_repuestos` | `detalle_ventas.repuesto_id` | `repuestos.id` | Sin cascada |
| `fk_auditoria_repuestos` | `auditoria_movimientos.repuesto_id` | `repuestos.id` | Sin cascada |
| `fk_auditoria_usuarios` | `auditoria_movimientos.usuario_id` | `usuarios.id` | Sin cascada |

### Restricciones `CHECK`

| Nombre | Tabla | Regla |
| :--- | :--- | :--- |
| `chk_precio_venta` | `repuestos` | `precio_venta > 0` |
| `chk_stock_actual` | `repuestos` | `stock_actual >= 0` |
| `chk_stock_minimo` | `repuestos` | `stock_minimo >= 0` |
| `chk_cantidad` | `detalle_ventas` | `cantidad > 0` |

---

## 6. Datos semilla

El script `schema.sql` inserta datos de demostración con `INSERT IGNORE`:

- **Roles:** ADMIN, VENDEDOR, INVENTARIO.
- **Usuarios:** administrador, vendedor y bodega.
- **Categorías:** Frenos, Motor y Transmisión, Eléctrico, Lubricantes y Químicos, Accesorios.
- **Repuestos:** 5 productos de ejemplo con precios en pesos colombianos.
- **Ventas y auditoría:** sin registros iniciales.

Los usuarios semilla son de demostración. Para un entorno real se deben crear usuarios nuevos con contraseñas cifradas y eliminar los datos de ejemplo.

---

## 7. Consultas de negocio

### 7.1. Alertas de stock mínimo

```sql
SELECT r.id,
       r.codigo_referencia,
       r.nombre,
       r.stock_actual,
       r.stock_minimo,
       c.nombre AS categoria_nombre,
       CASE
           WHEN r.stock_actual = 0 THEN 'AGOTADO'
           ELSE 'STOCK_BAJO'
       END AS nivel_alerta
FROM repuestos r
JOIN categorias c ON r.categoria_id = c.id
WHERE r.activo = 1
  AND r.stock_actual <= r.stock_minimo
ORDER BY r.stock_actual ASC;
```

### 7.2. Kardex de un repuesto

```sql
SELECT id,
       tipo_movimiento,
       cantidad,
       stock_anterior,
       stock_nuevo,
       justificacion,
       created_at
FROM auditoria_movimientos
WHERE repuesto_id = ?
ORDER BY created_at ASC;
```

### 7.3. Detalle de una venta

```sql
SELECT v.id,
       v.numero_factura,
       v.subtotal,
       v.iva,
       v.total,
       v.estado,
       v.created_at,
       u.nombre AS vendedor
FROM ventas v
JOIN usuarios u ON v.usuario_id = u.id
WHERE v.id = ?;

SELECT d.repuesto_id,
       r.nombre,
       r.codigo_referencia,
       d.cantidad,
       d.precio_unitario,
       d.subtotal
FROM detalle_ventas d
JOIN repuestos r ON d.repuesto_id = r.id
WHERE d.venta_id = ?;
```

### 7.4. Ventas por periodo

```sql
SELECT DATE(created_at) AS fecha,
       COUNT(*) AS numero_ventas,
       SUM(total) AS total_vendido
FROM ventas
WHERE estado = 'COMPLETADA'
  AND created_at BETWEEN ? AND ?
GROUP BY DATE(created_at)
ORDER BY fecha;
```

---

## 8. Notas de diseño

1. **Dinero con `DECIMAL(12,2)`:** evita errores de redondeo de `FLOAT`.
2. **Borrado lógico:** `repuestos.activo` y `usuarios.activo` permiten desactivar sin perder historial.
3. **Precio histórico:** `detalle_ventas.precio_unitario` conserva el precio de venta original.
4. **Auditoría separada del saldo:** `repuestos.stock_actual` es el estado actual; `auditoria_movimientos` es la historia.
5. **Integridad en la base:** las llaves foráneas y los `CHECK` protegen los datos incluso si la aplicación falla.
6. **Transacciones:** InnoDB permite `COMMIT` y `ROLLBACK`; el servicio de ventas los usa para evitar ventas parciales.

---

## 9. Extensiones recomendadas para la entrega final

- Agregar `ENUM` o `CHECK` a `ventas.estado` y `auditoria_movimientos.tipo_movimiento`.
- Agregar un índice compuesto para búsquedas por `nombre`, `codigo_referencia` y `codigo_oem`.
- Registrar el motivo de anulación en `ventas.notas` o en una columna específica.
- Agregar una tabla de compras/proveedores si se implementa RF-08.
- Agregar una tabla de usuarios o auditoría de accesos si se implementa administración de usuarios.
- Evaluar `ON DELETE RESTRICT` explícito en las relaciones que no deben borrarse.

---

**AllQuality — Ingeniería de Software II — COTECNOVA 2026-2**
