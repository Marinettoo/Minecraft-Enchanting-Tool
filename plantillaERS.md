# Especificación de Requisitos del Software (ERS)

## Datos del documento

| Campo | Valor |
|---|---|
| Nombre del proyecto | [Nombre del sistema] |
| Autores | [Nombre y apellidos de los integrantes] |
| Curso y grupo | [Curso y grupo] |
| Asignatura o módulo | [Nombre] |
| Docente | [Nombre] |
| Fecha | [DD/MM/AAAA] |
| Versión | [1.0] |
| Estado | [Borrador / En revisión / Aprobado] |

### Historial de cambios

| Versión | Fecha | Autor | Cambios realizados |
|---|---|---|---|
| 0.1 | [Fecha] | [Autor] | Primera versión del documento. |

## Instrucciones para completar la plantilla

- Sustituye los textos entre corchetes por la información de tu proyecto.
- Describe **qué debe hacer el sistema** y las condiciones que debe cumplir. Evita detallar su implementación, salvo que exista una restricción obligatoria.
- Asigna un identificador único a cada requisito y mantenlo aunque cambie su descripción.
- Redacta una sola obligación por requisito, con un lenguaje claro y comprobable. Evita expresiones como «rápido», «fácil» o «seguro» sin definir cómo se comprobarán.
- Duplica las fichas y filas que necesites. Si una sección no corresponde a tu proyecto, indica «No aplica» y explica el motivo.
- Marca como «Pendiente» la información que todavía no se haya acordado; no presentes las suposiciones como hechos confirmados.
- Elimina estas instrucciones y los ejemplos antes de entregar la versión final.

## 1. Introducción

### 1.1. Propósito del documento

[Explica para qué sirve esta ERS y quiénes la utilizarán: equipo de desarrollo, cliente, usuarios, docente, etc.]

### 1.2. Problema y objetivos

**Problema o necesidad:** [Describe la situación actual y la necesidad que se pretende resolver.]

| ID | Objetivo del proyecto | Indicador de logro |
|---|---|---|
| OBJ-01 | [Resultado que se quiere conseguir] | [Cómo se comprobará que se ha conseguido] |

### 1.3. Alcance

**El sistema incluirá:**

- [Funcionalidad o proceso incluido.]

**Queda fuera del alcance:**

- [Funcionalidad o proceso que no se abordará en esta versión.]

### 1.4. Definiciones y abreviaturas

| Término | Definición |
|---|---|
| ERS | Especificación de Requisitos del Software. |
| [Término del proyecto] | [Significado compartido por el equipo y los usuarios] |

### 1.5. Referencias y fuentes

| ID | Fuente | Fecha o versión | Ubicación |
|---|---|---|---|
| FUE-01 | [Enunciado, entrevista, documento, reunión, etc.] | [Fecha o versión] | [Enlace o ruta, si existe] |

## 2. Descripción general del sistema

### 2.1. Contexto y perspectiva del producto

[Explica si es un sistema nuevo o una ampliación, dónde se utilizará y con qué otros sistemas se relaciona. Puedes añadir un diagrama de contexto.]

### 2.2. Personas interesadas y tipos de usuario

| ID | Persona, colectivo o rol | Necesidad o responsabilidad | Permisos y conocimientos relevantes |
|---|---|---|---|
| ACT-01 | [Usuario, administrador, cliente, etc.] | [Qué necesita o qué decide] | [Acciones permitidas y conocimientos previos] |

### 2.3. Funciones principales

[Resume las capacidades principales del sistema. Los requisitos detallados se documentan en la sección 3.]

- [Función principal 1.]
- [Función principal 2.]

### 2.4. Entorno de uso

| Aspecto | Descripción |
|---|---|
| Dispositivos y plataformas | [Ordenadores, móviles, sistemas operativos o navegadores previstos] |
| Condiciones de uso | [Lugar, conectividad, frecuencia de uso, etc.] |
| Volumen esperado | [Usuarios simultáneos, registros u operaciones previstas] |

### 2.5. Restricciones

[Indica las limitaciones impuestas por el proyecto. Distingue las obligaciones de las preferencias del equipo.]

| ID | Restricción | Origen o justificación |
|---|---|---|
| RES-01 | [Tecnología obligatoria, equipo disponible, plazo, presupuesto, etc.] | [Quién la impone y por qué] |

### 2.6. Suposiciones y dependencias

| ID | Tipo | Descripción | Consecuencia si no se cumple |
|---|---|---|---|
| SUP-01 | Suposición | [Condición que se asume y debe confirmarse] | [Impacto] |
| DEP-01 | Dependencia | [Servicio, recurso o sistema externo necesario] | [Impacto] |

