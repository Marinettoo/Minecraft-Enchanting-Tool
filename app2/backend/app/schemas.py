"""Tipos estrictos de entrada y salida del contrato."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.rules import ENCHANTMENTS, INCOMPATIBLE, OBJECTS


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class Enchantment(StrictModel):
    nombre: str
    nivel: Annotated[int, Field(ge=1)]


class ProcessRequest(StrictModel):
    objeto: str
    encantamientos: Annotated[list[Enchantment], Field(min_length=1, max_length=8)]

    @model_validator(mode="after")
    def validate_selection(self):
        kind = OBJECTS.get(self.objeto)
        if kind is None:
            raise ValueError("Objeto no permitido")
        names = [item.nombre for item in self.encantamientos]
        if len(names) != len(set(names)):
            raise ValueError("Encantamientos repetidos")
        for item in self.encantamientos:
            rule = ENCHANTMENTS.get(item.nombre)
            if rule is None or item.nivel > rule[0] or kind not in rule[1]:
                raise ValueError("Encantamiento o nivel no permitido para el objeto")
        if any(len(set(names) & group) > 1 for group in INCOMPATIBLE):
            raise ValueError("Encantamientos incompatibles")
        return self


class Step(StrictModel):
    orden: Annotated[int, Field(ge=1)]
    izquierda: Annotated[str, Field(min_length=1)]
    derecha: Annotated[str, Field(min_length=1)]
    coste_niveles: Annotated[int, Field(ge=0)]


class Result(StrictModel):
    pasos: Annotated[list[Step], Field(min_length=1, max_length=8)]
    coste_total_niveles: Annotated[int, Field(ge=0)]
    advertencias: list[str]


class ProcessResponse(StrictModel):
    resultado: Result
