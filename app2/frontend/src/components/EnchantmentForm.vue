<script setup>
import { computed, ref, watch } from 'vue'
import { enchantments, incompatible, materialNames, objects, objectTypes } from '../data.js'
import PixelIcon from './PixelIcon.vue'

defineProps({ busy: Boolean })
const emit = defineEmits(['submit'])
const typeId = ref('')
const materialId = ref('')
const selected = ref([])
const levels = ref({})
const notice = ref('')
const materials = computed(() => objects.filter(object => object.type === typeId.value && object.id !== object.type)
  .map(object => object.id.split('_')[0]))
const objectId = computed(() => materials.value.length
  ? (materialId.value ? `${materialId.value}_${typeId.value}` : '') : typeId.value)
const available = computed(() => enchantments.filter(enchantment => enchantment.types.includes(typeId.value)))
const roman = ['I', 'II', 'III', 'IV', 'V']

watch(typeId, () => { materialId.value = '' })
watch(objectId, () => {
  selected.value = []
  levels.value = {}
  notice.value = ''
})

function blocked(id) {
  if (selected.value.includes(id)) return false
  return selected.value.length >= 8 || incompatible.some(group =>
    group.includes(id) && selected.value.some(name => group.includes(name)))
}

function select(enchantment, checked) {
  notice.value = ''
  if (checked) {
    selected.value.push(enchantment.id)
    levels.value[enchantment.id] = enchantment.max
  } else {
    selected.value = selected.value.filter(id => id !== enchantment.id)
    delete levels.value[enchantment.id]
  }
}

function submit() {
  if (!objectId.value || selected.value.length === 0) {
    notice.value = 'Elige un objeto, su material y al menos un encantamiento.'
    return
  }
  emit('submit', {
    objeto: objectId.value,
    encantamientos: selected.value.map(nombre => ({ nombre, nivel: levels.value[nombre] })),
  })
}
</script>

<template>
  <form @submit.prevent="submit" class="enchantment-form">
    <fieldset :disabled="busy">
      <legend class="sr-only">Tu selección</legend>
      <div class="object-selectors">
        <div>
          <label for="object">Objeto</label>
          <select id="object" v-model="typeId">
            <option value="">Selecciona</option>
            <option v-for="(name, id) in objectTypes" :key="id" :value="id">{{ name }}</option>
          </select>
        </div>
        <div>
          <label for="material">Material</label>
          <select id="material" v-model="materialId" :disabled="!materials.length">
            <option value="">{{ materials.length ? 'Selecciona' : '—' }}</option>
            <option v-for="material in materials" :key="material" :value="material">{{ materialNames[material] }}</option>
          </select>
        </div>
      </div>
      <div class="enchantments-heading">
        <h2>Encantamientos</h2>
        <span aria-label="Encantamientos seleccionados">{{ selected.length }}/8</span>
      </div>
      <div v-if="!typeId" class="selection-empty">
        <PixelIcon kind="pickaxe" />
        <p>Elige tu objeto para descubrir sus encantamientos.</p>
      </div>
      <div v-else class="enchantment-list">
        <div v-for="enchantment in available" :key="enchantment.id"
             class="enchantment-row" :class="{ selected: selected.includes(enchantment.id), unavailable: blocked(enchantment.id) }">
          <label class="enchantment-name">
            <input type="checkbox" :checked="selected.includes(enchantment.id)" :disabled="blocked(enchantment.id)"
                   @change="select(enchantment, $event.target.checked)" />
            <span>{{ enchantment.name }}</span>
          </label>
          <select :aria-label="`Nivel de ${enchantment.name}`" :value="levels[enchantment.id] ?? enchantment.max"
                  :disabled="!selected.includes(enchantment.id)"
                  @change="levels[enchantment.id] = Number($event.target.value)" class="level-select">
            <option v-for="level in enchantment.max" :key="level" :value="level">{{ roman[level - 1] }}</option>
          </select>
        </div>
      </div>
      <p v-if="typeId" class="selection-hint">De 1 a 8 libros. Las opciones incompatibles se desactivan.</p>
    </fieldset>
    <p v-if="notice" role="alert" class="paper-notice">{{ notice }}</p>
    <button type="submit" :disabled="busy" class="stone-button calculate-button">
      {{ busy ? 'Consultando…' : 'Calcular orden' }}
    </button>
  </form>
</template>
