# Especificación de Requisitos de Software

## Sistema de Gestión Comercial «AllQuality»
**Asignatura:** Ingeniería de Software II  
**Institución:** Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)  
**Periodo Académico:** 2026-2  
**Docente Titular:** Ing. Felipe Gutiérrez Isaza  
**Responsable de Documentación:** Santiago Calvo  
**Versión evaluada:** Entrega 2 — Aplicación web funcional (backend Flask + frontend React)

> El estado de implementación y la evidencia de cada requisito se documentan en [Verificación de requisitos — Entrega 2](verificacion-requisitos.md).

---

## 1. Alcance y Propósito del Sistema

El sistema **AllQuality** es una plataforma orientada a la administración comercial y control operativo de establecimientos de venta de repuestos y accesorios para motocicletas. Permite registrar y buscar repuestos por código y categoría, gestionar el inventario en bodega y mostrador, procesar ventas de mostrador con descuento atómico de existencias, prevenir la venta de productos agotados y generar reportes de auditoría.

---

## 2. Requisitos Funcionales (Priorización MoSCoW)

### RF-01. Autenticación y Control de Sesión
* **Prioridad:** Must Have  
* **Descripción:** El sistema debe permitir que los usuarios accedan mediante credenciales seguras y restringir el acceso según su rol asignado (`ADMIN`, `VENDEDOR`, `INVENTARIO`).
* **Criterios de Aceptación Tradicionales:**
  - Si las credenciales son válidas, el sistema permite el acceso y emite datos de sesión.
  - Si las credenciales son inválidas, el sistema rechaza el acceso con código HTTP 401.
  - El sistema no debe revelar si el error fue en el usuario o en la contraseña.

---

### RF-02. Crear y Administrar Repuestos en Catálogo
* **Prioridad:** Must Have  
* **Descripción:** El sistema debe permitir registrar nuevos repuestos y accesorios con sus atributos comerciales: código/referencia, código OEM, nombre, categoría, precio de compra, precio de venta, existencia y stock mínimo.
* **Criterios de Aceptación:**
  - Permite guardar un repuesto cuando sus campos obligatorios contienen datos válidos.
  - Rechaza el registro si faltan campos obligatorios (nombre, código, precio o stock).
  - Rechaza códigos o referencias duplicados con código HTTP 409 Conflict.
  - Rechaza precios $\le 0$ o existencias iniciales $< 0$ con código HTTP 422.

---

### RF-03. Consultar y Buscar Productos
* **Prioridad:** Must Have  
* **Descripción:** El sistema debe permitir consultar productos mediante filtros de texto por nombre, código de referencia y categoría.
* **Criterios de Aceptación:**
  - Permite buscar por coincidencias parciales en nombre o código exacto.
  - Filtra por categoría seleccionada.
  - Si no existen coincidencias, retorna una lista vacía con estado 200 sin producir errores de servidor.

---

### RF-04. Editar o Desactivar Repuesto
* **Prioridad:** Must Have  
* **Descripción:** Permite modificar los datos de un repuesto existente o marcarlo como inactivo para no mostrarlo en el mostrador de ventas sin romper la integridad referencial.
* **Criterios de Aceptación:**
  - Guarda los cambios cuando la información cumple las reglas de validación.
  - La desactivación fija el estado lógico (`activo = 0`), preservando los registros de ventas previas.

---

### RF-05. Registrar Venta (Punto de Venta)
* **Prioridad:** Must Have  
* **Descripción:** Permite seleccionar uno o varios repuestos, especificar cantidades, calcular subtotales y totalizar la venta.
* **Criterios de Aceptación:**
  - Permite agregar productos del catálogo con cantidades enteras positivas ($> 0$).
  - Calcula el subtotal multiplicando cantidad por precio unitario vigente.
  - No permite confirmar ventas con carrito vacío o datos inconsistentes.

---

