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
| Tiempo máximo de espera a la IA | 20 segundos (a ajustar tras probar) |
| Texto libre | Ninguno: todo se elige de listas |

Objetos permitidos (propuesta inicial, se puede ampliar): espada, hacha, pico, pala, azada, casco, pechera, grebas, botas, arco, ballesta, caña de pescar, tridente. En el código se escriben en inglés con el material (por ejemplo `diamond_sword`, `netherite_helmet`).

Encantamientos y nivel máximo (Java; propuesta inicial, contrastadla con la wiki de Minecraft antes de fijarla):

| Nombre en el código | Nivel máximo |
| --- | --- |
| sharpness | 5 |
| smite | 5 |
| bane\_of\_arthropods | 5 |
| knockback | 2 |
| fire\_aspect | 2 |
| looting | 3 |
| sweeping\_edge | 3 |
| unbreaking | 3 |
| mending | 1 |
| efficiency | 5 |
| fortune | 3 |
| silk\_touch | 1 |
| protection | 4 |
| thorns | 3 |
| feather\_falling | 4 |
| power | 5 |
| infinity | 1 |

Incompatibles que el backend debe rechazar con 422: Filo con Castigo con Perdición de los artrópodos; Toque de seda con Fortuna; Infinidad con Reparación; y los distintos tipos de Protección entre sí.

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

Idea para comentar con el profesor: como la IA puede calcular mal los niveles, el backend podría recalcular el coste del orden que devuelva y rechazar la respuesta si no cuadra (error RESPUESTA\_INVALIDA). Sigue siendo una sola llamada a la IA.

## 7. Decisiones pendientes

| Decisión | Propuesta | Quién la cierra |
| --- | --- | --- |
| Edición de Minecraft | Java (se asume en este documento) | Los dos |
| Proveedor y modelo de IA | OpenRouter con un modelo gratuito (nombre exacto por decidir). Sin Dify: FastAPI llama directamente a OpenRouter | Los dos |
| Vue o React | Vue | Los dos |
| Tiempo máximo de espera | 20 segundos | Backend |
| Lista exacta de objetos y encantamientos | La de la sección 5 | Los dos |
| Recalcular el coste en el backend | Preguntar al profesor | Los dos |
| Créditos y cuentas de la IA | Preguntar al profesor | Los dos |
