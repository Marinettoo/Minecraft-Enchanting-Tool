"""Validación del contrato público y del plan interno devuelto por la IA."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from rules import ENCHANTMENTS, INCOMPATIBLE, OBJECTS


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Enchantment(StrictModel):
    nombre: Annotated[str, Field(min_length=1, max_length=40)]
    nivel: Annotated[int, Field(ge=1, le=5)]


class ProcessRequest(StrictModel):
    objeto: Annotated[str, Field(min_length=1, max_length=40)]
    encantamientos: Annotated[list[Enchantment], Field(min_length=1, max_length=8)]

    @model_validator(mode="after")
    def check_rules(self):
        if self.objeto not in OBJECTS:
            raise ValueError("Objeto no permitido")
        names = [item.nombre for item in self.encantamientos]
        if len(names) != len(set(names)):
            raise ValueError("Encantamiento repetido")
        for item in self.encantamientos:
            rule = ENCHANTMENTS.get(item.nombre)
            if rule is None or item.nivel > rule[0] or OBJECTS[self.objeto] not in rule[1]:
                raise ValueError("Encantamiento o nivel no permitido para este objeto")
        if any(len(set(names) & group) > 1 for group in INCOMPATIBLE):
            raise ValueError("Encantamientos incompatibles")
        return self


class Step(StrictModel):
    orden: Annotated[int, Field(ge=1, le=8)]
    izquierda: Annotated[str, Field(min_length=1, max_length=500)]
    derecha: Annotated[str, Field(min_length=1, max_length=500)]
    coste_niveles: Annotated[int, Field(ge=0, le=1000)]


class Result(StrictModel):
    pasos: Annotated[list[Step], Field(min_length=1, max_length=8)]
    coste_total_niveles: Annotated[int, Field(ge=0, le=8000)]
    advertencias: Annotated[list[Annotated[str, Field(min_length=1, max_length=500)]], Field(max_length=12)]


class ProcessResponse(StrictModel):
    resultado: Result


class ErrorDetail(StrictModel):
    codigo: str
    mensaje: str


class ErrorResponse(StrictModel):
    error: ErrorDetail


def validate_plan(data: object, request: ProcessRequest) -> ProcessResponse:
    """Comprueba referencias consumibles, orden, integridad y suma; no optimalidad.

La IA utiliza objeto, libro_1... y paso_1... como referencias. Solo se
convierten a texto después de verificar que cada recurso se utiliza una vez.
"""
    response = ProcessResponse.model_validate(data)
    result = response.resultado
    if len(result.advertencias) > 10:
        raise ValueError("Demasiadas advertencias del proveedor")
    count = len(request.encantamientos)
    if len(result.pasos) != count:
        raise ValueError("Número de combinaciones incorrecto")
    available = {"objeto": (request.objeto, True)}
    for index, item in enumerate(request.encantamientos, 1):
        available[f"libro_{index}"] = (f"Libro de {item.nombre} {item.nivel}", False)
    for index, step in enumerate(result.pasos, 1):
        if step.orden != index or step.izquierda == step.derecha:
            raise ValueError("Orden inválido")
        if step.izquierda not in available or step.derecha not in available:
            raise ValueError("Referencia ausente o ya consumida")
        left_label, left_is_object = available.pop(step.izquierda)
        right_label, right_is_object = available.pop(step.derecha)
        if right_is_object:
            raise ValueError("El objeto debe ir a la izquierda")
        available[f"paso_{index}"] = (f"Resultado del paso {index}", left_is_object)
        step.izquierda, step.derecha = left_label, right_label
    if len(available) != 1 or not next(iter(available.values()))[1]:
        raise ValueError("Plan incompleto")
    if result.coste_total_niveles != sum(step.coste_niveles for step in result.pasos):
        raise ValueError("Suma incorrecta")
    if any(step.coste_niveles >= 40 for step in result.pasos):
        result.advertencias.append("Algún paso alcanza 40 niveles o más: demasiado caro en supervivencia.")
    result.advertencias.append("Costes estimados por IA: no se ha verificado que sean exactos ni mínimos.")
    return response