### RF-06. Actualización Atómica de Inventario por Venta
* **Prioridad:** Must Have  
* **Descripción:** Al confirmar una venta, el sistema debe descontar de forma inmediata e irreversible las existencias físicas del inventario en base de datos.
* **Criterios de Aceptación:**
  - Descuenta las unidades vendidas exactamente una sola vez por transacción.
  - La actualización se realiza bajo una transacción ACID (si falla un ítem, ningún producto se descuenta).

---

### RF-07. Validación de Disponibilidad (Anti-Sobrevanta)
* **Prioridad:** Must Have  
* **Descripción:** El sistema debe comprobar que existan suficientes unidades físicas antes de autorizar cualquier venta.
* **Criterios de Aceptación:**
  - Comprueba las existencias en tiempo real.
  - Bloquea cualquier venta donde la cantidad solicitada sea mayor a la existencia actual ($Q > S$).
  - Impide que el inventario caiga en valores negativos (`stock < 0`).
  - Informa claramente al vendedor cuántas unidades quedan disponibles.

---

### RF-08. Registrar Compras a Proveedores
* **Prioridad:** Should Have  
* **Descripción:** Permite registrar compras comerciales a distribuidores de repuestos con sus cantidades y costos de adquisición.

### RF-09. Entrada y Confirmación de Mercancía
* **Prioridad:** Should Have  
* **Descripción:** Incrementa las existencias en bodega únicamente cuando la mercancía ha sido efectivamente recibida e inspeccionada.

### RF-10. Anulación Autorizada de Ventas
* **Prioridad:** Should Have  
* **Descripción:** Permite al Administrador anular una venta previa, reintegrando las cantidades exactas al stock y registrando la justificación.

### RF-11. Consultar Alertas de Stock Bajo
* **Prioridad:** Must Have  
* **Descripción:** Identifica y lista todos los repuestos cuyas existencias sean menores o iguales al stock mínimo configurado ($S \le \text{stock\_minimo}$).

### RF-12. Administrar Usuarios y Roles
* **Prioridad:** Must Have  
* **Descripción:** Permite al Administrador dar de alta colaboradores, modificar roles y suspender accesos.

### RF-13. Control de Permisos por Rol
* **Prioridad:** Must Have  
* **Descripción:** Restringe en el backend el acceso a operaciones según el rol del usuario autenticado.

### RF-14. Copias de Seguridad (Backup)
* **Prioridad:** Could Have  
* **Descripción:** Permite generar un volcado SQL de la base de datos para recuperación ante desastres.

### RF-15. Restauración de Datos
* **Prioridad:** Could Have  
* **Descripción:** Permite restaurar la base de datos a partir de una copia válida en un entorno de contingencia.

### RF-16. Reportes Comerciales
* **Prioridad:** Should Have  
* **Descripción:** Genera resúmenes de ventas por periodos y lista los productos de mayor rotación.

### RF-17. Cálculo Exacto de Totales y Moneda
* **Prioridad:** Must Have  
* **Descripción:** Emplea tipos de datos de precisión fija decimal para evitar desvíos por redondeo de coma flotante.

### RF-18. Historial de Auditoría
* **Prioridad:** Must Have  
* **Descripción:** Conserva registro con marca de tiempo, usuario y acción para cada venta, anulación y ajuste de inventario.

---

## 3. Criterios de Aceptación en Formato BDD (Gherkin: Dado - Cuando - Entonces)

Para los flujos críticos del sistema se especifican los siguientes escenarios formales de comportamiento:

### Escenario 1: Registro exitoso de un repuesto en el catálogo
```gherkin
Escenario: Registrar un nuevo repuesto con datos válidos
  Dado que el usuario autenticado tiene el rol de "ADMIN" o "INVENTARIO"
  Y el código de referencia "PAST-FR-FZ16" no existe en la base de datos
  Cuando envía una solicitud con nombre "Pastillas de Freno FZ16", precio 35000 y stock 10
  Entonces el sistema responde con código HTTP 201 Created
  Y el nuevo repuesto queda almacenado con stock disponible igual a 10
```

