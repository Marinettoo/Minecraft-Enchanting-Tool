import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import App from '../src/App.vue'

const auth = vi.hoisted(() => ({ state: null }))
vi.mock('@clerk/vue', async () => {
  const { ref, h, defineComponent } = await import('vue')
  auth.state = { isLoaded: ref(true), isSignedIn: ref(true), getToken: ref(vi.fn()) }
  return {
    useAuth: () => auth.state,
    SignIn: defineComponent({ setup: () => () => h('p', 'Formulario de acceso') }),
    SignOutButton: defineComponent({
      setup: (_, { slots }) => () => h('div', {
        onClick: () => { auth.state.isSignedIn.value = false },
      }, slots.default?.()),
    }),
  }
})

const result = {
  pasos: [{ orden: 1, izquierda: 'Espada de diamante', derecha: 'Libro de Filo V', coste_niveles: 5 }],
  coste_total_niveles: 5, advertencias: [],
}
const response = (data = { resultado: result }, status = 200) => ({
  ok: status < 400, status, json: async () => data,
})
let wrapper
let fetchMock

beforeEach(() => {
  auth.state.isLoaded.value = true
  auth.state.isSignedIn.value = true
  auth.state.getToken.value.mockReset().mockResolvedValue('token_ficticio')
  fetchMock = vi.fn().mockResolvedValue(response())
  vi.stubGlobal('fetch', fetchMock)
  wrapper = mount(App)
})
afterEach(() => {
  wrapper.unmount()
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

async function chooseSword() {
  await wrapper.get('#object').setValue('sword')
  await wrapper.get('#material').setValue('diamond')
  const row = wrapper.findAll('.enchantment-row').find(row => row.get('.enchantment-name').text() === 'Filo')
  await row.get('input').setValue(true)
}
async function submit() {
  await wrapper.get('form').trigger('submit')
  await flushPromises()
}

describe('Selección y envío', () => {
  it('explica los datos que faltan sin enviar', async () => {
    await submit()
    expect(wrapper.get('[role="alert"]').text()).toContain('Elige un objeto')
    expect(fetchMock).not.toHaveBeenCalled()
  })
  it('desactiva incompatibilidades y limpia al cambiar de objeto', async () => {
    await chooseSword()
    const row = wrapper.findAll('.enchantment-row').find(row => row.get('.enchantment-name').text() === 'Castigo')
    expect(row.get('input').element.disabled).toBe(true)
    await wrapper.get('#object').setValue('bow')
    expect(wrapper.findAll('input:checked')).toHaveLength(0)
  })
  it('envía identificadores y token una vez y muestra el resultado', async () => {
    await chooseSword()
    await submit()
    expect(fetchMock).toHaveBeenCalledTimes(1)
    const options = fetchMock.mock.calls[0][1]
    expect(options.headers.Authorization).toBe('Bearer token_ficticio')
    expect(JSON.parse(options.body)).toEqual({ objeto: 'diamond_sword', encantamientos: [{ nombre: 'sharpness', nivel: 5 }] })
    expect(wrapper.get('.total-cost').text()).toContain('5 niveles')
  })
  it('bloquea envíos duplicados y retira el resultado anterior al repetir', async () => {
    await chooseSword()
    await submit()
    let finish
    fetchMock.mockImplementationOnce(() => new Promise(resolve => { finish = resolve }))
    await submit()
    await wrapper.get('form').trigger('submit')
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(wrapper.find('.plan-result').exists()).toBe(false)
    expect(wrapper.get('.calculate-button').element.disabled).toBe(true)
    finish(response())
    await flushPromises()
    expect(wrapper.get('.calculate-button').element.disabled).toBe(false)
  })
  it('no guarda la consulta y empieza vacía al montar de nuevo la pantalla', async () => {
    const persist = vi.spyOn(Storage.prototype, 'setItem')
    await chooseSword()
    await submit()
    expect(wrapper.get('.total-cost').text()).toContain('5 niveles')
    expect(persist).not.toHaveBeenCalled()
    wrapper.unmount()
    wrapper = mount(App)
    expect(wrapper.find('.plan-result').exists()).toBe(false)
    expect(wrapper.get('#object').element.value).toBe('')
    expect(wrapper.findAll('input:checked')).toHaveLength(0)
  })
})

describe('Errores y recuperación', () => {
  it.each([401, 422, 502, 504])('muestra el error %i y permite repetir sin reintento automático', async status => {
    fetchMock.mockResolvedValueOnce(response({ error: { mensaje: `Error controlado ${status}` } }, status))
    await chooseSword()
    await submit()
    expect(wrapper.get('[role="alert"]').text()).toContain(`Error controlado ${status}`)
    expect(wrapper.get('.calculate-button').element.disabled).toBe(false)
    expect(fetchMock).toHaveBeenCalledTimes(1)
    await submit()
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(wrapper.get('.total-cost').text()).toContain('5 niveles')
  })
  it('trata la conexión interrumpida', async () => {
    fetchMock.mockRejectedValueOnce(new TypeError('fallo de red'))
    await chooseSword()
    await submit()
    expect(wrapper.get('[role="alert"]').text()).toContain('No se ha podido conectar')
    expect(wrapper.get('.calculate-button').element.disabled).toBe(false)
  })
  it('trata una respuesta que no es JSON', async () => {
    fetchMock.mockResolvedValueOnce({ ok: true, json: async () => { throw new SyntaxError('HTML') } })
    await chooseSword()
    await submit()
    expect(wrapper.get('[role="alert"]').text()).toContain('respuesta utilizable')
  })
  it('rechaza una respuesta sin los campos de resultado', async () => {
    fetchMock.mockResolvedValueOnce(response({ resultado: {} }))
    await chooseSword()
    await submit()
    expect(wrapper.get('[role="alert"]').text()).toContain('no se puede mostrar')
  })
  it('pide acceder otra vez si Clerk no entrega un token', async () => {
    auth.state.getToken.value.mockResolvedValueOnce(null)
    await chooseSword()
    await submit()
    expect(wrapper.get('[role="alert"]').text()).toContain('Vuelve a iniciar sesión')
    expect(fetchMock).not.toHaveBeenCalled()
  })
  it('limita la espera del navegador sin reintentos', async () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    fetchMock.mockImplementationOnce(() => new Promise(() => {}))
    await chooseSword()
    await submit()
    await vi.advanceTimersByTimeAsync(75000)
    expect(wrapper.get('[role="alert"]').text()).toContain('demasiado')
    expect(wrapper.get('.calculate-button').element.disabled).toBe(false)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
  it('no muestra una respuesta tardía tras cerrar sesión', async () => {
    let finish
    fetchMock.mockImplementationOnce(() => new Promise(resolve => { finish = resolve }))
    await chooseSword()
    await submit()
    await wrapper.get('.session-button').trigger('click')
    finish(response())
    await flushPromises()
    expect(wrapper.text()).toContain('Formulario de acceso')
    expect(wrapper.find('.plan-result').exists()).toBe(false)
    expect(wrapper.find('form').exists()).toBe(false)
  })
  it('muestra las etiquetas HTML como texto', async () => {
    fetchMock.mockResolvedValueOnce(response({ resultado: {
      ...result, advertencias: ['<img src=x onerror="alert(1)">'],
    } }))
    await chooseSword()
    await submit()
    expect(wrapper.get('.warnings-list').text()).toContain('<img')
    expect(wrapper.find('img').exists()).toBe(false)
  })
})
