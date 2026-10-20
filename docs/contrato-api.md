# Contrato de la API: MeT (Minecraft Enchanting Tool)

Oct 8, 2026 · @Jesús

Este documento fija cómo se hablan el formulario (frontend) y FastAPI (backend). Con él, cada uno trabaja en su parte y las dos encajan al juntarlas. Lo que ponga aquí manda: si algo cambia, se cambia primero aquí y se avisa al compañero.

## 1. Qué hace la app

Un jugador de Minecraft elige un objeto (por ejemplo, una espada de diamante) y los encantamientos que quiere; la app le devuelve el orden de combinación en el yunque que gasta menos niveles.

## 2. Lo que envía el formulario (petición)

Una sola ruta: `POST /api/procesar`, con los datos en JSON.

| Campo | Tipo | Obligatorio | Regla |
| --- | --- | --- | --- |
| objeto | texto | Sí | Uno de la lista cerrada de objetos (ver sección 5). |
| encantamientos | lista | Sí | Entre 1 y 8 elementos, sin repetir encantamiento. |
| encantamientos\[\].nombre | texto | Sí | Uno de la lista cerrada de encantamientos. |
| encantamientos\[\].nivel | número entero | Sí | Entre 1 y el nivel máximo de ese encantamiento. |

Ejemplo:

```json
{
  "objeto": "diamond_sword",
  "encantamientos": [
    {"nombre": "sharpness", "nivel": 5},
    {"nombre": "mending", "nivel": 1}
  ]
}
```

## 3. Lo que devuelve el backend si todo va bien (código 200)

| Campo | Significado |
| --- | --- |
| resultado.pasos | Lista ordenada de combinaciones en el yunque. Cada paso tiene `orden`, `izquierda`, `derecha` y `coste_niveles`. |
| resultado.coste\_total\_niveles | Suma de los costes de todos los pasos. |
| resultado.advertencias | Lista de textos (puede ir vacía), por ejemplo si algún paso supera el límite del juego. |

Ejemplo (los números son solo ilustrativos):

```json
{
  "resultado": {
    "pasos": [
      {"orden": 1, "izquierda": "Espada de diamante", "derecha": "Libro de Filo V", "coste_niveles": 5},
      {"orden": 2, "izquierda": "Espada de diamante (con Filo V)", "derecha": "Libro de Reparación", "coste_niveles": 3}
    ],
    "coste_total_niveles": 8,
    "advertencias": []
  }
}
```

El frontend muestra todo como texto normal, nunca como HTML.

## 4. Errores

Siempre tienen esta forma, sin detalles técnicos ni claves:

```json
{"error": {"codigo": "IA_NO_DISPONIBLE", "mensaje": "No se ha podido completar la petición. Inténtalo más tarde."}}
```

| Código HTTP | `codigo` interno | Cuándo ocurre | Llama a la IA |
| --- | --- | --- | --- |
| 422 | VALIDACION | Objeto o encantamiento desconocido; encantamiento que no se puede poner a ese objeto; dos encantamientos incompatibles (como Filo y Castigo); nivel fuera de rango; lista vacía o con más de 8 elementos. | No |
| 502 | IA\_NO\_DISPONIBLE | Falla el proveedor de IA. | Sí (falló) |
| 502 | RESPUESTA\_INVALIDA | La IA responde algo que no se puede usar, o el orden no es válido al comprobarlo. | Sí |
| 504 | IA\_TIMEOUT | La IA no responde dentro del tiempo límite. | Sí (sin respuesta) |
| 401 | NO\_AUTORIZADO | Solo App 2: falta el token de Clerk o no es válido. | No |

## 5. Límites y listas cerradas

Como el usuario no escribe texto libre sino que elige de listas, la validación es exacta y se evita que alguien meta instrucciones raras a la IA.

| Límite | Valor propuesto |
| --- | --- |
| Encantamientos por petición | De 1 a 8 |
| Repetir un encantamiento | No permitido |
| Nivel | De 1 al máximo del encantamiento (tabla de abajo) |
| Tiempo máximo de espera a la IA | 60 segundos (ajustado tras probar con modelos gratuitos) |
| Texto libre | Ninguno: todo se elige de listas |

