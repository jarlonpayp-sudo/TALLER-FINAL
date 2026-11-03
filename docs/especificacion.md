# Requisitos funcionales

# RF-01. Iniciar sesión
Descripción: El sistema debe permitir que los usuarios accedan mediante sus credenciales.
# Criterios de aceptación:
Si las credenciales son válidas, el sistema permite el acceso.
Si las credenciales son inválidas, el sistema rechaza el acceso.
El sistema no debe revelar información sensible cuando el inicio de sesión falla.

# RF-02. Crear producto
Descripción: El sistema debe permitir registrar nuevos productos.
# Criterios de aceptación:
Permite guardar un producto cuando sus campos obligatorios contienen datos válidos.
Rechaza el registro si faltan campos obligatorios.
Rechaza códigos o referencias duplicados.
Confirma el registro cuando los datos se guardan correctamente.

# RF-03. Consultar y buscar productos
Descripción: El sistema debe permitir consultar productos por nombre, código o referencia y categoría.
# Criterios de aceptación:
Permite buscar por nombre, código o referencia y categoría.
Muestra los productos que coinciden con los criterios de búsqueda.
Presenta información correcta del producto encontrado.
Si no existen coincidencias, informa que no se encontraron resultados.

# RF-04. Editar o desactivar producto
Descripción: El sistema debe permitir modificar la información de un producto o desactivarlo.
# Criterios de aceptación:
Guarda los cambios cuando la información es válida.
Rechaza modificaciones con datos inválidos.
Impide realizar operaciones para las que el usuario no tenga autorización.
Evita dejar la información del producto en un estado inconsistente.

# RF-05. Registrar venta
Descripción: El sistema debe permitir registrar ventas con uno o varios productos.
# Criterios de aceptación:
Permite seleccionar productos y especificar cantidades válidas.
Calcula el total según las cantidades y los precios registrados.
Guarda la venta y el detalle de los productos vendidos.
No confirma la venta si los datos son inválidos o la operación no puede completarse.

# RF-06. Actualizar inventario por venta
Descripción: El sistema debe descontar del inventario las unidades correspondientes a una venta confirmada.
# Criterios de aceptación:
Descuenta las unidades vendidas cuando la venta se confirma.
Actualiza las existencias de los productos involucrados.
Cada venta confirmada aplica el descuento correspondiente una sola vez.
La información de la venta y del inventario debe permanecer consistente.

# RF-07. Validar existencias
Descripción: El sistema debe verificar que las cantidades solicitadas en una venta estén disponibles.
# Criterios de aceptación:
Comprueba las existencias antes de confirmar la venta.
Impide vender cantidades superiores al inventario disponible cuando las reglas del negocio lo prohíban.
No permite que una operación inválida genere existencias negativas.
Informa cuando no hay suficiente inventario para completar la operación.

# RF-08. Registrar compra
Descripción: El sistema debe permitir registrar compras de productos y sus cantidades.
# Criterios de aceptación:
Permite registrar una compra con productos y cantidades válidas.
Rechaza los datos obligatorios que estén vacíos o sean inválidos.
Guarda la información de la compra correctamente.
El registro de la compra por sí solo no debe incorporar cantidades que todavía no hayan sido recibidas y confirmadas.

# RF-09. Confirmar recepción
Descripción: El sistema debe permitir confirmar la recepción de la mercancía comprada.
# Criterios de aceptación:
Permite confirmar las cantidades efectivamente recibidas.
Actualiza el inventario únicamente por las unidades recibidas y confirmadas.
Conserva información consistente entre la compra y la recepción.
No incorpora cantidades no recibidas o no confirmadas.

# RF-10. Anular venta autorizada
Descripción: El sistema debe permitir anular una venta cuando el usuario tenga autorización para hacerlo.
# Criterios de aceptación:
Solo permite realizar la anulación a usuarios autorizados.
Registra la anulación realizada.
Ajusta el inventario de acuerdo con las reglas definidas para la anulación.
Evita aplicar dos veces el mismo ajuste de inventario.

