<script setup>
import PixelIcon from './PixelIcon.vue'
defineProps({ result: { type: Object, required: true } })
</script>

<template>
  <section class="plan-result" aria-label="Resultado de la consulta">
    <ol class="steps-list">
      <li v-for="step in result.pasos" :key="step.orden" class="step-card">
        <span class="step-number" :aria-label="`Paso ${step.orden}`">{{ step.orden }}</span>
        <div class="step-items">
          <p><PixelIcon :kind="step.izquierda.startsWith('Libro') ? 'book' : 'anvil'" />
            <span><span class="sr-only">Izquierda: </span>{{ step.izquierda }}</span></p>
          <p><span class="plus-sign" aria-hidden="true">+</span><PixelIcon :kind="step.derecha.startsWith('Libro') ? 'book' : 'anvil'" />
            <span><span class="sr-only">Derecha: </span>{{ step.derecha }}</span></p>
        </div>
        <span class="step-cost" :aria-label="`Coste estimado: ${step.coste_niveles} niveles`">{{ step.coste_niveles }} niv.</span>
      </li>
    </ol>
    <div class="total-cost">
      <span>Total estimado</span>
      <strong><span class="experience-gem" aria-hidden="true"></span>{{ result.coste_total_niveles }} niveles</strong>
    </div>
    <ul v-if="result.advertencias.length" class="warnings-list">
      <li v-for="(warning, index) in result.advertencias" :key="index">{{ warning }}</li>
    </ul>
  </section>
</template>
