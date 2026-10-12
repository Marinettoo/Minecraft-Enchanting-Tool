<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { OBJETOS, TIPOS_OBJETO, ENCANTAMIENTOS, INCOMPATIBLES, MAX_ENCANTAMIENTOS, etiqueta, romano, iconoObjeto } from './data.js'
import ItemIcon from './components/ItemIcon.vue'

// Para trabajar sin backend: VITE_USAR_RESPUESTA_FALSA=true en .env.local
const USAR_RESPUESTA_FALSA = import.meta.env.VITE_USAR_RESPUESTA_FALSA === 'true'
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const TIEMPO_MAX_MS = 65000 // el backend espera a la IA 60 s como máximo (AI_TIMEOUT_SECONDS)

// El objeto se elige en dos pasos: tipo (pico, casco, arco...) y material (netherita...)
const tipo = ref('')
const material = ref('')
const materialesDisponibles = computed(() => TIPOS_OBJETO.find((t) => t.id === tipo.value)?.materiales ?? [])

// Id final del objeto (p. ej. netherite_pickaxe). Sin material (arco...), es solo el tipo.
const objeto = computed(() => {
  if (!tipo.value) return ''
  if (materialesDisponibles.value.length === 0) return tipo.value
  return material.value ? `${material.value}_${tipo.value}` : ''
})
const vistaPrevia = computed(() => iconoObjeto(objeto.value) ?? (tipo.value ? { forma: tipo.value, material: 'neutro' } : null))

watch(tipo, () => {
  if (!materialesDisponibles.value.some((m) => m.id === material.value)) material.value = ''
})
const estado = ref('entrada') // entrada | espera | resultado | error
const resultado = ref(null)
const mensaje = ref('')

// Estado de cada encantamiento (marcado y nivel elegido)
const seleccion = reactive(
  Object.fromEntries(Object.entries(ENCANTAMIENTOS).map(([id, e]) => [id, { activo: false, nivel: e.max }])),
)

// Solo los encantamientos que admite el objeto elegido
const lista = computed(() => {
  const tipo = OBJETOS[objeto.value]?.tipo
  if (!tipo) return []
  return Object.entries(ENCANTAMIENTOS)
    .filter(([, e]) => e.tipos.includes(tipo))
    .map(([id, e]) => ({ id, nombre: e.nombre, max: e.max }))
})

const activos = computed(() => lista.value.filter((e) => seleccion[e.id].activo))

// Un encantamiento queda bloqueado si es incompatible con otro marcado
// o si ya se han marcado 8.
function bloqueado(id) {
  if (seleccion[id].activo) return false
  if (activos.value.length >= MAX_ENCANTAMIENTOS) return true
  return INCOMPATIBLES.some((g) => g.includes(id) && g.some((o) => o !== id && seleccion[o].activo))
}

watch(objeto, () => {
  for (const s of Object.values(seleccion)) s.activo = false
  estado.value = 'entrada'
  resultado.value = null
})

// Icono de una etiqueta del resultado: objeto, libro o resultado de un paso anterior
function icono(texto, profundidad = 0) {
  if (OBJETOS[texto]) return { ...iconoObjeto(texto), encantado: false }
  if (texto.startsWith('Libro de')) return { forma: 'book', material: 'neutro', encantado: false }
  const m = /^Resultado del paso (\d+)$/.exec(texto)
  const paso = m && profundidad < 8 && resultado.value?.pasos[Number(m[1]) - 1]
  if (paso) {
    const base = icono(paso.izquierda, profundidad + 1)
    return base && { ...base, encantado: base.forma !== 'book' }
  }
  return null
}

function fallo(texto) {
  mensaje.value = texto
  estado.value = 'error'
}

