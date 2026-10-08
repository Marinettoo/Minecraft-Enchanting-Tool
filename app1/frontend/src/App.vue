<script setup>
import { ref, reactive } from 'vue'

// Mientras el backend no esté listo, dejar en true para usar una respuesta falsa.
const USAR_RESPUESTA_FALSA = true
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Listas cerradas del contrato (sección 5). Ampliar cuando se acuerde con el backend.
const objetos = [
  { id: 'diamond_sword', nombre: 'Espada de diamante' },
  { id: 'diamond_pickaxe', nombre: 'Pico de diamante' },
  { id: 'diamond_helmet', nombre: 'Casco de diamante' },
  { id: 'diamond_chestplate', nombre: 'Pechera de diamante' },
  { id: 'diamond_boots', nombre: 'Botas de diamante' },
  { id: 'bow', nombre: 'Arco' },
]

const lista = reactive([
  { id: 'sharpness', nombre: 'Filo', max: 5 },
  { id: 'smite', nombre: 'Castigo', max: 5 },
  { id: 'bane_of_arthropods', nombre: 'Perdición de los artrópodos', max: 5 },
  { id: 'knockback', nombre: 'Empuje', max: 2 },
  { id: 'fire_aspect', nombre: 'Aspecto ígneo', max: 2 },
  { id: 'looting', nombre: 'Botín', max: 3 },
  { id: 'sweeping_edge', nombre: 'Filo barredor', max: 3 },
  { id: 'unbreaking', nombre: 'Irrompibilidad', max: 3 },
  { id: 'mending', nombre: 'Reparación', max: 1 },
  { id: 'efficiency', nombre: 'Eficiencia', max: 5 },
  { id: 'fortune', nombre: 'Fortuna', max: 3 },
  { id: 'silk_touch', nombre: 'Toque de seda', max: 1 },
  { id: 'protection', nombre: 'Protección', max: 4 },
  { id: 'thorns', nombre: 'Espinas', max: 3 },
  { id: 'feather_falling', nombre: 'Caída de pluma', max: 4 },
  { id: 'power', nombre: 'Poder', max: 5 },
  { id: 'infinity', nombre: 'Infinidad', max: 1 },
].map((e) => ({ ...e, activo: false, nivel: e.max })))

const objeto = ref('')
const estado = ref('entrada') // entrada | espera | resultado | error
const resultado = ref(null)
const mensaje = ref('')

const esperar = (ms) => new Promise((r) => setTimeout(r, ms))

async function enviar() {
  if (estado.value === 'espera') return // evita envíos duplicados

  const elegidos = lista
    .filter((e) => e.activo)
    .map((e) => ({ nombre: e.id, nivel: Number(e.nivel) }))

  // Validación del frontend (ayuda al usuario; el backend vuelve a validar)
  if (!objeto.value) {
    mensaje.value = 'Elige un objeto.'
    estado.value = 'error'
    return
  }
  if (elegidos.length === 0 || elegidos.length > 8) {
    mensaje.value = 'Elige entre 1 y 8 encantamientos.'
    estado.value = 'error'
    return
  }

  estado.value = 'espera'
  resultado.value = null
  try {
    let datos
    if (USAR_RESPUESTA_FALSA) {
      await esperar(800)
      datos = {
        resultado: {
          pasos: [
            { orden: 1, izquierda: 'Objeto', derecha: 'Libro de ejemplo', coste_niveles: 5 },
            { orden: 2, izquierda: 'Objeto (con ejemplo)', derecha: 'Otro libro', coste_niveles: 3 },
          ],
          coste_total_niveles: 8,
          advertencias: ['Respuesta falsa de prueba.'],
        },
      }
    } else {
      const resp = await fetch(`${API_URL}/api/procesar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ objeto: objeto.value, encantamientos: elegidos }),
      })
      const cuerpo = await resp.json().catch(() => ({}))
      if (!resp.ok) {
        throw new Error(cuerpo?.error?.mensaje || 'La petición no es válida o ha fallado.')
      }
      datos = cuerpo
    }
    resultado.value = datos.resultado
    estado.value = 'resultado'
  } catch (e) {
    mensaje.value = e.message || 'No se ha podido completar la petición.'
    estado.value = 'error'
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
        <ul class="grid gap-2 sm:grid-cols-2">
          <li v-for="e in lista" :key="e.id" class="flex items-center justify-between gap-2 rounded border border-gray-300 p-2">
            <label class="flex items-center gap-2">
              <input v-model="e.activo" type="checkbox" class="h-4 w-4 accent-green-700" />
              {{ e.nombre }}
            </label>
            <select
              v-model="e.nivel"
              :disabled="!e.activo"
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
          {{ p.izquierda }} + {{ p.derecha }}: {{ p.coste_niveles }} niveles
        </li>
      </ol>
      <p class="mt-3 font-semibold">Coste total: {{ resultado.coste_total_niveles }} niveles</p>
      <ul v-if="resultado.advertencias?.length" class="mt-2 list-disc pl-5 text-sm text-gray-700">
        <li v-for="(a, i) in resultado.advertencias" :key="i">{{ a }}</li>
      </ul>
    </section>
  </main>
</template>