### Escenario 2: Rechazo de repuesto con código duplicado
```gherkin
Escenario: Intentar registrar un repuesto con código existente
  Dado que existe en el catálogo un repuesto con código "PAST-FR-FZ16"
  Cuando un usuario intenta registrar otro repuesto con el mismo código "PAST-FR-FZ16"
  Entonces el sistema rechaza la operación con código HTTP 409 Conflict
  Y muestra el mensaje "El código de referencia ya se encuentra registrado"
```

### Escenario 3: Rechazo de precio inválido (Análisis de Valores Límite)
```gherkin
Escenario: Registrar repuesto con precio en cero o negativo
  Dado que el usuario completa el formulario de registro
  Cuando ingresa un precio de venta menor o igual a 0.00
  Entonces el sistema responde con código HTTP 422 Unprocessable Entity
  Y no almacena el producto en la base de datos
```

### Escenario 4: Venta exitosa y descuento atómico de inventario
```gherkin
Escenario: Confirmar venta con existencias suficientes
  Dado que el repuesto "Bujía NGK CR8E" tiene un stock actual de 15 unidades
  Y el vendedor agrega 3 unidades al carrito de ventas
  Cuando confirma la transacción de venta
  Entonces el sistema registra la venta con el total correspondiente
  Y descuenta inmediatamente las 3 unidades dejando el stock en 12
  Y la operación queda registrada en la bitácora de auditoría
```

### Escenario 5: Bloqueo de venta por stock insuficiente (Anti-Sobrevanta)
```gherkin
Escenario: Intentar vender más unidades de las disponibles
  Dado que el repuesto "Kit de Arrastre Pulsar 200" tiene solo 2 unidades disponibles
  Cuando el vendedor intenta registrar una venta solicitando 5 unidades
  Entonces el sistema bloquea la confirmación con código HTTP 400 Bad Request
  Y muestra la alerta "Stock insuficiente: solo quedan 2 unidades disponibles"
  Y el inventario permanece inalterado en 2 unidades
```

### Escenario 6: Disparo automático de alerta de stock bajo
```gherkin
Escenario: El inventario alcanza el umbral mínimo configurado
  Dado que el repuesto "Aceite Motul 7100 10W40" tiene configurado un stock mínimo de 5 unidades
  Y su saldo de existencias actual es de 5 unidades
  Cuando se consulta el módulo de inventario o alertas
  Entonces el sistema marca el producto con alerta visual de stock bajo
  Y lo incluye en el listado de productos prioritarios para reposición
```

---

## 4. Requisitos No Funcionales (RNF)

* **RNF-01. Rendimiento:** El percentil 95 ($p95$) de las consultas de catálogo debe responder en $\le 1.5$ segundos bajo condiciones de prueba.
* **RNF-02. Seguridad:** Hashing de contraseñas con sal mediante algoritmos criptográficos seguros; verificación de roles en el servidor para rutas protegidas.
* **RNF-03. Usabilidad:** Interfaz en React con flujo de venta de mostrador en $\le 4$ clics y validación visual inmediata.
* **RNF-04. Fiabilidad y Transaccionalidad:** Consistencia ACID en ventas; cero sobreventas o inventarios negativos bajo concurrencia.
* **RNF-05. Compatibilidad:** Funcionamiento en navegadores modernos (Google Chrome, Firefox, Microsoft Edge) y resolución responsiva POS.
* **RNF-06. Mantenibilidad:** Arquitectura desacoplada en capas (Flask REST API + React Vite) con suite de pruebas automatizadas en `pytest`.
* **RNF-07. Simplicidad de Despliegue:** Ejecutable de forma 100% nativa y local con Python 3.12 y MySQL (XAMPP/Laragon) sin requerir Docker.
* **RNF-08. Integridad de Datos:** Restricciones a nivel de esquema en base de datos (`CHECK stock >= 0`, `CHECK precio > 0`).

---

**Aprobado por:**  
**Santiago Calvo**  
*Responsable de Documentación*  
*Ingeniería de Software II — COTECNOVA 2026-2*
