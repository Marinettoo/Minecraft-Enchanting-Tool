// Pruebas de interfaz de App1. No usan red ni IA: fetch está simulado.
// Ejecutar con: npm test
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import App from '../src/App.vue'

// Lo que devuelve el backend cuando todo va bien (docs/contrato-api.md, sección 3)
const resultado = {
  pasos: [{ orden: 1, izquierda: 'diamond_sword', derecha: 'Libro de sharpness 5', coste_niveles: 5 }],
  coste_total_niveles: 5,
  advertencias: [],
}
const respuesta = (cuerpo = { resultado }, status = 200) => ({
  ok: status < 400,
  status,
  json: async () => cuerpo,
})

let wrapper
let fetchMock

beforeEach(() => {
  fetchMock = vi.fn().mockResolvedValue(respuesta())
  vi.stubGlobal('fetch', fetchMock)
  wrapper = mount(App)
})
afterEach(() => {
  wrapper.unmount()
  vi.unstubAllGlobals()
})

// --- ayudas ---------------------------------------------------------------
const fila = (nombre) => wrapper.findAll('.enc').find((f) => f.get('label span').text() === nombre)
const casilla = (nombre) => fila(nombre).get('input[type="checkbox"]')
const marcar = (nombre) => casilla(nombre).setValue(true)
const boton = () => wrapper.get('button[type="submit"]')

async function elegirObjeto(tipo, material) {
  await wrapper.get('#tipo').setValue(tipo)
  if (material) await wrapper.get('#material').setValue(material)
}
async function elegirEspadaConFilo() {
  await elegirObjeto('sword', 'diamond')
  await marcar('Filo')
}
async function enviar() {
  await wrapper.get('form').trigger('submit')
  await flushPromises()
}

