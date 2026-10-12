// Listas cerradas del contrato (docs/contrato-api.md, sección 5).
// Deben coincidir con app1/backend/rules.py. Si cambian allí, cambian aquí.

const TIPOS = {
  sword: 'Espada', axe: 'Hacha', pickaxe: 'Pico', shovel: 'Pala', hoe: 'Azada',
  helmet: 'Casco', chestplate: 'Pechera', leggings: 'Grebas', boots: 'Botas',
}
const HERRAMIENTAS = ['sword', 'axe', 'pickaxe', 'shovel', 'hoe']
const ARMADURA = ['helmet', 'chestplate', 'leggings', 'boots']

const MAT_HERRAMIENTA = {
  wooden: 'madera', stone: 'piedra', iron: 'hierro', golden: 'oro', diamond: 'diamante', netherite: 'netherita',
}
const MAT_ARMADURA = {
  leather: 'cuero', chainmail: 'malla', iron: 'hierro', golden: 'oro', diamond: 'diamante', netherite: 'netherita',
}

// id -> { nombre, tipo }
export const OBJETOS = {}
for (const [mat, matNombre] of Object.entries(MAT_HERRAMIENTA)) {
  for (const t of HERRAMIENTAS) OBJETOS[`${mat}_${t}`] = { nombre: `${TIPOS[t]} de ${matNombre}`, tipo: t, material: mat }
}
for (const [mat, matNombre] of Object.entries(MAT_ARMADURA)) {
  for (const t of ARMADURA) OBJETOS[`${mat}_${t}`] = { nombre: `${TIPOS[t]} de ${matNombre}`, tipo: t, material: mat }
}
Object.assign(OBJETOS, {
  bow: { nombre: 'Arco', tipo: 'bow' },
  crossbow: { nombre: 'Ballesta', tipo: 'crossbow' },
  fishing_rod: { nombre: 'Caña de pescar', tipo: 'fishing_rod' },
  trident: { nombre: 'Tridente', tipo: 'trident' },
})

// Objetos que se eligen por tipo y material (el material depende del tipo).
const nombresMat = { ...MAT_HERRAMIENTA, ...MAT_ARMADURA }
const mats = (ids) => ids.map((id) => ({ id, nombre: nombresMat[id][0].toUpperCase() + nombresMat[id].slice(1) }))
export const TIPOS_OBJETO = [
  ...HERRAMIENTAS.map((id) => ({ id, nombre: TIPOS[id], materiales: mats(Object.keys(MAT_HERRAMIENTA)) })),
  ...ARMADURA.map((id) => ({ id, nombre: TIPOS[id], materiales: mats(Object.keys(MAT_ARMADURA)) })),
  // Sin material: el arco, la ballesta, la caña y el tridente no se hacen de materiales distintos
  { id: 'bow', nombre: 'Arco', materiales: [] },
  { id: 'crossbow', nombre: 'Ballesta', materiales: [] },
  { id: 'fishing_rod', nombre: 'Caña de pescar', materiales: [] },
  { id: 'trident', nombre: 'Tridente', materiales: [] },
]

const TODOS = [...HERRAMIENTAS, ...ARMADURA, 'bow', 'crossbow', 'fishing_rod', 'trident']
const SIN_ESPADA = HERRAMIENTAS.filter((t) => t !== 'sword')

