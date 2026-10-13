# Pruebas

## Automáticas (backend)
Están en `app1/backend/tests/test_backend.py` (pytest) y no usan red ni la IA real. Cubren:

- Petición válida: una sola llamada a la IA y respuesta con la forma del contrato.
- Entradas inválidas (objeto o encantamiento desconocido, nivel fuera de rango, incompatibles, lista vacía o con más de 8): 422 sin llamar a la IA.
- JSON mal formado.
- Límites: 1 y 7 encantamientos aceptados; 8 pasan la longitud pero fallan por incompatibilidad.
- Errores controlados del proveedor (`IA_NO_DISPONIBLE`, `IA_TIMEOUT`) con su código HTTP.
- Planes inválidos de la IA: `RESPUESTA_INVALIDA`.
- Combinaciones con libros permitidas.
- CORS.
- Transporte a OpenRouter simulado y modo `mock` / sin credenciales sin conexión.

Ejecutar (Python 3.12 o 3.13, desde `app1/backend`):

```bash
pip install -r requirements-dev.txt
pytest
```

## Manuales (frontend + backend + IA)
Con `AI_MODE=openrouter` en local, o en la web desplegada. Anotar el resultado de cada caso.

| Caso | Esperado | Resultado |
| --- | --- | --- |
| Arco con Poder V, Irrompibilidad III y Reparación | Pasos con costes razonados por la IA, sin errores | Pendiente de anotar |
| Pico de netherita con Eficiencia V, Fortuna III, Irrompibilidad III | Plan válido | Pendiente de anotar |
| Elegir un arco | El selector de material queda desactivado | Pendiente de anotar |
| Marcar dos encantamientos incompatibles (Filo y Castigo) | La interfaz lo impide | Pendiente de anotar |
| Pedir un plan con pasos de 40 o más niveles | Advertencia de 40 niveles o más (demasiado caro) | Pendiente de anotar |
| Backend apagado | Mensaje «No se puede conectar con el servidor» | Pendiente de anotar |
| Modelo gratuito saturado (429) o lento | Mensaje de error controlado, sin detalles técnicos | Pendiente de anotar |
