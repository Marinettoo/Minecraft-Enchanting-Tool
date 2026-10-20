# Especificación de App 2: orden de encantamientos

**Funcionalidad**: `001-orden-encantamientos`

**Fecha**: 20/10/2026

**Fase**: Especificación

**Petición**: Crear App 2 desde cero con Spec Kit, siguiendo la ERS y la constitución. Explicar el comportamiento con lenguaje claro y revisar cada fase antes de continuar.

**Base**: [ERS de App 2](../../../docs/ERS-APP2.md) y [constitución](../../.specify/memory/constitution.md). Conservamos los identificadores RF y RNF de la ERS para poder relacionar los documentos.

## Escenarios de uso y comprobación

### Historia 1. Consultar el orden de combinación (Prioridad: P1)

Como jugador, quiero acceder, elegir un objeto y sus encantamientos y ver cómo combinarlos en el yunque. Así puedo seguir los pasos y conocer el coste estimado.

**Por qué tiene esta prioridad**: Es la función principal de la aplicación.

**Comprobación por separado**: Hacer el recorrido completo con una sesión válida y una propuesta simulada. Comprobar el contenido de la pantalla y el número de consultas a IA. La comprobación con los servicios reales se hará por separado.

**Casos de aceptación**:

1. **Dado** un jugador sin sesión, **cuando** inicia sesión, **entonces** puede usar el formulario sin ir a otra pantalla.
2. **Dada** una sesión válida, **cuando** el jugador elige un objeto y entre 1 y 8 encantamientos compatibles, **entonces** puede enviar la consulta. Se comprobarán por separado los límites de 1 y 8 con los ejemplos del anexo B de la ERS.
3. **Dado** un envío válido y autorizado, **cuando** se procesa, **entonces** se hace una sola consulta a IA y se muestra la espera. Pulsar de nuevo mientras está pendiente no inicia otra petición.
4. **Dada** una propuesta válida con N libros, **cuando** termina la consulta, **entonces** se muestran N pasos, los elementos de cada combinación, su coste y el total en la misma pantalla. El total coincide con la suma de los pasos.
5. **Dado** un resultado, **cuando** se muestra, **entonces** los costes se identifican como estimados. Si un paso cuesta 40 niveles o más se avisa de que es demasiado caro en supervivencia; con 39 no se activa ese aviso.
6. **Dado** un resultado visible, **cuando** empieza otra consulta, **entonces** el resultado anterior se sustituye. Recargar o cerrar sesión retira la selección y el resultado, y no permite recuperarlos después.

### Historia 2. Corregir una selección o volver a acceder (Prioridad: P1)

Como jugador, quiero saber si falta algún dato, si la selección no está permitida o si mi sesión ya no es válida. Así puedo corregirlo antes de consultar a IA.

**Por qué tiene esta prioridad**: Evita procesar peticiones incorrectas o sin autorización.

**Comprobación por separado**: Probar el formulario y enviar peticiones directas con acceso y datos simulados. Contar que ningún rechazo consulta a IA.

**Casos de aceptación**:

1. **Dado** un formulario sin objeto o sin encantamientos, **cuando** se intenta enviar, **entonces** se explica qué falta y no se consulta a IA.
2. **Dada** una petición sin sesión válida, con credencial manipulada, de otro emisor o caducada, **cuando** llega al servicio, **entonces** se rechaza sin consultar a IA. Si no se puede verificar el acceso, tampoco se permite continuar.
3. **Dada** una sesión válida y una selección con 0 o 9 encantamientos, repetidos, niveles incorrectos o campos adicionales, **cuando** se envía, **entonces** se rechaza sin consultar a IA y se informa del error.
4. **Dados** Filo y Castigo juntos, o un encantamiento de botas para una espada, **cuando** se envían con sesión válida, **entonces** se rechazan sin consultar a IA.
5. **Dado** un jugador con sesión abierta, **cuando** la cierra, **entonces** se retiran los datos visibles y no puede volver a consultar hasta acceder otra vez.

### Historia 3. Entender un fallo y poder continuar (Prioridad: P1)

Como jugador, quiero recibir un mensaje si la consulta falla o si la IA devuelve pasos que no se pueden utilizar. Así puedo corregir la selección, volver a acceder o repetir la consulta manualmente.

**Por qué tiene esta prioridad**: Una consulta fallida debe terminar sin dejar el formulario bloqueado ni mostrar un resultado incorrecto.

**Comprobación por separado**: Simular los fallos de acceso, entrada, proveedor, respuesta y conexión. Comprobar el mensaje, el fin de la espera y la ausencia de reintentos automáticos.

**Casos de aceptación**:

1. **Dado** un fallo del proveedor, **cuando** termina la consulta, **entonces** se muestra un aviso y se permite otro intento manual. No se cambia de modelo ni se repite automáticamente.
2. **Dado** un proveedor que no responde dentro del límite de 60 segundos, **cuando** se agota ese plazo, **entonces** se informa del tiempo agotado y termina la espera. Este límite corresponde a la espera al proveedor, no al tiempo total del recorrido.
3. **Dada** una propuesta con libros omitidos, inventados o reutilizados, un paso usado antes de crearse, un coste negativo o una suma incorrecta, **cuando** se comprueba, **entonces** se rechaza completa sin mostrar pasos parciales ni hacer otra consulta a IA.
4. **Dada** una conexión interrumpida o una respuesta que no se puede leer, **cuando** falla la consulta, **entonces** se muestra un aviso y se permite continuar con otro intento manual.
5. **Dado** contenido con etiquetas HTML en una advertencia o en un mensaje, **cuando** se presenta en pantalla, **entonces** se muestra como texto y no se ejecuta.

### Casos límite

- Se aceptan niveles enteros desde 1 hasta el máximo del encantamiento. Se rechazan cero, negativos, decimales, texto, booleanos y valores superiores al máximo.
- Las opciones válidas son los 58 objetos y 39 encantamientos del anexo A de la ERS, con sus niveles y compatibilidades. Los nombres se muestran en español.
- Se rechaza una entrada ilegible, con campos obligatorios ausentes o con instrucciones en lugar de opciones admitidas.
- Cada combinación consume dos elementos distintos disponibles y crea uno nuevo. Un elemento consumido no se puede volver a utilizar.
- Se permiten libro con libro y objeto con libro. El objeto, o el resultado que lo contiene, va a la izquierda. El resultado final contiene el objeto y todos los libros elegidos.
- Una propuesta vacía, ilegible, con orden no consecutivo, costes que no sean enteros no negativos o con un número de pasos distinto al de libros se rechaza completa.
- Los textos largos se ajustan al ancho de la pantalla. Los errores se explican con texto y no solo con colores.

## Requisitos

### Requisitos funcionales

Todos son obligatorios. Las prioridades de las historias indican por dónde empezar, sin quitar requisitos de la entrega.

- **RF-01. Acceso**: Permitir iniciar y cerrar sesión en la misma pantalla o en un modal. Comprobar el acceso antes de procesar cualquier consulta, también las peticiones directas. Rechazar las sesiones ausentes, inválidas o caducadas sin llamar a IA. El cierre de sesión retira los datos funcionales visibles.
- **RF-02. Selección**: Ofrecer un formulario con un objeto y entre 1 y 8 encantamientos distintos, cada uno con su nivel. Usar las opciones, máximos e incompatibilidades del anexo A de la ERS. Mostrar nombres en español y avisar de los datos obligatorios que falten.
- **RF-03. Validación**: Comprobar la selección en el servicio que procesa la consulta, aunque no proceda del formulario. Rechazar opciones desconocidas, incompatibles, repetidas o fuera de rango, campos adicionales y tipos incorrectos. No convertir textos ni booleanos en niveles. Los rechazos no consultan a IA.
- **RF-04. Consulta a IA**: Solicitar una propuesta que busque reducir el gasto de niveles, con una sola llamada por envío autorizado y válido. No hacer reintentos automáticos, llamadas complementarias ni cambios automáticos de modelo. El orden y los costes los propone la IA.
- **RF-05. Comprobación del resultado**: Aceptar solo propuestas con estructura válida, pasos consecutivos, costes enteros no negativos y total igual a su suma. Comprobar que cada combinación utiliza elementos disponibles, que no se reutilizan y que el resultado final contiene el objeto y todos los libros. Con N libros debe haber N pasos. Rechazar la propuesta completa si falla alguna comprobación, sin recalcular los costes del juego ni pedir otra respuesta a IA.
- **RF-06. Presentación**: Mostrar espera, pasos, elementos combinados, coste por paso, total y advertencias en la misma pantalla. Indicar que los costes son estimados y avisar desde 40 niveles por paso. Tratar el contenido recibido como texto e impedir envíos duplicados mientras haya una petición pendiente. Una consulta nueva sustituye la anterior.
- **RF-07. Errores**: Explicar los fallos de acceso, selección, proveedor, respuesta, tiempo y conexión sin revelar información privada. Terminar la espera y permitir corregir datos, volver a acceder o repetir manualmente según el caso. Los códigos y campos se recogen en el contrato.

### Condiciones de uso y calidad

- **RNF-01. Espera**: Limitar a 60 segundos la espera al proveedor, sin reintentos. Comprobar el límite con una respuesta simulada que lo supere.
- **RNF-02. Protección**: Mantener las claves privadas fuera de la pantalla, los archivos públicos, las imágenes de despliegue, los mensajes y los registros. Usar conexión segura en los despliegues públicos y verificar la sesión antes de procesar. Los registros solo pueden contener estados y códigos técnicos.
- **RNF-03. Datos temporales**: No conservar selecciones ni respuestas en bases de datos, archivos, registros o almacenamiento del navegador. Tras una nueva consulta, recarga, cierre de sesión o reinicio no se recupera la consulta anterior. La sesión técnica solo se utiliza para autenticar.
- **RNF-04. Uso**: Permitir completar acceso, selección, envío y cierre con teclado en Chrome y Edge, a 360 y 1280 píxeles de ancho. Mantener controles utilizables, foco visible, etiquetas claras y textos ajustados al ancho.
- **RNF-05. Reproducción**: Documentar lo necesario para que otra persona instale y ejecute la aplicación con sus propias credenciales. Demostrar el mismo flujo en los entornos exigidos por la ERS, con pruebas habituales sin llamadas a servicios externos y comprobaciones reales separadas.

