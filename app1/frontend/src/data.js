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
  for (const t of HERRAMIENTAS) OBJETOS[`${mat}_${t}`] = { nombre: `${TIPOS[t]} de ${matNombre}`, tipo: t }
}
for (const [mat, matNombre] of Object.entries(MAT_ARMADURA)) {
  for (const t of ARMADURA) OBJETOS[`${mat}_${t}`] = { nombre: `${TIPOS[t]} de ${matNombre}`, tipo: t }
}
Object.assign(OBJETOS, {
  bow: { nombre: 'Arco', tipo: 'bow' },
  crossbow: { nombre: 'Ballesta', tipo: 'crossbow' },
  fishing_rod: { nombre: 'Caña de pescar', tipo: 'fishing_rod' },
  trident: { nombre: 'Tridente', tipo: 'trident' },
})

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
  unbreaking: { nombre: 'Irrompibilidad', max: 3, tipos: TODOS },
  mending: { nombre: 'Reparación', max: 1, tipos: TODOS },
  efficiency: { nombre: 'Eficiencia', max: 5, tipos: SIN_ESPADA },
  fortune: { nombre: 'Fortuna', max: 3, tipos: SIN_ESPADA },
  silk_touch: { nombre: 'Toque de seda', max: 1, tipos: SIN_ESPADA },
  protection: { nombre: 'Protección', max: 4, tipos: ARMADURA },
  thorns: { nombre: 'Espinas', max: 3, tipos: ARMADURA },
  feather_falling: { nombre: 'Caída de pluma', max: 4, tipos: ['boots'] },
  power: { nombre: 'Poder', max: 5, tipos: ['bow'] },
  infinity: { nombre: 'Infinidad', max: 1, tipos: ['bow'] },
}

export const INCOMPATIBLES = [
  ['sharpness', 'smite', 'bane_of_arthropods'],
  ['silk_touch', 'fortune'],
  ['infinity', 'mending'],
]

export const MAX_ENCANTAMIENTOS = 8

// Traduce las etiquetas que devuelve el backend ("diamond_sword",
// "Libro de sharpness 5") a texto legible. Lo demás se deja tal cual.
export function etiqueta(texto) {
  if (OBJETOS[texto]) return OBJETOS[texto].nombre
  const libro = /^Libro de (\S+) (\d+)$/.exec(texto)
  if (libro && ENCANTAMIENTOS[libro[1]]) return `Libro de ${ENCANTAMIENTOS[libro[1]].nombre} ${libro[2]}`
  return texto
}