## 3. Requisitos funcionales

Los requisitos funcionales describen las acciones y comportamientos que debe ofrecer el sistema.

**Prioridades:** Alta = imprescindible para la versión prevista; Media = importante, pero puede aplazarse mediante acuerdo; Baja = deseable.

### 3.1. Catálogo de requisitos funcionales

| ID | Nombre | Prioridad | Fuente | Estado |
|---|---|---|---|---|
| RF-01 | [Nombre breve] | [Alta / Media / Baja] | [FUE-01 o rol que lo solicita] | [Propuesto / Validado / Pendiente] |

### 3.2. Ficha de requisito funcional

> Duplica esta ficha para cada requisito del catálogo.

#### RF-01. [Nombre del requisito]

| Campo | Descripción |
|---|---|
| Enunciado | El sistema deberá [acción observable sobre un objeto, indicando las condiciones relevantes]. |
| Justificación | [Necesidad que satisface] |
| Actor | [Rol o sistema que inicia o recibe la acción] |
| Prioridad | [Alta / Media / Baja] |
| Fuente | [Referencia a la fuente] |
| Precondiciones | [Qué debe cumplirse antes de ejecutar la acción] |
| Entradas | [Datos necesarios y sus condiciones de validez] |
| Comportamiento esperado | [Qué debe hacer el sistema] |
| Salidas y postcondiciones | [Resultado observable y estado final] |
| Errores o alternativas | [Qué debe ocurrir ante entradas incorrectas o situaciones excepcionales] |
| Dependencias | [IDs de requisitos o reglas relacionados, o «Ninguna»] |

**Criterios de aceptación:**

- **CA-RF01-01:** Dado [estado inicial], cuando [acción o evento], entonces [resultado concreto y verificable].
- **CA-RF01-02:** Dado [situación de error o caso límite], cuando [acción o evento], entonces [respuesta esperada].

**Ejemplo orientativo — eliminar al completar:**

> El sistema deberá permitir que el usuario registrado cancele una reserva propia que todavía no haya comenzado.
>
> Dado un usuario identificado con una reserva propia futura, cuando confirme su cancelación, entonces la reserva aparecerá como cancelada y la plaza quedará disponible.
>
> Dado un usuario identificado con una reserva ya iniciada, cuando solicite cancelarla, entonces el sistema rechazará la cancelación, mostrará el motivo y mantendrá la reserva sin cambios.

## 4. Requisitos no funcionales

Describen propiedades de calidad y condiciones de funcionamiento. Incluye únicamente las categorías relevantes y define una comprobación objetiva para cada requisito.

| ID | Categoría | Requisito medible | Condiciones de comprobación | Criterio de aceptación | Prioridad |
|---|---|---|---|---|---|
| RNF-01 | Rendimiento | [Tiempo máximo de respuesta o capacidad requerida] | [Carga, datos y entorno] | [Umbral que debe alcanzarse] | [Prioridad] |
| RNF-02 | Seguridad y privacidad | [Acceso, permisos o protección de datos exigida] | [Roles y escenario de prueba] | [Resultado verificable] | [Prioridad] |
| RNF-03 | Usabilidad y accesibilidad | [Tarea o interacción que debe facilitarse] | [Perfil de usuario y condiciones] | [Medida o comprobación concreta] | [Prioridad] |
| RNF-04 | Fiabilidad y recuperación | [Comportamiento ante fallos y recuperación] | [Fallo simulado] | [Resultado y plazo admitidos] | [Prioridad] |
| RNF-05 | Compatibilidad | [Plataformas o formatos requeridos] | [Versiones y entorno acordados] | [Funciones que deben superar la prueba] | [Prioridad] |

**Ejemplo orientativo — eliminar al completar:**

> RNF-01: El sistema deberá mostrar los resultados de búsqueda en un máximo de 2 segundos para al menos el 95 % de 100 búsquedas de prueba, con 20 usuarios simultáneos y 10 000 registros, en el entorno de pruebas acordado y descrito en la sección 2.4.

## 5. Datos y reglas de negocio

### 5.1. Información que gestionará el sistema

| ID | Entidad o conjunto de datos | Campos principales | Validaciones | Acceso y conservación |
|---|---|---|---|---|
| DAT-01 | [Usuario, producto, reserva, etc.] | [Campos y tipos de datos] | [Obligatoriedad, unicidad, rangos y relaciones] | [Quién puede consultar o modificar; cuándo se elimina] |

### 5.2. Reglas de negocio

Las reglas de negocio expresan condiciones del ámbito del problema que el sistema debe respetar.

