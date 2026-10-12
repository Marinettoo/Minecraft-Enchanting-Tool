"""Listas estáticas del contrato; no son registros ni datos persistidos.

Alcance inicial: Java, objetos y libros nuevos (sin trabajos de yunque previos).
Revisar con el compañero antes de ampliar estas listas.
"""

TOOLS = {"sword", "axe", "pickaxe", "shovel", "hoe"}
ARMOR = {"helmet", "chestplate", "leggings", "boots"}
OBJECTS = {
    f"{material}_{kind}": kind
    for material in ("wooden", "stone", "iron", "golden", "diamond", "netherite")
    for kind in TOOLS
}
OBJECTS.update({
    f"{material}_{kind}": kind
    for material in ("leather", "chainmail", "iron", "golden", "diamond", "netherite")
    for kind in ARMOR
})
OBJECTS.update({kind: kind for kind in ("bow", "crossbow", "fishing_rod", "trident")})

ALL_TYPES = TOOLS | ARMOR | {"bow", "crossbow", "fishing_rod", "trident"}
# nombre: (nivel máximo, tipos de objeto admitidos)
ENCHANTMENTS = {
    "sharpness": (5, {"sword", "axe"}),
    "smite": (5, {"sword", "axe"}),
    "bane_of_arthropods": (5, {"sword", "axe"}),
    "knockback": (2, {"sword"}),
    "fire_aspect": (2, {"sword"}),
    "looting": (3, {"sword"}),
    "sweeping_edge": (3, {"sword"}),
    "unbreaking": (3, ALL_TYPES),
    "mending": (1, ALL_TYPES),
    "efficiency": (5, TOOLS - {"sword"}),
    "fortune": (3, TOOLS - {"sword"}),
    "silk_touch": (1, TOOLS - {"sword"}),
    "protection": (4, ARMOR),
    "thorns": (3, ARMOR),
    "feather_falling": (4, {"boots"}),
    "power": (5, {"bow"}),
    "infinity": (1, {"bow"}),
}
INCOMPATIBLE = (
    {"sharpness", "smite", "bane_of_arthropods"},
    {"silk_touch", "fortune"},
    {"infinity", "mending"},
    {"protection", "fire_protection", "blast_protection", "projectile_protection"},
)
