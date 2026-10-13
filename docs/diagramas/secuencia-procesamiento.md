# Diagrama de secuencia del procesamiento de una solicitud

El diagrama representa el flujo de una solicitud en modo real, desde el envío del formulario hasta la presentación del resultado o del error en la misma pantalla.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant F as Frontend · Vue
    participant B as Backend · FastAPI
    participant IA as API de IA · OpenRouter

    U->>F: Seleccionar objeto, encantamientos y niveles
    U->>F: Enviar formulario
    F->>F: Comprobar campos obligatorios y número de encantamientos

    alt Formulario incompleto o fuera de límites
        F-->>U: Mostrar mensaje de validación
    else Formulario completo
        F->>F: Mostrar espera y bloquear nuevos envíos
        F->>F: Iniciar solicitud HTTP al backend

        alt No se puede establecer conexión con el backend
            F->>F: Detectar fallo y preparar mensaje de conexión

        else Conexión establecida
            F->>B: POST /api/procesar (JSON)
            Note over F: Espera la respuesta del backend
            B->>B: Validar esquema, niveles, duplicados y compatibilidad

            alt Entrada inválida
                B-->>F: 422 · VALIDACION

            else Entrada válida
                B->>B: Comprobar configuración del servicio de IA

                alt Configuración incompleta
                    B-->>F: 502 · IA_NO_DISPONIBLE

                else Configuración disponible
                    B->>B: Iniciar consulta a OpenRouter con plazo máximo

                    alt Se agota el plazo durante la conexión
                        B->>B: Detectar timeout y cancelar la consulta
                        B-->>F: 504 · IA_TIMEOUT

                    else Falla la conexión con OpenRouter
                        B->>B: Detectar fallo de comunicación
                        B-->>F: 502 · IA_NO_DISPONIBLE

                    else Conexión con OpenRouter establecida
                        B->>IA: Una solicitud HTTPS con credencial privada
                        Note over B: Espera la respuesta dentro del plazo restante

                        alt Se agota el plazo esperando la respuesta
                            B->>B: Detectar timeout y cancelar la espera
                            B-->>F: 504 · IA_TIMEOUT

                        else Falla la comunicación durante la consulta
                            B->>B: Detectar interrupción de la comunicación
                            B-->>F: 502 · IA_NO_DISPONIBLE

                        else El proveedor devuelve un error HTTP
                            IA-->>B: Error del proveedor, por ejemplo 429
                            B->>B: Transformar el error al contrato público
                            B-->>F: 502 · IA_NO_DISPONIBLE

                        else El proveedor devuelve una respuesta correcta
                            IA-->>B: Contenido generado
                            B->>B: Comprobar finalización y formato JSON
                            B->>B: Validar estructura, referencias, orden y suma

                            alt Respuesta o plan inválido
                                B-->>F: 502 · RESPUESTA_INVALIDA

                            else Plan válido
                                B->>B: Transformar referencias y añadir advertencias
                                B-->>F: 200 · Pasos, coste total y advertencias
                            end
                        end
                    end
                end
            end
        end

        alt Resultado recibido y utilizable
            F->>F: Preparar pasos, coste total y advertencias como texto
        else Error HTTP, de conexión o respuesta no utilizable
            F->>F: Preparar mensaje de error
        end

        F->>F: Finalizar espera y habilitar nuevos envíos
        F-->>U: Mostrar resultado o error en la misma pantalla
    end
```

Si la conexión entre frontend y backend se interrumpe después del envío, el frontend también lo trata como error de comunicación, aunque el backend haya recibido la solicitud. No se realizan reintentos automáticos.

La validación del plan comprueba su estructura y la suma de los costes; no garantiza su exactitud ni un coste mínimo.

[Ver la imagen exportada del diagrama](secuencia-procesamiento.png)