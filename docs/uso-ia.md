# Uso de IA

## 1. IA dentro de la aplicación

- **Proveedor y modelo:** OpenRouter, modelo gratuito `poolside/laguna-s-2.1:free`.
- **Quién calcula:** solo la IA. Recibe el objeto y los encantamientos con sus niveles y devuelve el orden de combinaciones en el yunque con el coste de cada paso. El servidor no recalcula ni corrige el resultado.
- **Una llamada por petición válida.** Si la petición es inválida, el backend responde 422 sin llamar a la IA. No hay reintentos.
- **Parámetros:** temperatura 0, sin streaming, razonamiento desactivado, sin proveedores alternativos y tiempo máximo de 60 s.
- **Prompt (`app1/backend/ai_client.py`):** explica las reglas de coste del yunque de Minecraft Java: coste de un paso = (2^n_izquierda − 1) + (2^n_derecha − 1) + suma de nivel × multiplicador del libro del objeto de la derecha; el resultado tiene n = máximo + 1 usos del yunque; un paso de 40 o más es «Demasiado caro». Incluye la tabla de multiplicadores por encantamiento, un ejemplo resuelto con un arco, el formato JSON de salida y la instrucción de usar solo `objeto`, `libro_N` y `paso_N` como referencias.
- **Validación del resultado:** el backend solo comprueba la estructura, las referencias entre pasos y que la suma de costes cuadre. Si no es válido, responde 502 `RESPUESTA_INVALIDA`.
- **Seguridad:** el usuario no escribe texto libre, solo elige de listas cerradas, así que no puede inyectar instrucciones en el prompt. La clave de OpenRouter vive solo en el backend.

### Modelos probados
| Modelo | Resultado |
| --- | --- |
| `google/gemma-4-31b-it:free` | Error 429 frecuente (límite del proveedor). |
| `nvidia/nemotron-3-super` (gratuito) | Tiempos de espera agotados. |
| Modelos con razonamiento | El razonamiento consumía la respuesta (`finish_reason: length`, contenido vacío). Se desactivó el razonamiento. |
| Modelos pequeños | Planes inválidos (reutilizaban `objeto` o inventaban nombres). Se reforzó el prompt. |
| `poolside/laguna-s-2.1:free` | El que mejor funciona; es el elegido. |

## 2. IA en el desarrollo

La interfaz, la integración con la API y buena parte del backend se han construido con ayuda de Claude (asistente de IA de Anthropic), a petición de los integrantes: código del formulario y de los iconos, lista de encantamientos, prompt de la IA, reparto en ramas y despliegue en Vercel.

El enunciado pide construcción progresiva y comprensión del código. Esta asistencia no sustituye ese trabajo: los integrantes deben revisar los módulos, entenderlos y poder explicarlos en la defensa.

## 3. Cosas por verificar
- Los multiplicadores de libro y los niveles máximos de los encantamientos más recientes se escribieron de memoria; hay que contrastarlos con la wiki de Minecraft.
