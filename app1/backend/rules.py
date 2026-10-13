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
    "efficiency": (5, TOOLS - {"sword"}),
    "fortune": (3, TOOLS - {"sword"}),
    "silk_touch": (1, TOOLS - {"sword"}),
    "protection": (4, ARMOR),
    "fire_protection": (4, ARMOR),
    "blast_protection": (4, ARMOR),
    "projectile_protection": (4, ARMOR),
    "thorns": (3, ARMOR),
    "respiration": (3, {"helmet"}),
    "aqua_affinity": (1, {"helmet"}),
    "feather_falling": (4, {"boots"}),
    "depth_strider": (3, {"boots"}),
    "frost_walker": (2, {"boots"}),
    "soul_speed": (3, {"boots"}),
    "swift_sneak": (3, {"leggings"}),
    "power": (5, {"bow"}),
    "punch": (2, {"bow"}),
    "flame": (1, {"bow"}),
    "infinity": (1, {"bow"}),
    "multishot": (1, {"crossbow"}),
    "piercing": (4, {"crossbow"}),
    "quick_charge": (3, {"crossbow"}),
    "loyalty": (3, {"trident"}),
    "riptide": (3, {"trident"}),
    "channeling": (1, {"trident"}),
    "impaling": (5, {"trident"}),
    "luck_of_the_sea": (3, {"fishing_rod"}),
    "lure": (3, {"fishing_rod"}),
    "unbreaking": (3, ALL_TYPES),
    "mending": (1, ALL_TYPES),
    "binding_curse": (1, ARMOR),
    "vanishing_curse": (1, ALL_TYPES),
}
INCOMPATIBLE = (
    {"sharpness", "smite", "bane_of_arthropods"},
    {"silk_touch", "fortune"},
    {"infinity", "mending"},
    {"protection", "fire_protection", "blast_protection", "projectile_protection"},
    {"depth_strider", "frost_walker"},
    {"multishot", "piercing"},
    {"riptide", "loyalty"},
    {"riptide", "channeling"},
)