// id -> { nombre, max, tipos }
export const ENCANTAMIENTOS = {
  sharpness: { nombre: 'Filo', max: 5, tipos: ['sword', 'axe'] },
  smite: { nombre: 'Castigo', max: 5, tipos: ['sword', 'axe'] },
  bane_of_arthropods: { nombre: 'Perdición de los artrópodos', max: 5, tipos: ['sword', 'axe'] },
  knockback: { nombre: 'Empuje', max: 2, tipos: ['sword'] },
  fire_aspect: { nombre: 'Aspecto ígneo', max: 2, tipos: ['sword'] },
  looting: { nombre: 'Botín', max: 3, tipos: ['sword'] },
  sweeping_edge: { nombre: 'Filo barredor', max: 3, tipos: ['sword'] },
  efficiency: { nombre: 'Eficiencia', max: 5, tipos: SIN_ESPADA },
  fortune: { nombre: 'Fortuna', max: 3, tipos: SIN_ESPADA },
  silk_touch: { nombre: 'Toque de seda', max: 1, tipos: SIN_ESPADA },
  protection: { nombre: 'Protección', max: 4, tipos: ARMADURA },
  fire_protection: { nombre: 'Protección contra el fuego', max: 4, tipos: ARMADURA },
  blast_protection: { nombre: 'Protección contra explosiones', max: 4, tipos: ARMADURA },
  projectile_protection: { nombre: 'Protección contra proyectiles', max: 4, tipos: ARMADURA },
  thorns: { nombre: 'Espinas', max: 3, tipos: ARMADURA },
  respiration: { nombre: 'Respiración', max: 3, tipos: ['helmet'] },
  aqua_affinity: { nombre: 'Afinidad acuática', max: 1, tipos: ['helmet'] },
  feather_falling: { nombre: 'Caída de pluma', max: 4, tipos: ['boots'] },
  depth_strider: { nombre: 'Agilidad acuática', max: 3, tipos: ['boots'] },
  frost_walker: { nombre: 'Paso helado', max: 2, tipos: ['boots'] },
  soul_speed: { nombre: 'Velocidad del alma', max: 3, tipos: ['boots'] },
  swift_sneak: { nombre: 'Sigilo veloz', max: 3, tipos: ['leggings'] },
  power: { nombre: 'Poder', max: 5, tipos: ['bow'] },
  punch: { nombre: 'Retroceso', max: 2, tipos: ['bow'] },
  flame: { nombre: 'Llama', max: 1, tipos: ['bow'] },
  infinity: { nombre: 'Infinidad', max: 1, tipos: ['bow'] },
  multishot: { nombre: 'Multidisparo', max: 1, tipos: ['crossbow'] },
  piercing: { nombre: 'Perforación', max: 4, tipos: ['crossbow'] },
  quick_charge: { nombre: 'Carga rápida', max: 3, tipos: ['crossbow'] },
  loyalty: { nombre: 'Lealtad', max: 3, tipos: ['trident'] },
  riptide: { nombre: 'Propulsión acuática', max: 3, tipos: ['trident'] },
  channeling: { nombre: 'Conductividad', max: 1, tipos: ['trident'] },
  impaling: { nombre: 'Empalamiento', max: 5, tipos: ['trident'] },
  luck_of_the_sea: { nombre: 'Suerte del mar', max: 3, tipos: ['fishing_rod'] },
  lure: { nombre: 'Atracción', max: 3, tipos: ['fishing_rod'] },
  unbreaking: { nombre: 'Irrompibilidad', max: 3, tipos: TODOS },
  mending: { nombre: 'Reparación', max: 1, tipos: TODOS },
  binding_curse: { nombre: 'Maldición de ligamiento', max: 1, tipos: ARMADURA },
  vanishing_curse: { nombre: 'Maldición de desaparición', max: 1, tipos: TODOS },
}

export const INCOMPATIBLES = [
  ['sharpness', 'smite', 'bane_of_arthropods'],
  ['silk_touch', 'fortune'],
  ['infinity', 'mending'],
  ['protection', 'fire_protection', 'blast_protection', 'projectile_protection'],
  ['depth_strider', 'frost_walker'],
  ['multishot', 'piercing'],
  ['riptide', 'loyalty'],
  ['riptide', 'channeling'],
]

export const MAX_ENCANTAMIENTOS = 8

// Forma y material del icono pixelado de un objeto (ver icons.js)
export function iconoObjeto(id) {
  const o = OBJETOS[id]
  return o ? { forma: o.tipo, material: o.material || 'neutro' } : null
}

const ROMANOS = ['', 'I', 'II', 'III', 'IV', 'V']
export const romano = (n) => ROMANOS[n] || String(n)

// Traduce las etiquetas que devuelve el backend ("diamond_sword",
// "Libro de sharpness 5") a texto legible. Lo demás se deja tal cual.
export function etiqueta(texto) {
  if (OBJETOS[texto]) return OBJETOS[texto].nombre
  const libro = /^Libro de (\S+) (\d+)$/.exec(texto)
  if (libro && ENCANTAMIENTOS[libro[1]]) return `Libro de ${ENCANTAMIENTOS[libro[1]].nombre} ${romano(Number(libro[2]))}`
  return texto
}