async function enviar() {
  if (estado.value === 'espera') return // evita envíos duplicados

  const elegidos = activos.value.map((e) => ({ nombre: e.id, nivel: Number(seleccion[e.id].nivel) }))

  // Validación del frontend (ayuda al usuario; el backend vuelve a validar)
  if (!objeto.value) return fallo('Elige un objeto.')
  if (elegidos.length === 0) return fallo('Elige al menos un encantamiento.')

  estado.value = 'espera'
  resultado.value = null
  try {
    let datos
    if (USAR_RESPUESTA_FALSA) {
      await new Promise((r) => setTimeout(r, 800))
      datos = {
        resultado: {
          pasos: [{ orden: 1, izquierda: 'Objeto', derecha: 'Libro de ejemplo', coste_niveles: 5 }],
          coste_total_niveles: 5,
          advertencias: ['Respuesta falsa de prueba.'],
        },
      }
    } else {
      const resp = await fetch(`${API_URL}/api/procesar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ objeto: objeto.value, encantamientos: elegidos }),
        signal: AbortSignal.timeout(TIEMPO_MAX_MS),
      })
      const cuerpo = await resp.json().catch(() => ({}))
      if (!resp.ok) return fallo(cuerpo?.error?.mensaje || 'La petición ha fallado.')
      datos = cuerpo
    }
    resultado.value = datos.resultado
    estado.value = 'resultado'
  } catch (e) {
    fallo(
      e?.name === 'TimeoutError'
        ? 'El servidor tarda demasiado en responder. Inténtalo más tarde.'
        : 'No se puede conectar con el servidor. Comprueba que el backend está en marcha.',
    )
  }
}
</script>

<template>
  <main class="libro">
    <!-- Página izquierda: el formulario -->
    <form class="pagina pagina-izq" @submit.prevent="enviar">
      <header class="cabecera">
        <div>
          <h1 class="titulo">MeT</h1>
          <p class="subtitulo">Minecraft Enchanting Tool</p>
        </div>
        <div class="ranura" aria-hidden="true">
          <ItemIcon v-if="vistaPrevia" v-bind="vistaPrevia" :size="44" />
        </div>
      </header>

      <div class="campo campo-doble">
        <div>
          <label for="tipo">Objeto</label>
          <select id="tipo" v-model="tipo" class="control">
            <option value="" disabled>Elige…</option>
            <option v-for="t in TIPOS_OBJETO" :key="t.id" :value="t.id">{{ t.nombre }}</option>
          </select>
        </div>
        <div>
          <label for="material">Material</label>
          <select id="material" v-model="material" class="control" :disabled="!materialesDisponibles.length">
            <option value="" disabled>{{ tipo && !materialesDisponibles.length ? 'No aplica' : 'Elige…' }}</option>
            <option v-for="m in materialesDisponibles" :key="m.id" :value="m.id">{{ m.nombre }}</option>
          </select>
        </div>
      </div>

      <fieldset class="campo">
        <legend>
          <span>Encantamientos</span>
          <span class="contador">{{ activos.length }}/{{ MAX_ENCANTAMIENTOS }}</span>
        </legend>
        <p v-if="!objeto" class="pista">Elige primero un objeto{{ tipo ? ' y su material' : '' }}.</p>
        <ul class="list-none m-0 p-0">
          <li v-for="e in lista" :key="e.id" class="enc">
            <label>
              <input v-model="seleccion[e.id].activo" type="checkbox" :disabled="bloqueado(e.id)" />
              <span>{{ e.nombre }}</span>
            </label>
            <select
              v-model="seleccion[e.id].nivel"
              :disabled="!seleccion[e.id].activo"
              :aria-label="`Nivel de ${e.nombre}`"
              class="control control-nivel"
            >
              <option v-for="n in e.max" :key="n" :value="n">{{ romano(n) }}</option>
            </select>
          </li>
        </ul>
      </fieldset>

      <button type="submit" class="boton" :disabled="estado === 'espera'">
        {{ estado === 'espera' ? 'Encantando…' : 'Calcular orden' }}
      </button>
    </form>

    <!-- Página derecha: el resultado -->
    <section class="pagina pagina-der" aria-live="polite">
      <h2 class="encabezado">Orden del yunque</h2>

      <template v-if="estado === 'espera'">
        <div class="brillo" aria-hidden="true"></div>
        <p class="pista">El libro está brillando… la IA calcula el orden más barato.</p>
      </template>

      <p v-else-if="estado === 'error'" role="alert" class="error">{{ mensaje }}</p>

      <template v-else-if="estado === 'resultado' && resultado">
        <ol class="pasos">
          <li v-for="p in resultado.pasos" :key="p.orden" class="paso">
            <span class="paso-n">{{ p.orden }}</span>
            <span class="paso-texto">
              <span class="linea">
                <ItemIcon v-if="icono(p.izquierda)" v-bind="icono(p.izquierda)" :size="24" />
                <span>{{ etiqueta(p.izquierda) }}</span>
              </span>
              <span class="linea">
                <span class="paso-mas">+</span>
                <ItemIcon v-if="icono(p.derecha)" v-bind="icono(p.derecha)" :size="24" />
                <span>{{ etiqueta(p.derecha) }}</span>
              </span>
            </span>
            <span class="paso-coste">{{ p.coste_niveles }} niv.</span>
          </li>
        </ol>
        <p class="total">
          <span>Coste total</span>
          <strong><span class="orbe" aria-hidden="true"></span>{{ resultado.coste_total_niveles }} niveles</strong>
        </p>
        <ul v-if="resultado.advertencias?.length" class="avisos">
          <li v-for="(a, i) in resultado.advertencias" :key="i">{{ a }}</li>
        </ul>
      </template>

      <div v-else class="hueco">
        <p class="pista">
          Elige un objeto y sus encantamientos en la página de la izquierda y pulsa «Calcular orden».
        </p>
      </div>
    </section>
  </main>
</template>
