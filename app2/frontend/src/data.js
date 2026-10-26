const tools = ['sword', 'axe', 'pickaxe', 'shovel', 'hoe']
const armor = ['helmet', 'chestplate', 'leggings', 'boots']
const materials = {
  wooden: 'madera', stone: 'piedra', iron: 'hierro', golden: 'oro',
  diamond: 'diamante', netherite: 'netherita', leather: 'cuero', chainmail: 'cota de malla',
}
const types = {
  sword: 'Espada', axe: 'Hacha', pickaxe: 'Pico', shovel: 'Pala', hoe: 'Azada',
  helmet: 'Casco', chestplate: 'Pechera', leggings: 'Grebas', boots: 'Botas',
  bow: 'Arco', crossbow: 'Ballesta', fishing_rod: 'Caña de pescar', trident: 'Tridente',
}

export const objectTypes = types
export const materialNames = materials

function materialObjects(materialNames, objectTypes) {
  return materialNames.flatMap(material => objectTypes.map(type => ({
    id: `${material}_${type}`, type, name: `${types[type]} de ${materials[material]}`,
  })))
}

export const objects = [
  ...materialObjects(['wooden', 'stone', 'iron', 'golden', 'diamond', 'netherite'], tools),
  ...materialObjects(['leather', 'chainmail', 'iron', 'golden', 'diamond', 'netherite'], armor),
  ...['bow', 'crossbow', 'fishing_rod', 'trident'].map(type => ({ id: type, type, name: types[type] })),
]

const all = Object.keys(types)
const mining = ['axe', 'pickaxe', 'shovel', 'hoe']
const weapons = ['sword', 'axe']
export const enchantments = [
  ['sharpness', 'Filo', 5, weapons],
  ['smite', 'Castigo', 5, weapons],
  ['bane_of_arthropods', 'Perdición de los artrópodos', 5, weapons],
  ['knockback', 'Empuje', 2, ['sword']],
  ['fire_aspect', 'Aspecto ígneo', 2, ['sword']],
  ['looting', 'Botín', 3, ['sword']],
  ['sweeping_edge', 'Filo barredor', 3, ['sword']],
  ['efficiency', 'Eficiencia', 5, mining],
  ['fortune', 'Fortuna', 3, mining],
  ['silk_touch', 'Toque de seda', 1, mining],
  ['protection', 'Protección', 4, armor],
  ['fire_protection', 'Protección contra el fuego', 4, armor],
  ['blast_protection', 'Protección contra explosiones', 4, armor],
  ['projectile_protection', 'Protección contra proyectiles', 4, armor],
  ['thorns', 'Espinas', 3, armor],
  ['respiration', 'Respiración', 3, ['helmet']],
  ['aqua_affinity', 'Afinidad acuática', 1, ['helmet']],
  ['feather_falling', 'Caída de pluma', 4, ['boots']],
  ['depth_strider', 'Agilidad acuática', 3, ['boots']],
  ['frost_walker', 'Paso helado', 2, ['boots']],
  ['soul_speed', 'Velocidad del alma', 3, ['boots']],
  ['swift_sneak', 'Sigilo veloz', 3, ['leggings']],
  ['power', 'Poder', 5, ['bow']],
  ['punch', 'Retroceso', 2, ['bow']],
  ['flame', 'Fuego', 1, ['bow']],
  ['infinity', 'Infinidad', 1, ['bow']],
  ['multishot', 'Multidisparo', 1, ['crossbow']],
  ['piercing', 'Perforación', 4, ['crossbow']],
  ['quick_charge', 'Carga rápida', 3, ['crossbow']],
  ['loyalty', 'Lealtad', 3, ['trident']],
  ['riptide', 'Propulsión acuática', 3, ['trident']],
  ['channeling', 'Canalización', 1, ['trident']],
  ['impaling', 'Empalamiento', 5, ['trident']],
  ['luck_of_the_sea', 'Suerte marina', 3, ['fishing_rod']],
  ['lure', 'Atracción', 3, ['fishing_rod']],
  ['unbreaking', 'Irrompibilidad', 3, all],
  ['mending', 'Reparación', 1, all],
  ['binding_curse', 'Maldición de ligamiento', 1, armor],
  ['vanishing_curse', 'Maldición de desaparición', 1, all],
].map(([id, name, max, types]) => ({ id, name, max, types }))

export const incompatible = [
  ['sharpness', 'smite', 'bane_of_arthropods'], ['fortune', 'silk_touch'], ['infinity', 'mending'],
  ['protection', 'fire_protection', 'blast_protection', 'projectile_protection'],
  ['depth_strider', 'frost_walker'], ['multishot', 'piercing'],
  ['riptide', 'loyalty'], ['riptide', 'channeling'],
]
