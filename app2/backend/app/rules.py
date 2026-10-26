"""Opciones y compatibilidades del anexo A de la ERS de App 2."""

TOOL_TYPES = {"sword", "axe", "pickaxe", "shovel", "hoe"}
ARMOR_TYPES = {"helmet", "chestplate", "leggings", "boots"}
OBJECTS = {
    f"{material}_{kind}": kind
    for material in ("wooden", "stone", "iron", "golden", "diamond", "netherite")
    for kind in TOOL_TYPES
} | {
    f"{material}_{kind}": kind
    for material in ("leather", "chainmail", "iron", "golden", "diamond", "netherite")
    for kind in ARMOR_TYPES
} | {kind: kind for kind in ("bow", "crossbow", "fishing_rod", "trident")}

ALL_TYPES = set(OBJECTS.values())
TOOLS = {"axe", "pickaxe", "shovel", "hoe"}
WEAPONS = {"sword", "axe"}

# Cada entrada indica el máximo y los tipos de objeto permitidos.
ENCHANTMENTS = {
    "sharpness": (5, WEAPONS), "smite": (5, WEAPONS), "bane_of_arthropods": (5, WEAPONS),
    "knockback": (2, {"sword"}), "fire_aspect": (2, {"sword"}),
    "looting": (3, {"sword"}), "sweeping_edge": (3, {"sword"}),
    "efficiency": (5, TOOLS), "fortune": (3, TOOLS), "silk_touch": (1, TOOLS),
    "protection": (4, ARMOR_TYPES), "fire_protection": (4, ARMOR_TYPES),
    "blast_protection": (4, ARMOR_TYPES), "projectile_protection": (4, ARMOR_TYPES),
    "thorns": (3, ARMOR_TYPES), "respiration": (3, {"helmet"}), "aqua_affinity": (1, {"helmet"}),
    "feather_falling": (4, {"boots"}), "depth_strider": (3, {"boots"}),
    "frost_walker": (2, {"boots"}), "soul_speed": (3, {"boots"}), "swift_sneak": (3, {"leggings"}),
    "power": (5, {"bow"}), "punch": (2, {"bow"}), "flame": (1, {"bow"}), "infinity": (1, {"bow"}),
    "multishot": (1, {"crossbow"}), "piercing": (4, {"crossbow"}), "quick_charge": (3, {"crossbow"}),
    "loyalty": (3, {"trident"}), "riptide": (3, {"trident"}),
    "channeling": (1, {"trident"}), "impaling": (5, {"trident"}),
    "luck_of_the_sea": (3, {"fishing_rod"}), "lure": (3, {"fishing_rod"}),
    "unbreaking": (3, ALL_TYPES), "mending": (1, ALL_TYPES),
    "binding_curse": (1, ARMOR_TYPES), "vanishing_curse": (1, ALL_TYPES),
}

INCOMPATIBLE = (
    {"sharpness", "smite", "bane_of_arthropods"}, {"fortune", "silk_touch"},
    {"infinity", "mending"},
    {"protection", "fire_protection", "blast_protection", "projectile_protection"},
    {"depth_strider", "frost_walker"}, {"multishot", "piercing"},
    {"riptide", "loyalty"}, {"riptide", "channeling"},
)

TYPE_NAMES = {
    "sword": "Espada", "axe": "Hacha", "pickaxe": "Pico", "shovel": "Pala", "hoe": "Azada",
    "helmet": "Casco", "chestplate": "Pechera", "leggings": "Grebas", "boots": "Botas",
    "bow": "Arco", "crossbow": "Ballesta", "fishing_rod": "Caña de pescar", "trident": "Tridente",
}
MATERIAL_NAMES = {
    "wooden": "madera", "stone": "piedra", "iron": "hierro", "golden": "oro",
    "diamond": "diamante", "netherite": "netherita", "leather": "cuero", "chainmail": "cota de malla",
}
OBJECT_NAMES = {
    name: TYPE_NAMES[kind] if name == kind else f"{TYPE_NAMES[kind]} de {MATERIAL_NAMES[name.split('_')[0]]}"
    for name, kind in OBJECTS.items()
}
ENCHANTMENT_NAMES = dict(zip(ENCHANTMENTS, (
    "Filo", "Castigo", "Perdición de los artrópodos", "Empuje", "Aspecto ígneo", "Botín", "Filo barredor",
    "Eficiencia", "Fortuna", "Toque de seda", "Protección", "Protección contra el fuego",
    "Protección contra explosiones", "Protección contra proyectiles", "Espinas", "Respiración",
    "Afinidad acuática", "Caída de pluma", "Agilidad acuática", "Paso helado", "Velocidad del alma",
    "Sigilo veloz", "Poder", "Retroceso", "Fuego", "Infinidad", "Multidisparo", "Perforación",
    "Carga rápida", "Lealtad", "Propulsión acuática", "Canalización", "Empalamiento", "Suerte marina",
    "Atracción", "Irrompibilidad", "Reparación", "Maldición de ligamiento", "Maldición de desaparición",
), strict=True))