Objetos permitidos (propuesta inicial, se puede ampliar): espada, hacha, pico, pala, azada, casco, pechera, grebas, botas, arco, ballesta, caña de pescar, tridente. En el código se escriben en inglés con el material (por ejemplo `diamond_sword`, `netherite_helmet`).

Encantamientos y nivel máximo (Java; qué objetos admite cada uno está en `rules.py` y en `data.js`; contrastadlo con la wiki de Minecraft antes de fijarlo):

| Nombre en el código | Nivel máximo |
| --- | --- |
| sharpness | 5 |
| smite | 5 |
| bane\_of\_arthropods | 5 |
| knockback | 2 |
| fire\_aspect | 2 |
| looting | 3 |
| sweeping\_edge | 3 |
| efficiency | 5 |
| fortune | 3 |
| silk\_touch | 1 |
| protection | 4 |
| fire\_protection | 4 |
| blast\_protection | 4 |
| projectile\_protection | 4 |
| thorns | 3 |
| respiration | 3 |
| aqua\_affinity | 1 |
| feather\_falling | 4 |
| depth\_strider | 3 |
| frost\_walker | 2 |
| soul\_speed | 3 |
| swift\_sneak | 3 |
| power | 5 |
| punch | 2 |
| flame | 1 |
| infinity | 1 |
| multishot | 1 |
| piercing | 4 |
| quick\_charge | 3 |
| loyalty | 3 |
| riptide | 3 |
| channeling | 1 |
| impaling | 5 |
| luck\_of\_the\_sea | 3 |
| lure | 3 |
| unbreaking | 3 |
| mending | 1 |
| binding\_curse | 1 |
| vanishing\_curse | 1 |

Incompatibles que el backend debe rechazar con 422: Filo, Castigo y Perdición de los artrópodos entre sí; Toque de seda con Fortuna; Infinidad con Reparación; los cuatro tipos de Protección entre sí; Agilidad acuática con Paso helado; Multidisparo con Perforación; Propulsión acuática con Lealtad y con Conductividad.

## 6. Reglas del flujo y reparto de trabajo

Estas reglas vienen del enunciado y valen para las dos partes:

- Cada petición válida provoca **una sola** llamada a la IA.
- La clave de la IA vive solo en el backend, nunca en el frontend.
- Si la petición es inválida, el backend responde 422 **sin llamar** a la IA.
- No se guarda nada: ni resultados, ni historial, ni base de datos.
- El frontend muestra el resultado y los errores en la misma pantalla, sin acumular resultados anteriores.

Para trabajar en paralelo:

- **Backend:** debe devolver exactamente lo que dicen las secciones 3 y 4. Probádmoslo primero con ejemplos fijos.
- **Frontend:** mientras el backend no esté listo, se construye contra una respuesta falsa con la forma de la sección 3 y otra con la forma de la sección 4.
- **Cambios:** cualquier cambio de campos o códigos se anota aquí y se avisa al compañero antes de tocar código.

Decisión tomada: el orden y los costes los calcula **exclusivamente la IA**. El backend no recalcula ni corrige el resultado; solo comprueba que tiene la estructura del contrato, que las referencias entre pasos son coherentes y que la suma de costes cuadra (si no, responde RESPUESTA\_INVALIDA). Para que la IA acierte, el prompt incluye las reglas de coste del yunque; ver `docs/uso-ia.md`.

## 7. Decisiones pendientes

| Decisión | Propuesta | Quién la cierra |
| --- | --- | --- |
| Edición de Minecraft | Java (se asume en este documento) | Los dos |
| Proveedor y modelo de IA | OpenRouter con `poolside/laguna-s-2.1:free` (cerrada). Sin Dify: FastAPI llama directamente a OpenRouter | Los dos |
| Vue o React | Vue (cerrada) | Los dos |
| Tiempo máximo de espera | 60 segundos (cerrada) | Backend |
| Lista exacta de objetos y encantamientos | La de la sección 5 | Los dos |
| Recalcular el coste en el backend | No: lo calcula solo la IA (cerrada) | Los dos |
| Créditos y cuentas de la IA | Preguntar al profesor | Los dos |