// --- formulario -----------------------------------------------------------
describe('Formulario', () => {
  it('pide elegir un objeto antes de enviar y no llama al servidor', async () => {
    await enviar()
    expect(wrapper.get('[role="alert"]').text()).toContain('Elige un objeto')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('pide al menos un encantamiento y no llama al servidor', async () => {
    await elegirObjeto('sword', 'diamond')
    await enviar()
    expect(wrapper.get('[role="alert"]').text()).toContain('al menos un encantamiento')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('el arco no tiene material y muestra sus encantamientos', async () => {
    await elegirObjeto('bow')
    expect(wrapper.get('#material').element.disabled).toBe(true)
    expect(fila('Poder')).toBeTruthy()
    expect(fila('Filo')).toBeUndefined()
  })

  it('solo ofrece los encantamientos que admite el objeto elegido', async () => {
    await elegirObjeto('sword', 'iron')
    expect(fila('Filo')).toBeTruthy()
    expect(fila('Botín')).toBeTruthy()
    expect(fila('Eficiencia')).toBeUndefined() // la eficiencia es de herramientas, no de espadas
  })

  it('bloquea los encantamientos incompatibles y los libera al desmarcar', async () => {
    await elegirObjeto('sword', 'diamond')
    await marcar('Filo')
    expect(casilla('Castigo').element.disabled).toBe(true)
    expect(casilla('Perdición de los artrópodos').element.disabled).toBe(true)
    await casilla('Filo').setValue(false)
    expect(casilla('Castigo').element.disabled).toBe(false)
  })

  it('no deja marcar más de 8 encantamientos', async () => {
    await elegirObjeto('boots', 'netherite')
    for (const nombre of [
      'Protección', 'Espinas', 'Caída de pluma', 'Agilidad acuática',
      'Velocidad del alma', 'Irrompibilidad', 'Reparación', 'Maldición de ligamiento',
    ]) await marcar(nombre)
    expect(wrapper.get('.contador').text()).toBe('8/8')
    expect(casilla('Maldición de desaparición').element.disabled).toBe(true)
  })

  it('al cambiar de objeto se limpian los encantamientos y el resultado', async () => {
    await elegirEspadaConFilo()
    await enviar()
    expect(wrapper.find('.pasos').exists()).toBe(true)
    await elegirObjeto('bow')
    expect(wrapper.findAll('input[type="checkbox"]:checked')).toHaveLength(0)
    expect(wrapper.find('.pasos').exists()).toBe(false)
  })
})

// --- envío y resultado ----------------------------------------------------
describe('Envío y resultado', () => {
  it('envía una sola petición con el contrato y muestra pasos y total', async () => {
    await elegirEspadaConFilo()
    await enviar()

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, opciones] = fetchMock.mock.calls[0]
    expect(url).toMatch(/\/api\/procesar$/)
    expect(opciones.method).toBe('POST')
    expect(JSON.parse(opciones.body)).toEqual({
      objeto: 'diamond_sword',
      encantamientos: [{ nombre: 'sharpness', nivel: 5 }],
    })

    // Las referencias del backend se traducen a texto legible
    const paso = wrapper.get('.paso')
    expect(paso.text()).toContain('Espada de diamante')
    expect(paso.text()).toContain('Libro de Filo V')
    expect(paso.text()).toContain('5 niv.')
    expect(wrapper.get('.total').text()).toContain('5 niveles')
  })

  it('envía el nivel elegido, no solo el máximo', async () => {
    await elegirEspadaConFilo()
    await fila('Filo').get('select').setValue(3)
    await enviar()
    expect(JSON.parse(fetchMock.mock.calls[0][1].body).encantamientos).toEqual([{ nombre: 'sharpness', nivel: 3 }])
  })

  it('bloquea el botón y evita envíos duplicados mientras espera', async () => {
    let terminar
    fetchMock.mockImplementationOnce(() => new Promise((resolve) => { terminar = resolve }))
    await elegirEspadaConFilo()
    await wrapper.get('form').trigger('submit')
    await wrapper.get('form').trigger('submit') // segundo clic: se ignora

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(boton().element.disabled).toBe(true)
    expect(boton().text()).toBe('Encantando…')

    terminar(respuesta())
    await flushPromises()
    expect(boton().element.disabled).toBe(false)
    expect(wrapper.find('.pasos').exists()).toBe(true)
  })

  it('una nueva consulta sustituye al resultado anterior, sin historial', async () => {
    await elegirEspadaConFilo()
    await enviar()
    fetchMock.mockResolvedValueOnce(respuesta({ resultado: { ...resultado, coste_total_niveles: 9 } }))
    await enviar()
    expect(wrapper.findAll('.total')).toHaveLength(1)
    expect(wrapper.get('.total').text()).toContain('9 niveles')
  })

  it('muestra las advertencias como texto, nunca como HTML', async () => {
    fetchMock.mockResolvedValueOnce(respuesta({
      resultado: { ...resultado, advertencias: ['<img src=x onerror="alert(1)">'] },
    }))
    await elegirEspadaConFilo()
    await enviar()
    expect(wrapper.get('.avisos').text()).toContain('<img')
    expect(wrapper.find('img').exists()).toBe(false)
  })

  it('no guarda la consulta en el navegador', async () => {
    const guardar = vi.spyOn(Storage.prototype, 'setItem')
    await elegirEspadaConFilo()
    await enviar()
    expect(guardar).not.toHaveBeenCalled()
  })
})

// --- errores y recuperación -----------------------------------------------
describe('Errores y recuperación', () => {
  it.each([422, 502, 504])('muestra el error %i del backend y permite repetir a mano', async (estado) => {
    fetchMock.mockResolvedValueOnce(respuesta({ error: { codigo: 'X', mensaje: `Error controlado ${estado}` } }, estado))
    await elegirEspadaConFilo()
    await enviar()

    expect(wrapper.get('[role="alert"]').text()).toContain(`Error controlado ${estado}`)
    expect(boton().element.disabled).toBe(false)
    expect(fetchMock).toHaveBeenCalledTimes(1) // sin reintento automático

    await enviar() // reintento manual: ahora responde bien
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(wrapper.get('.total').text()).toContain('5 niveles')
  })

  it('usa un mensaje genérico si el error no trae mensaje', async () => {
    fetchMock.mockResolvedValueOnce(respuesta({}, 500))
    await elegirEspadaConFilo()
    await enviar()
    expect(wrapper.get('[role="alert"]').text()).toContain('La petición ha fallado')
  })

  it('avisa si no se puede conectar con el servidor', async () => {
    fetchMock.mockRejectedValueOnce(new TypeError('fallo de red'))
    await elegirEspadaConFilo()
    await enviar()
    expect(wrapper.get('[role="alert"]').text()).toContain('No se puede conectar con el servidor')
    expect(boton().element.disabled).toBe(false)
  })

  it('avisa si el servidor tarda demasiado', async () => {
    fetchMock.mockRejectedValueOnce(new DOMException('tiempo agotado', 'TimeoutError'))
    await elegirEspadaConFilo()
    await enviar()
    expect(wrapper.get('[role="alert"]').text()).toContain('tarda demasiado')
    expect(boton().element.disabled).toBe(false)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})
