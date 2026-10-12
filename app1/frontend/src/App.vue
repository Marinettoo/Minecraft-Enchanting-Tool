<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { OBJETOS, ENCANTAMIENTOS, INCOMPATIBLES, MAX_ENCANTAMIENTOS, etiqueta } from './data.js'

// Para trabajar sin backend: VITE_USAR_RESPUESTA_FALSA=true en .env.local
const USAR_RESPUESTA_FALSA = import.meta.env.VITE_USAR_RESPUESTA_FALSA === 'true'
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const TIEMPO_MAX_MS = 65000 // el backend espera a la IA 60 s como máximo (AI_TIMEOUT_SECONDS)

const objetos = Object.entries(OBJETOS).map(([id, o]) => ({ id, nombre: o.nombre }))

const objeto = ref('')
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
  <main class="mx-auto max-w-2xl p-4 sm:p-8">
    <h1 class="text-3xl font-bold text-green-700">MeT</h1>
    <p class="mb-6 text-gray-600">Minecraft Enchanting Tool: el orden de encantado que gasta menos niveles.</p>

    <form class="space-y-6" @submit.prevent="enviar">
      <div>
        <label for="objeto" class="mb-1 block font-semibold">Objeto</label>
        <select id="objeto" v-model="objeto" class="w-full rounded border border-gray-400 p-2 focus:outline-2 focus:outline-green-600">
          <option value="" disabled>Elige un objeto…</option>
          <option v-for="o in objetos" :key="o.id" :value="o.id">{{ o.nombre }}</option>
        </select>
      </div>

      <fieldset>
        <legend class="mb-2 font-semibold">Encantamientos (máximo 8)</legend>
        <p v-if="!objeto" class="text-sm text-gray-600">Elige primero un objeto.</p>
        <ul class="grid gap-2 sm:grid-cols-2">
          <li v-for="e in lista" :key="e.id" class="flex items-center justify-between gap-2 rounded border border-gray-300 p-2">
            <label class="flex items-center gap-2">
              <input v-model="seleccion[e.id].activo" type="checkbox" :disabled="bloqueado(e.id)" class="h-4 w-4 accent-green-700 disabled:opacity-40" />
              {{ e.nombre }}
            </label>
            <select
              v-model="seleccion[e.id].nivel"
              :disabled="!seleccion[e.id].activo"
              :aria-label="`Nivel de ${e.nombre}`"
              class="rounded border border-gray-400 p-1 disabled:opacity-40"
            >
              <option v-for="n in e.max" :key="n" :value="n">{{ n }}</option>
            </select>
          </li>
        </ul>
      </fieldset>

      <button
        type="submit"
        :disabled="estado === 'espera'"
        class="w-full rounded bg-green-700 px-4 py-3 font-semibold text-white hover:bg-green-800 focus:outline-2 focus:outline-offset-2 focus:outline-green-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {{ estado === 'espera' ? 'Calculando…' : 'Calcular orden' }}
      </button>
    </form>

    <p v-if="estado === 'error'" role="alert" class="mt-6 rounded border border-red-300 bg-red-50 p-3 text-red-800">
      {{ mensaje }}
    </p>

    <section v-if="estado === 'resultado' && resultado" class="mt-6 rounded border border-green-300 bg-green-50 p-4" aria-live="polite">
      <h2 class="mb-2 text-xl font-bold">Orden recomendado</h2>
      <ol class="list-decimal space-y-1 pl-5">
        <li v-for="p in resultado.pasos" :key="p.orden" class="break-words">
          {{ etiqueta(p.izquierda) }} + {{ etiqueta(p.derecha) }}: {{ p.coste_niveles }} niveles
        </li>
      </ol>
      <p class="mt-3 font-semibold">Coste total: {{ resultado.coste_total_niveles }} niveles</p>
      <ul v-if="resultado.advertencias?.length" class="mt-2 list-disc pl-5 text-sm text-gray-700">
        <li v-for="(a, i) in resultado.advertencias" :key="i">{{ a }}</li>
      </ul>
    </section>
  </main>
</template>