### Datos principales

Estos datos son temporales y no requieren una base de datos.

- **Selección**: Un objeto y una lista de encantamientos con nombre y nivel. Cada encantamiento representa un libro nuevo con un solo encantamiento.
- **Elemento disponible**: El objeto inicial, un libro inicial o el resultado de una combinación anterior. Tiene los encantamientos que contiene y se utiliza una sola vez.
- **Paso**: Su número, los dos elementos que se combinan y el coste estimado. Produce un elemento que puede usarse en un paso posterior.
- **Propuesta**: La lista de pasos, el coste total y las advertencias. Solo se muestra si supera todas las comprobaciones.
- **Error**: Un código y un mensaje comprensible que indican por qué no se ha podido completar la consulta.
- **Sesión**: Acredita que el jugador ha accedido. No se envía a la IA ni se utiliza como historial de consultas.

## Criterios de éxito

### Resultados que comprobaremos

Son objetivos de comprobación para el desarrollo, no resultados de pruebas ya realizadas.

- **SC-001**: Las selecciones válidas de 1 y 8 encantamientos del anexo B permiten completar el recorrido y ver todos los pasos, costes y advertencias en una sola pantalla. Cubre RF-02, RF-04, RF-05 y RF-06.
- **SC-002**: Todos los casos de acceso y selección rechazados de las historias 1 y 2 y de los casos límite terminan con un aviso y cero consultas a IA. Un envío válido y autorizado provoca exactamente una consulta. Cubre RF-01 a RF-04.
- **SC-003**: Todas las propuestas inválidas descritas en la historia 3 y los casos límite se rechazan completas. Las aceptadas tienen tantos pasos como libros, usan cada elemento una vez y suman sus costes correctamente. Cubre RF-05.
- **SC-004**: Las pruebas de 39 y 40 niveles distinguen correctamente el aviso de supervivencia. Todos los resultados indican que los costes son estimados. Cubre RF-06.
- **SC-005**: Cada fallo de la historia 3 produce un mensaje comprensible y termina la espera. El caso de tiempo agotado respeta el límite configurado de 60 segundos al proveedor y ninguno de los fallos provoca reintentos automáticos. Cubre RF-07 y RNF-01.
- **SC-006**: No se recupera ninguna selección o respuesta anterior al repetir las comprobaciones tras nueva consulta, recarga, cierre de sesión y reinicio. No aparecen secretos, tokens ni datos de consultas en los materiales públicos o registros revisados. Cubre RNF-02 y RNF-03.
- **SC-007**: Se completa el recorrido con teclado en las cuatro combinaciones de navegador y ancho: Chrome y Edge, a 360 y 1280 píxeles. No se pierden controles ni resultados y los textos largos se pueden leer. Cubre RNF-04.
- **SC-008**: Otra persona puede seguir las instrucciones con sus propias credenciales y completar una consulta válida y un caso de error en cada entorno exigido. Se anotan versión, fecha, entorno y resultado real de cada comprobación. Cubre RNF-05.

## Suposiciones y dependencias

- Trabajamos con Minecraft Java y solo con las opciones del anexo A. El objeto es nuevo y no tiene encantamientos ni trabajos previos de yunque. Los libros son nuevos y cada uno lleva el encantamiento al nivel solicitado.
- No se incluyen reparación, renombrado, aumento de niveles por combinación, libros con varios encantamientos iniciales ni Minecraft Bedrock.
- La aplicación ofrece una única función y una sola pantalla. No incorpora historial, perfiles propios, paneles, estadísticas, carga de archivos, chat ni almacenamiento de consultas.
- Las comprobaciones de estructura, referencias y sumas no demuestran que la propuesta sea la más barata posible ni que los costes coincidan con el juego.
- Se mantienen las decisiones técnicas ya recogidas en la ERS y la constitución. El diseño, las dependencias concretas y la organización del código se resolverán en el plan.
- El funcionamiento real depende de que el servicio de identidad y el proveedor de IA estén configurados y disponibles. Si falla el acceso no se desactiva la protección para continuar.
- Los datos iniciales y los resultados intermedios se identifican como explica el apartado de App 2 del contrato. La pantalla los presenta con nombres comprensibles.
- Se comprobarán el acceso y el formato del modelo antes de cerrar el plan, y el acceso en la única pantalla antes de implementar la integración de identidad. Las cuentas y recursos de despliegue se concretarán antes de publicar, según la ERS.
- La nueva implementación tendrá sus propios archivos en App 2. App 1 sirve como referencia de requisitos y funcionamiento, sin copiar su código.
