# Frontend de MeT

Interfaz en Vue 3 + Vite + Tailwind CSS que simula un libro de encantamientos de Minecraft (tipografía Monocraft).

## Qué hace
1. El usuario elige un **objeto** (pico, espada, arco...) y, si lo tiene, un **material**. Arcos, ballestas, cañas de pescar y tridentes no tienen material.
2. Marca los encantamientos y niveles disponibles para ese objeto (entre 1 y 8, sin incompatibles).
3. Pulsa **Calcular orden**: envía `POST /api/procesar` al backend y muestra los pasos del yunque, el coste total y las advertencias.

## Ejecutar
```bash
npm install
cp .env.example .env     # VITE_API_BASE_URL=http://localhost:8000
npm run dev              # http://localhost:5173
```

`npm run build` genera `dist/`. La variable `VITE_API_BASE_URL` es pública: nunca pongas aquí la clave de la IA.

## Archivos principales
- `src/App.vue`: formulario, validación en cliente y llamada a la API.
- `src/data.js`: objetos, materiales, encantamientos e incompatibilidades (deben coincidir con `app1/backend/rules.py`).
- `src/icons.js` y `src/components/ItemIcon.vue`: iconos de píxel dibujados a mano.
- `src/style.css`: estilo del libro y fuente Monocraft (`src/assets/fonts/`, licencia en `Monocraft-OFL.txt`).
