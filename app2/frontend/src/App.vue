<script setup>
import { SignIn, SignOutButton, useAuth } from '@clerk/vue'
import { onUnmounted, ref, watch } from 'vue'
import EnchantmentForm from './components/EnchantmentForm.vue'
import PlanResult from './components/PlanResult.vue'
import PixelIcon from './components/PixelIcon.vue'
import { processSelection } from './api.js'

const { isLoaded, isSignedIn, getToken } = useAuth()
const busy = ref(false)
const result = ref(null)
const error = ref('')
let controller
let requestId = 0

function clearConsultation() {
  requestId++
  controller?.abort()
  busy.value = false
  result.value = null
  error.value = ''
}

watch(isSignedIn, signedIn => { if (!signedIn) clearConsultation() })
onUnmounted(clearConsultation)

async function submit(selection) {
  if (busy.value || !isSignedIn.value) return
  busy.value = true
  result.value = null
  error.value = ''
  const current = ++requestId
  controller = new AbortController()
  const timeout = setTimeout(() => {
    if (current !== requestId) return
    controller.abort()
    requestId++
    error.value = 'La consulta ha tardado demasiado. Puedes volver a intentarlo.'
    busy.value = false
  }, 75000)
  try {
    const token = await getToken.value()
    if (current !== requestId) return
    if (!token) throw new Error('Vuelve a iniciar sesión para realizar la consulta.')
    const response = await processSelection(selection, token, controller.signal)
    if (current === requestId && isSignedIn.value) result.value = response
  } catch (cause) {
    if (current === requestId) {
      error.value = cause instanceof TypeError
        ? 'No se ha podido conectar. Comprueba la conexión y vuelve a intentarlo.'
        : cause.message || 'No se ha podido completar la consulta.'
    }
  } finally {
    clearTimeout(timeout)
    if (current === requestId) busy.value = false
  }
}
</script>

<template>
  <main class="book-scene">
    <header class="scene-heading">
      <span>MINECRAFT JAVA · TU LIBRO DE ENCANTAMIENTOS</span>
      <span>CADA NIVEL CUENTA</span>
    </header>
    <div class="enchanting-book">
      <section class="paper-page left-page" aria-labelledby="app-title">
        <header class="book-brand">
          <div>
            <h1 id="app-title" class="brand-title">MeT</h1>
            <p class="brand-subtitle">Minecraft Enchanting Tool</p>
          </div>
          <div class="icon-slot"><PixelIcon kind="pickaxe" /></div>
        </header>
        <template v-if="isLoaded && isSignedIn">
          <div class="session-bar">
            <span class="session-indicator">Has iniciado sesión</span>
            <SignOutButton><button type="button" class="session-button">Cerrar sesión</button></SignOutButton>
          </div>
          <EnchantmentForm :busy="busy" @submit="submit" />
        </template>
        <div v-else class="login-intro">
          <h2>El orden importa.</h2>
          <p>Tus herramientas, tus libros y el próximo gran encantamiento. Prepara la combinación antes de pasar por el yunque.</p>
          <div class="login-decoration"><PixelIcon kind="book" /></div>
        </div>
      </section>
      <section class="paper-page right-page" aria-labelledby="result-title">
        <span class="bookmark" aria-hidden="true"></span>
        <h2 id="result-title" class="page-title">{{ isSignedIn ? 'Orden del yunque' : 'Abre tu libro' }}</h2>
        <p v-if="!isLoaded" role="status" class="paper-loading">Cargando acceso…</p>
        <template v-else-if="isSignedIn">
          <p v-if="busy" role="status" class="paper-loading">Buscando un orden de combinación…</p>
          <p v-if="error" role="alert" class="paper-notice">{{ error }}</p>
          <div aria-live="polite">
            <PlanResult v-if="result" :result="result" />
            <div v-else-if="!busy && !error" class="result-placeholder">
              <PixelIcon kind="anvil" />
              <h3>Tu próxima mejora<br />empieza aquí.</h3>
              <p>Elige el objeto y sus libros. Aquí aparecerán las combinaciones y el coste estimado.</p>
            </div>
          </div>
        </template>
        <div v-else class="clerk-container">
          <SignIn routing="hash" :withSignUp="true" />
        </div>
      </section>
    </div>
    <footer class="scene-footer">Un objeto. Tus libros. El orden para combinarlos.</footer>
  </main>
</template>