# RF-11. Consultar alertas de inventario bajo
Descripción: El sistema debe mostrar los productos cuyas existencias alcancen el mínimo configurado.
# Criterios de aceptación:
Compara las existencias con el mínimo configurado para cada producto.
Identifica los productos que alcanzan dicho mínimo.
Muestra las alertas correspondientes a los productos identificados.
Actualiza la información de las alertas cuando cambian las existencias.

# RF-12. Administrar usuarios y roles
Descripción: El sistema debe permitir gestionar las cuentas de usuario y sus roles.
# Criterios de aceptación:
Permite gestionar usuarios y roles únicamente a usuarios autorizados.
Permite asignar los roles definidos para el sistema.
Conserva la relación entre cada usuario y los permisos de su rol.
Impide que usuarios no autorizados administren cuentas o permisos.

# RF-13. Aplicar permisos por rol
Descripción: El sistema debe restringir las operaciones según el rol del usuario autenticado.
# Criterios de aceptación:
Verifica que el usuario tenga permiso para realizar la operación solicitada.
Bloquea las operaciones que no correspondan al rol asignado.
Las restricciones se verifican en el servidor para las operaciones protegidas.
Un usuario sin autorización no puede completar una operación restringida.

# RF-14. Crear copia de seguridad
Descripción: El sistema debe permitir generar una copia de seguridad de la base de datos mediante el mecanismo definido para el proyecto.
# Criterios de aceptación:
Permite ejecutar el procedimiento de respaldo definido.
Informa si el proceso termina correctamente o presenta un error.
La copia generada puede identificarse y utilizarse en una prueba de restauración.

# RF-15. Restaurar datos
Descripción: El sistema debe permitir recuperar una copia de seguridad en un entorno controlado.
# Criterios de aceptación:
Permite ejecutar el procedimiento de restauración definido.
Verifica que los datos recuperados sean consistentes.
Registra el resultado de la restauración y el tiempo empleado.
Los errores durante el proceso deben informarse sin declarar una recuperación exitosa si esta no se completó.

# RF-16. Generar reportes
Descripción: El sistema debe permitir consultar reportes de ventas por periodo y movimientos de inventario.
# Criterios de aceptación:
Permite consultar las ventas correspondientes a un periodo seleccionado.
Presenta los movimientos de inventario registrados.
Los datos del reporte coinciden con las transacciones que lo originan.
Los totales y las cantidades presentadas son consistentes con los registros del sistema.

# RF-17. Calcular totales
Descripción: El sistema debe calcular correctamente los valores de las ventas a partir de las cantidades y los precios de los productos.
# Criterios de aceptación:
Calcula los subtotales según las cantidades y los precios registrados.
Obtiene el total de la venta a partir de sus productos y de las reglas de negocio acordadas.
Aplica las reglas de redondeo definidas para el proyecto.
Los totales calculados coinciden con una verificación independiente de los mismos datos.

# RF-18. Registrar historial de operaciones
Descripción: El sistema debe conservar el historial de las operaciones relevantes.
# Criterios de aceptación:
Registra el usuario responsable cuando corresponda.
Registra la fecha, la acción realizada y el registro afectado cuando corresponda.
Permite conservar evidencia de operaciones relevantes, como ventas, compras, anulaciones y cambios autorizados.
La información registrada permite identificar qué operación se realizó y sobre qué registro.

# Requisitos NO Funcionales

# RNF-01. Rendimiento
Descripción: El sistema debe responder en tiempos adecuados al consultar información y registrar ventas.
# Criterios de aceptación:
Medir el tiempo de respuesta de las consultas bajo una carga de prueba definida.
Medir el tiempo requerido para registrar ventas bajo condiciones de prueba documentadas.
Utilizar como metas iniciales propuestas un tiempo de hasta 2 segundos para consultas y hasta 3 segundos para registrar ventas.
Confirmar las metas con el equipo y el entorno de ejecución antes de declarar su cumplimiento.
Registrar los tiempos y resultados obtenidos durante las pruebas.

# RNF-02. Seguridad
Descripción: El sistema debe proteger el acceso a las funciones y los datos según los permisos de cada usuario.
# Criterios de aceptación:
Verificar los permisos en el servidor para cada operación protegida.
Rechazar las operaciones realizadas por usuarios sin autorización.
Proteger las credenciales y evitar revelar información sensible en los mensajes de error.
Ejecutar pruebas de acceso no autorizado y registrar sus resultados.
Aprobar las pruebas críticas de autorización antes de declarar que se cumple este requisito.