## 8. Condiciones de App 2

Para App 2 se mantiene la forma de petición y respuesta de este contrato, con las siguientes condiciones de su ERS y constitución. Este apartado concreta lo que debe cumplir la nueva implementación.

### Acceso y entrada

- La ruta es `POST /api/procesar`. El token de sesión de Clerk se envía en `Authorization: Bearer ...`, fuera del cuerpo de la petición.
- Antes de validar la selección se comprueban firma, emisor, caducidad y las condiciones de audiencia u origen que correspondan. Si no se puede verificar la sesión, se responde 401 con `NO_AUTORIZADO`, sin consultar a IA.
- Las listas cerradas son los 58 objetos y 39 encantamientos del anexo A de [ERS-APP2.md](ERS-APP2.md), con sus niveles, materiales y compatibilidades. Las opciones del formulario y las del backend deben coincidir.
- Solo se admiten `objeto` y `encantamientos`, con `nombre` y `nivel` en cada elemento. Se rechazan campos adicionales, datos ausentes, JSON incorrecto, opciones desconocidas, duplicados e incompatibilidades. Los niveles deben ser enteros: no se admiten decimales, booleanos ni textos convertidos a números.
- El objeto y los libros son nuevos, sin trabajos anteriores de yunque. Cada libro lleva un encantamiento al nivel solicitado.

### Identificación y comprobación de los pasos

La respuesta solicitada a la IA utiliza estas referencias en `izquierda` y `derecha`:

| Referencia | Qué representa |
| --- | --- |
| `objeto` | El objeto inicial. |
| `libro_1`, `libro_2`, etc. | Los libros, en el mismo orden que los encantamientos de la petición. |
| `paso_1`, `paso_2`, etc. | El resultado de una combinación anterior. |

Cada paso consume dos elementos distintos que estén disponibles y produce uno nuevo. No se puede reutilizar un elemento consumido ni usar un paso antes de crearlo. Se permiten libro con libro y objeto con libro; el objeto o el resultado que lo contiene va siempre a la izquierda. Con N libros debe haber N pasos consecutivos desde 1. Al terminar debe quedar un único resultado con el objeto y todos los encantamientos solicitados.

Por ejemplo, con dos libros se puede combinar `libro_1` con `libro_2` en el paso 1 y después `objeto` con `paso_1` en el paso 2. La comprobación sigue qué contiene cada resultado sin depender de cómo lo haya descrito la IA.

Tras validar las referencias, el backend las transforma en nombres comprensibles para la pantalla, manteniendo los campos de la sección 3. Un resultado intermedio se identifica como «Resultado del paso 1», por ejemplo. Esta comprobación no recalcula ni corrige los costes del juego.

Los costes por paso y el total deben ser enteros no negativos. El total debe coincidir con la suma. Una propuesta vacía, ilegible, incompleta o incoherente se rechaza entera con 502 y `RESPUESTA_INVALIDA`, sin una segunda consulta a IA.

### Advertencias y errores

- Todo resultado debe indicar que sus costes son estimados y que no se ha comprobado que sean exactos ni mínimos.
- Si algún paso alcanza 40 niveles o más, se añade la advertencia de que es demasiado caro en supervivencia. No se activa este aviso con 39 niveles.
- La espera al proveedor se limita a 60 segundos. Al agotarse se responde 504 con `IA_TIMEOUT`.
- Un fallo del proveedor produce 502 con `IA_NO_DISPONIBLE`. Una selección incorrecta produce 422 con `VALIDACION`.
- Los errores mantienen la forma `error.codigo` y `error.mensaje` de la sección 4, sin secretos ni detalles privados.
- Solo se realiza una llamada por envío autorizado y válido a `poolside/laguna-s-2.1:free`. No hay reintentos automáticos ni cambios automáticos de modelo.
- Los despliegues públicos utilizan HTTPS. El token de sesión no se envía a la IA. Las claves privadas no se incluyen en los datos, las instrucciones ni el resultado de la consulta.
