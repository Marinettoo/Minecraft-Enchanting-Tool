<script setup>
import { computed } from 'vue'
import { pixeles } from '../icons.js'

const props = defineProps({
  forma: { type: String, required: true },
  material: { type: String, default: 'neutro' },
  size: { type: Number, default: 32 },
  encantado: { type: Boolean, default: false },
})

const puntos = computed(() => pixeles(props.forma, props.material))
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="-1 -1 18 18"
    shape-rendering="crispEdges"
    aria-hidden="true"
    focusable="false"
    class="icono"
    :class="{ encantado }"
  >
    <rect v-for="p in puntos" :key="`${p.x}-${p.y}`" :x="p.x" :y="p.y" width="1" height="1" :fill="p.fill" />
  </svg>
</template>