# RNF-03. Usabilidad
Descripción: El sistema debe facilitar que los usuarios realicen las tareas correspondientes a sus funciones.
# Criterios de aceptación:
Probar tareas representativas con usuarios o participantes definidos para la evaluación.
Registrar si las tareas se completan correctamente.
Medir y documentar el tiempo requerido para completar las tareas.
Registrar los errores cometidos y la necesidad de ayuda.
Utilizar los resultados para identificar oportunidades de mejora en la interfaz y los procesos.

# RNF-04. Fiabilidad y recuperación
Descripción: El sistema debe conservar la consistencia de la información y permitir recuperar los datos mediante el procedimiento de respaldo definido.
# Criterios de aceptación:
Realizar una restauración controlada de una copia de seguridad.
Verificar que los registros recuperados sean consistentes.
Documentar el tiempo requerido para la recuperación.
Definir y documentar los objetivos aceptables de tiempo de recuperación y pérdida de datos.
Registrar los resultados y los errores encontrados durante las pruebas.

# RNF-05. Compatibilidad
Descripción: El sistema debe funcionar en los navegadores, versiones y entornos que el equipo declare como compatibles.
# Criterios de aceptación:
Documentar los navegadores y sus versiones que forman parte del alcance.
Documentar las versiones y los entornos de los componentes utilizados.
Ejecutar pruebas en los entornos seleccionados.
Registrar los resultados y los problemas de compatibilidad encontrados.
No declarar compatibilidad con entornos que no hayan sido definidos o probados.

# RNF-06. Mantenibilidad
Descripción: El sistema debe permitir realizar cambios controlados sin afectar las funciones existentes que son críticas para el negocio.
# Criterios de aceptación:
Ejecutar pruebas de regresión después de cambios controlados.
Repetir las pruebas de las funciones críticas relacionadas con el cambio.
Registrar los defectos nuevos que aparezcan.
Verificar que los cambios no alteren incorrectamente las operaciones de ventas e inventario.

# RNF-07. Portabilidad
Descripción: El sistema debe poder instalarse o ejecutarse en los entornos alternativos que el equipo defina como parte de su alcance.
# Criterios de aceptación:
Documentar el entorno principal de ejecución y sus requisitos.
Definir un segundo entorno para verificar la portabilidad, si esta es una meta del proyecto.
Intentar instalar o ejecutar el sistema en el entorno alternativo definido.
Registrar los ajustes necesarios y los resultados obtenidos.
No declarar portabilidad a otros entornos sin evidencia de las pruebas correspondientes.

# RNF-08. Integridad de datos
Descripción: El sistema debe mantener la consistencia de la información entre las ventas, las compras, las anulaciones y el inventario.
# Criterios de aceptación:
Verificar que las ventas confirmadas descuenten las existencias una sola vez.
Verificar que las compras aumenten el inventario únicamente por las cantidades recibidas y confirmadas.
Verificar que las anulaciones apliquen los ajustes correspondientes una sola vez.
Comprobar que las operaciones relacionadas mantengan datos consistentes.
Registrar los resultados de las pruebas de consistencia.

# RNF-09. Trazabilidad
Descripción: Los requisitos deben relacionarse con sus pruebas, resultados y evidencias.
# Criterios de aceptación:
Asignar un identificador único a cada requisito.
Relacionar los requisitos con los casos de prueba correspondientes.
Registrar el resultado real de cada prueba ejecutada.
Conservar evidencia de las pruebas, como capturas, registros o resultados automatizados.
Mantener identificados los requisitos y pruebas pendientes de ejecución.

# RNF-10. Manejo de errores
Descripción: El sistema debe validar las operaciones y comunicar los errores de forma comprensible.
# Criterios de aceptación:
Validar campos obligatorios, cantidades, precios y operaciones no permitidas.
Mostrar mensajes comprensibles cuando se detecten datos inválidos o errores.
No confirmar una operación que no se haya guardado correctamente.
Evitar que un error deje información inconsistente.
Registrar los errores relevantes para facilitar su revisión y corrección.
