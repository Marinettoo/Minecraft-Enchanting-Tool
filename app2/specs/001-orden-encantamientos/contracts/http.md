# Contrato HTTP de App 2

Base: apartado 8 de [contrato-api.md](../../../../docs/contrato-api.md) y [ERS-APP2.md](../../../../docs/ERS-APP2.md). Este documento concreta la interfaz que implementaremos en App 2.

## Petición

`POST /api/procesar`

Encabezados: `Content-Type: application/json` y `Authorization: Bearer <token de sesión>`.

```json
{
  "objeto": "diamond_sword",
  "encantamientos": [
    {"nombre": "sharpness", "nivel": 5}
  ]
}
```

Solo se aceptan esos campos. Las opciones, materiales, máximos y compatibilidades son los del anexo A de la ERS. Se exige de 1 a 8 encantamientos distintos y niveles enteros estrictos. No hay texto libre.

El backend verifica el acceso antes de leer y validar la selección. Una petición sin sesión válida devuelve 401; una selección incorrecta con sesión válida devuelve 422. Ninguno de esos casos consulta a IA.

## Respuesta correcta

Código 200, con esta estructura. Los números del ejemplo son ilustrativos.

```json
{
  "resultado": {
    "pasos": [
      {
        "orden": 1,
        "izquierda": "Espada de diamante",
        "derecha": "Libro de Filo V",
        "coste_niveles": 5
      }
    ],
    "coste_total_niveles": 5,
    "advertencias": [
      "Costes estimados por IA: no se ha comprobado que sean exactos ni mínimos."
    ]
  }
}
```

Cada paso tiene un orden consecutivo, dos nombres comprensibles y un coste entero no negativo. El total es la suma de los costes. La respuesta no incluye el token ni los metadatos privados del proveedor.

La IA usa internamente `objeto`, `libro_N` y `paso_N`. El backend comprueba esas referencias antes de convertirlas en textos como «Resultado del paso 1». No exige que la IA invente nombres para los elementos intermedios.

Con N libros habrá N pasos y el último resultado contendrá el objeto y todos los libros. Un paso de 40 niveles o más añade el aviso de que es demasiado caro en supervivencia. La pantalla muestra los textos sin ejecutar HTML ni código.

## Errores

Todos los errores controlados tienen esta forma:

```json
{
  "error": {
    "codigo": "NO_AUTORIZADO",
    "mensaje": "Vuelve a iniciar sesión para realizar la consulta."
  }
}
```

| HTTP | Código | Situación | Consultas al proveedor |
| --- | --- | --- | --- |
| 401 | `NO_AUTORIZADO` | Falta el token, no es válido o no se puede verificar. | Cero. |
| 422 | `VALIDACION` | Datos incompletos, ilegibles, adicionales o no permitidos. | Cero. |
| 502 | `IA_NO_DISPONIBLE` | Fallo de conexión o rechazo del proveedor. | Una intentada. |
| 502 | `RESPUESTA_INVALIDA` | Contenido incompleto, ilegible o que incumple las reglas de la propuesta. | Una. |
| 504 | `IA_TIMEOUT` | Se supera el límite total de 60 segundos al proveedor. | Una intentada. |

No hay reintentos automáticos ni resultados parciales. Una respuesta de proveedor con terminación incompleta se rechaza aunque parezca contener JSON. Los errores de validación de FastAPI se adaptarán al mismo formato, sin devolver valores privados ni el detalle completo de la petición.

Si el navegador no recibe una respuesta utilizable, presenta un aviso local de conexión o respuesta no disponible y termina la espera.

## Configuración entre entornos

- En local, frontend y backend usan orígenes distintos. El backend admite los orígenes configurados y los encabezados `Authorization` y `Content-Type`. La petición previa de CORS no procesa consultas y no sustituye la autenticación.
- En Vercel se configura la URL pública del backend en el frontend. Se mantiene la misma ruta y ambos usan HTTPS.
- En Docker, el navegador usa `/api/procesar` en el mismo origen. Caddy dirige la petición al backend interno conservando la ruta.
- No se añaden endpoints de cuentas, perfiles o historial. Si se necesita una comprobación técnica de salud, será `GET /health`, sin acceso al proveedor ni información privada.
