// @vitest-environment node
// Pruebas de las listas del contrato (src/data.js) y de su coherencia con el backend.
// Este archivo usa el entorno Node (no jsdom) porque lee rules.py del disco.
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { ENCANTAMIENTOS, INCOMPATIBLES, MAX_ENCANTAMIENTOS, OBJETOS, etiqueta, iconoObjeto, romano } from '../src/data.js'

describe('Listas cerradas', () => {
  it('tienen el tamaño del contrato', () => {
    expect(Object.keys(OBJETOS)).toHaveLength(58)
    expect(Object.keys(ENCANTAMIENTOS)).toHaveLength(39)
    expect(MAX_ENCANTAMIENTOS).toBe(8)
  })

  it('todo encantamiento tiene nivel máximo y al menos un tipo de objeto', () => {
    for (const [id, e] of Object.entries(ENCANTAMIENTOS)) {
      expect(e.max, id).toBeGreaterThanOrEqual(1)
      expect(e.tipos.length, id).toBeGreaterThan(0)
    }
  })

  it('los grupos de incompatibilidad solo citan encantamientos que existen', () => {
    expect(INCOMPATIBLES).toHaveLength(8)
    for (const grupo of INCOMPATIBLES) for (const id of grupo) expect(ENCANTAMIENTOS[id], id).toBeDefined()
  })
})

describe('Coherencia con el backend (app1/backend/rules.py)', () => {
  const reglas = readFileSync(fileURLToPath(new URL('../../backend/rules.py', import.meta.url)), 'utf8')

  it('los mismos encantamientos con el mismo nivel máximo', () => {
    const backend = Object.fromEntries([...reglas.matchAll(/"(\w+)": \((\d+),/g)].map(([, id, max]) => [id, Number(max)]))
    const frontend = Object.fromEntries(Object.entries(ENCANTAMIENTOS).map(([id, e]) => [id, e.max]))
    expect(frontend).toEqual(backend)
  })
})

describe('Textos', () => {
  it('traduce el objeto y los libros que devuelve el backend', () => {
    expect(etiqueta('diamond_sword')).toBe('Espada de diamante')
    expect(etiqueta('Libro de sharpness 5')).toBe('Libro de Filo V')
    expect(etiqueta('Libro de mending 1')).toBe('Libro de Reparación I')
  })

  it('deja tal cual lo que no reconoce', () => {
    expect(etiqueta('Resultado del paso 2')).toBe('Resultado del paso 2')
    expect(etiqueta('Libro de inventado 3')).toBe('Libro de inventado 3')
  })

  it('escribe los niveles en romanos', () => {
    expect([1, 2, 3, 4, 5].map(romano)).toEqual(['I', 'II', 'III', 'IV', 'V'])
  })

  it('da forma y material al icono de un objeto', () => {
    expect(iconoObjeto('netherite_pickaxe')).toEqual({ forma: 'pickaxe', material: 'netherite' })
    expect(iconoObjeto('bow')).toEqual({ forma: 'bow', material: 'neutro' })
    expect(iconoObjeto('no_existe')).toBeNull()
  })
})
