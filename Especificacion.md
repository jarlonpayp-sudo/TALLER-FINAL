Requisitos funcionales

**RF-01. Iniciar sesión
Descripción: El sistema debe permitir que los usuarios accedan mediante sus credenciales.

Criterios de aceptación:

Si las credenciales son válidas, el sistema permite el acceso.

Si las credenciales son inválidas, el sistema rechaza el acceso.

El sistema no debe revelar información sensible cuando el inicio de sesión falla.

RF-02. Crear producto

Descripción: El sistema debe permitir registrar nuevos productos.

Criterios de aceptación:

Permite guardar un producto cuando sus campos obligatorios contienen datos válidos.

Rechaza el registro si faltan campos obligatorios.

Rechaza códigos o referencias duplicados.

Confirma el registro cuando los datos se guardan correctamente.

RF-03. Consultar y buscar productos

Descripción: El sistema debe permitir consultar productos por nombre, código o referencia y categoría.

Criterios de aceptación:

Permite buscar por nombre, código o referencia y categoría.

Muestra los productos que coinciden con los criterios de búsqueda.

Presenta información correcta del producto encontrado.

Si no existen coincidencias, informa que no se encontraron resultados.

RF-04. Editar o desactivar producto

Descripción: El sistema debe permitir modificar la información de un producto o desactivarlo.

Criterios de aceptación:

Guarda los cambios cuando la información es válida.

Rechaza modificaciones con datos inválidos.

Impide realizar operaciones para las que el usuario no tenga autorización.

Evita dejar la información del producto en un estado inconsistente.

RF-05. Registrar venta

Descripción: El sistema debe permitir registrar ventas con uno o varios productos.

Criterios de aceptación:

Permite seleccionar productos y especificar cantidades válidas.

Calcula el total según las cantidades y los precios registrados.

Guarda la venta y el detalle de los productos vendidos.

No confirma la venta si los datos son inválidos o la operación no puede completarse.

RF-06. Actualizar inventario por venta

Descripción: El sistema debe descontar del inventario las unidades correspondientes a una venta confirmada.

Criterios de aceptación:

Descuenta las unidades vendidas cuando la venta se confirma.

Actualiza las existencias de los productos involucrados.

Cada venta confirmada aplica el descuento correspondiente una sola vez.

La información de la venta y del inventario debe permanecer consistente.

RF-07. Validar existencias

Descripción: El sistema debe verificar que las cantidades solicitadas en una venta estén disponibles.

Criterios de aceptación:

Comprueba las existencias antes de confirmar la venta.

Impide vender cantidades superiores al inventario disponible cuando las reglas del negocio lo prohíban.

No permite que una operación inválida genere existencias negativas.

Informa cuando no hay suficiente inventario para completar la operación.

RF-08. Registrar compra

Descripción: El sistema debe permitir registrar compras de productos y sus cantidades.

Criterios de aceptación:

Permite registrar una compra con productos y cantidades válidas.

Rechaza los datos obligatorios que estén vacíos o sean inválidos.

Guarda la información de la compra correctamente.

El registro de la compra por sí solo no debe incorporar cantidades que todavía no hayan sido recibidas y confirmadas.

RF-09. Confirmar recepción

Descripción: El sistema debe permitir confirmar la recepción de la mercancía comprada.

Criterios de aceptación:

Permite confirmar las cantidades efectivamente recibidas.

Actualiza el inventario únicamente por las unidades recibidas y confirmadas.

Conserva información consistente entre la compra y la recepción.

No incorpora cantidades no recibidas o no confirmadas.

RF-10. Anular venta autorizada

Descripción: El sistema debe permitir anular una venta cuando el usuario tenga autorización para hacerlo.

Criterios de aceptación:

Solo permite realizar la anulación a usuarios autorizados.

Registra la anulación realizada.

Ajusta el inventario de acuerdo con las reglas definidas para la anulación.

Evita aplicar dos veces el mismo ajuste de inventario.

RF-11. Consultar alertas de inventario bajo

Descripción: El sistema debe mostrar los productos cuyas existencias alcancen el mínimo configurado.

Criterios de aceptación:

Compara las existencias con el mínimo configurado para cada producto.

Identifica los productos que alcanzan dicho mínimo.

Muestra las alertas correspondientes a los productos identificados.

Actualiza la información de las alertas cuando cambian las existencias.

RF-12. Administrar usuarios y roles

Descripción: El sistema debe permitir gestionar las cuentas de usuario y sus roles.

Criterios de aceptación:

Permite gestionar usuarios y roles únicamente a usuarios autorizados.

Permite asignar los roles definidos para el sistema.

Conserva la relación entre cada usuario y los permisos de su rol.

Impide que usuarios no autorizados administren cuentas o permisos.

RF-13. Aplicar permisos por rol

Descripción: El sistema debe restringir las operaciones según el rol del usuario autenticado.

Criterios de aceptación:

Verifica que el usuario tenga permiso para realizar la operación solicitada.

Bloquea las operaciones que no correspondan al rol asignado.

Las restricciones se verifican en el servidor para las operaciones protegidas.

Un usuario sin autorización no puede completar una operación restringida.

RF-14. Crear copia de seguridad

Descripción: El sistema debe permitir generar una copia de seguridad de la base de datos mediante el mecanismo definido para el proyecto.

Criterios de aceptación:

Permite ejecutar el procedimiento de respaldo definido.

Informa si el proceso termina correctamente o presenta un error.

La copia generada puede identificarse y utilizarse en una prueba de restauración.

RF-15. Restaurar datos

Descripción: El sistema debe permitir recuperar una copia de seguridad en un entorno controlado.

Criterios de aceptación:

Permite ejecutar el procedimiento de restauración definido.

Verifica que los datos recuperados sean consistentes.

Registra el resultado de la restauración y el tiempo empleado.

Los errores durante el proceso deben informarse sin declarar una recuperación exitosa si esta no se completó.

RF-16. Generar reportes

Descripción: El sistema debe permitir consultar reportes de ventas por periodo y movimientos de inventario.

Criterios de aceptación:

Permite consultar las ventas correspondientes a un periodo seleccionado.

Presenta los movimientos de inventario registrados.

Los datos del reporte coinciden con las transacciones que lo originan.

Los totales y las cantidades presentadas son consistentes con los registros del sistema.

RF-17. Calcular totales

Descripción: El sistema debe calcular correctamente los valores de las ventas a partir de las cantidades y los precios de los productos.

Criterios de aceptación:

Calcula los subtotales según las cantidades y los precios registrados.

Obtiene el total de la venta a partir de sus productos y de las reglas de negocio acordadas.

Aplica las reglas de redondeo definidas para el proyecto.

Los totales calculados coinciden con una verificación independiente de los mismos datos.

RF-18. Registrar historial de operaciones

Descripción: El sistema debe conservar el historial de las operaciones relevantes.

Criterios de aceptación:

Registra el usuario responsable cuando corresponda.

Registra la fecha, la acción realizada y el registro afectado cuando corresponda.

Permite conservar evidencia de operaciones relevantes, como ventas, compras, anulaciones y cambios autorizados.

La información registrada permite identificar qué operación se realizó y sobre qué registro.
