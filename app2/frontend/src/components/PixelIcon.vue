<script setup>
defineProps({ kind: { type: String, default: 'anvil' } })
</script>

<template>
  <svg viewBox="0 0 24 24" aria-hidden="true" class="pixel-icon" shape-rendering="crispEdges">
    <g v-if="kind === 'book'">
      <path fill="#322038" d="M5 3h13v2h2v16H5v-2H3V5h2z" />
      <path fill="#76509a" d="M5 5h12v13H5z" />
      <path fill="#b591cf" d="M7 5h2v13H7zm4 2h4v2h-4zm1 5h3v2h-3z" />
      <path fill="#e8d7a3" d="M5 18h13v2H5z" />
      <path fill="#563070" d="M17 5h2v13h-2z" />
    </g>
    <g v-else-if="kind === 'pickaxe'">
      <path fill="#392a25" d="M4 3h12v2h4v7h-3V8h-5v3h-2v3H8v3H6v3H3v-4h2v-3h3v-3h2V6H4z" />
      <path fill="#c6c4b8" d="M5 4h10v2h4v5h-1V7h-6V6H5z" />
      <path fill="#a17b49" d="M10 8h2v3h-2v3H8v3H6v2H4v-2h2v-3h2v-3h2z" />
    </g>
    <g v-else>
      <path fill="#29282b" d="M3 4h18v5h-4v3h-3v5h4v3H6v-3h4v-5H7V9H3z" />
      <path fill="#a5a2a0" d="M3 4h18v2H3z" />
      <path fill="#777477" d="M5 6h14v2h-4v3H9V8H5zM7 17h10v2H7z" />
      <path fill="#58545c" d="M11 11h2v6h-2z" />
    </g>
  </svg>
</template>
