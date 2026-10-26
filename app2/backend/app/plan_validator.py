"""Comprueba el uso de elementos y los costes recibidos, sin recalcular el yunque."""

from app.rules import ENCHANTMENT_NAMES, OBJECT_NAMES
from app.schemas import ProcessRequest, ProcessResponse


def validate_plan(raw: object, selection: ProcessRequest) -> ProcessResponse:
    response = ProcessResponse.model_validate(raw)
    result = response.resultado
    count = len(selection.encantamientos)
    if len(result.pasos) != count:
        raise ValueError("Número de pasos incorrecto")
    available = {"objeto": (OBJECT_NAMES[selection.objeto], True, frozenset())}
    for index, book in enumerate(selection.encantamientos, 1):
        level = ("I", "II", "III", "IV", "V")[book.nivel - 1]
        available[f"libro_{index}"] = (f"Libro de {ENCHANTMENT_NAMES[book.nombre]} {level}", False, frozenset({index}))
    for number, step in enumerate(result.pasos, 1):
        if step.orden != number or step.izquierda == step.derecha:
            raise ValueError("Orden o combinación incorrectos")
        if step.izquierda not in available or step.derecha not in available:
            raise ValueError("Elemento inexistente o ya utilizado")
        left = available.pop(step.izquierda)
        right = available.pop(step.derecha)
        if right[1]:
            raise ValueError("El objeto debe ir a la izquierda")
        available[f"paso_{number}"] = (f"Resultado del paso {number}", left[1], left[2] | right[2])
        step.izquierda, step.derecha = left[0], right[0]
    final = next(iter(available.values()))
    if len(available) != 1 or not final[1] or final[2] != frozenset(range(1, count + 1)):
        raise ValueError("La propuesta no utiliza todos los elementos")
    if result.coste_total_niveles != sum(step.coste_niveles for step in result.pasos):
        raise ValueError("El total no coincide con la suma")
    if any(step.coste_niveles >= 40 for step in result.pasos):
        result.advertencias.append("Algún paso alcanza 40 niveles o más: demasiado caro en supervivencia.")
    return response