| ID | Regla | Requisitos relacionados | Fuente |
|---|---|---|---|
| RN-01 | [Ejemplo: un usuario no puede tener más de tres reservas activas a la vez.] | [RF-01, etc.] | [Fuente de la regla] |

## 6. Interfaces externas

### 6.1. Interfaz de usuario

| ID | Pantalla o interacción | Usuarios | Información y acciones necesarias | Requisitos relacionados |
|---|---|---|---|---|
| IU-01 | [Nombre] | [Roles] | [Datos visibles, entradas, acciones y mensajes] | [RF / RNF] |

[Añade enlaces o imágenes de bocetos si ayudan a aclarar los requisitos. Indica si son orientativos o vinculantes.]

### 6.2. Interfaces con otros sistemas o dispositivos

| ID | Sistema o dispositivo externo | Información intercambiada | Dirección y momento del intercambio | Formato o protocolo exigido | Respuesta ante fallos |
|---|---|---|---|---|---|
| INT-01 | [Nombre] | [Datos enviados o recibidos] | [Entrada / Salida / Ambas; cuándo] | [Formato acordado o «Pendiente»] | [Comportamiento esperado] |

## 7. Casos de uso o escenarios de usuario

Los escenarios muestran cómo se combinan los requisitos para realizar una tarea. Referencia sus identificadores para evitar duplicar especificaciones.

### CU-01. [Nombre del caso de uso]

| Campo | Descripción |
|---|---|
| Objetivo | [Qué quiere conseguir el actor] |
| Actor principal | [Rol] |
| Precondiciones | [Estado necesario antes de empezar] |
| Evento de inicio | [Qué desencadena el escenario] |
| Requisitos relacionados | [RF-01, RNF-01, RN-01, etc.] |

**Flujo principal:**

1. [El actor realiza una acción.]
2. [El sistema responde.]
3. [El actor o el sistema completa la tarea.]

**Flujos alternativos y excepciones:**

- **A1 — [Nombre]:** En el paso [n], si [condición], el sistema [respuesta] y el flujo [continúa en el paso… / termina].

**Postcondiciones:** [Estado final cuando se completa la tarea y cuando falla, si corresponde.]

## 8. Verificación y trazabilidad

Relaciona cada requisito con su origen y con una prueba, inspección o demostración que permita comprobarlo. Añade tantas filas como necesites para cubrir todos los requisitos funcionales y no funcionales.

| Requisito | Objetivo o necesidad de origen | Criterio de aceptación | ID de prueba | Método y datos de comprobación | Resultado esperado |
|---|---|---|---|---|---|
| RF-01 | [OBJ-01 / FUE-01] | CA-RF01-01 | PR-01 | [Pasos y datos concretos] | [Resultado observable] |
| RNF-01 | [OBJ-01 / FUE-01] | [Criterio de la sección 4] | PR-02 | [Procedimiento y entorno] | [Umbral exigido] |

## 9. Cuestiones pendientes

| ID | Duda o decisión pendiente | Requisitos afectados | Responsable de resolverla | Fecha prevista | Resolución |
|---|---|---|---|---|---|
| PEN-01 | [Qué falta por aclarar] | [IDs] | [Persona o rol] | [Fecha] | [Pendiente / Decisión acordada y fecha] |

## 10. Revisión y conformidad

### 10.1. Lista de comprobación antes de entregar

- [ ] El problema, los objetivos y los límites del sistema están definidos.
- [ ] Se identifican los usuarios y sus permisos.
- [ ] Cada requisito tiene un identificador único.
- [ ] Los requisitos son claros, necesarios y no se contradicen.
- [ ] Cada requisito funcional expresa una obligación y tiene criterios de aceptación verificables.
- [ ] Se contemplan los errores y los casos límite relevantes.
- [ ] Los requisitos no funcionales incluyen medidas y condiciones de comprobación.
- [ ] Los datos, las reglas de negocio y las interfaces están descritos.
- [ ] Todos los requisitos están relacionados con su origen y su comprobación.
- [ ] Las dudas pendientes están identificadas y tienen un responsable.
- [ ] Se han sustituido los marcadores, eliminado los ejemplos y justificado los apartados que no aplican.
- [ ] Se han actualizado la fecha, la versión y el historial de cambios.

### 10.2. Registro de revisión

| Revisor y rol | Versión revisada | Fecha | Resultado | Observaciones |
|---|---|---|---|---|
| [Nombre y rol] | [Versión] | [Fecha] | [Conforme / Requiere cambios] | [Comentarios] |

## Anexos

[Incluye, si procede, diagramas, bocetos, ejemplos de datos, entrevistas u otro material que ayude a comprender los requisitos. Referencia cada anexo desde la sección correspondiente.]
