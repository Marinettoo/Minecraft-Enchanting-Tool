// Iconos pixelados de 16x16 dibujados a mano (originales, sin texturas de Mojang).
// Cada forma se dibuja en una rejilla y se colorea según el material.

const N = 16

const MATERIALES = {
  wooden: { H: '#a8763f', h: '#7a4f26', L: '#c99a60' },
  stone: { H: '#8f8f8f', h: '#5f5f5f', L: '#b4b4b4' },
  iron: { H: '#d6d6d6', h: '#9a9a9a', L: '#f4f4f4' },
  golden: { H: '#f2c230', h: '#b8861a', L: '#ffe27a' },
  diamond: { H: '#3fd7d1', h: '#1f9a98', L: '#9ff7f2' },
  netherite: { H: '#524a4f', h: '#2f292d', L: '#766d73' },
  leather: { H: '#a8632f', h: '#6b3e1b', L: '#c9824a' },
  chainmail: { H: '#a5abb1', h: '#6c7278', L: '#cfd4d8' },
  neutro: { H: '#9a9a9a', h: '#666666', L: '#c4c4c4' },
}
const FIJOS = { s: '#7a5230', S: '#4e3320', w: '#f2f2f2', O: '#1b1208', B: '#6b3fa0', b: '#3e2266', P: '#e6d3a3', G: '#d3b5ff', T: '#3aa59d', t: '#1f6a66' }

const grid = () => Array.from({ length: N }, () => Array(N).fill('.'))
const put = (g, x, y, c) => { if (x >= 0 && x < N && y >= 0 && y < N) g[y][x] = c }
const rect = (g, x, y, w, h, c) => { for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) put(g, x + i, y + j, c) }
function line(g, x0, y0, x1, y1, c) {
  const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0)
  const sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1
  let err = dx + dy
  for (;;) {
    put(g, x0, y0, c)
    if (x0 === x1 && y0 === y1) break
    const e2 = 2 * err
    if (e2 >= dy) { err += dy; x0 += sx }
    if (e2 <= dx) { err += dx; y0 += sy }
  }
}
const cells = (g, c, list) => list.forEach(([x, y]) => put(g, x, y, c))

const FORMAS = {
  sword(g) {
    line(g, 2, 13, 5, 10, 's'); put(g, 1, 14, 'S')
    line(g, 3, 8, 7, 12, 'S')
    line(g, 6, 9, 14, 1, 'H'); line(g, 7, 9, 14, 2, 'h'); line(g, 6, 8, 13, 1, 'L'); put(g, 15, 0, 'L')
  },
  axe(g) {
    line(g, 3, 14, 11, 6, 's'); put(g, 2, 15, 'S')
    const fila = (y, x0, x1) => rect(g, x0, y, x1 - x0 + 1, 1, 'H')
    fila(1, 10, 12); fila(2, 9, 13); fila(3, 8, 14); fila(4, 8, 14); fila(5, 9, 13); fila(6, 11, 12)
    rect(g, 10, 1, 2, 1, 'L'); rect(g, 9, 2, 2, 1, 'L'); rect(g, 8, 3, 2, 1, 'L'); rect(g, 8, 4, 1, 1, 'L')
    rect(g, 14, 3, 1, 2, 'h'); rect(g, 13, 2, 1, 1, 'h'); rect(g, 13, 5, 1, 1, 'h'); rect(g, 9, 5, 4, 1, 'h')
  },
  pickaxe(g) {
    line(g, 3, 14, 11, 6, 's'); put(g, 2, 15, 'S')
    line(g, 5, 3, 13, 11, 'H'); line(g, 6, 3, 13, 10, 'h')
    cells(g, 'H', [[4, 4], [14, 12]]); cells(g, 'L', [[5, 3], [6, 4], [7, 5]])
  },
  shovel(g) {
    line(g, 2, 15, 10, 7, 's')
    const fila = (y, x0, x1) => rect(g, x0, y, x1 - x0 + 1, 1, 'H')
    fila(0, 12, 14); fila(1, 11, 15); fila(2, 11, 15); fila(3, 11, 15); fila(4, 12, 14); fila(5, 11, 12); fila(6, 10, 11)
    rect(g, 12, 0, 2, 1, 'L'); rect(g, 11, 1, 2, 1, 'L'); rect(g, 11, 2, 1, 2, 'L')
    rect(g, 15, 1, 1, 3, 'h'); rect(g, 14, 4, 1, 1, 'h'); rect(g, 13, 3, 2, 1, 'h')
  },
  hoe(g) {
    line(g, 3, 14, 11, 6, 's'); put(g, 2, 15, 'S')
    rect(g, 6, 2, 8, 2, 'H'); rect(g, 6, 4, 2, 3, 'H')
    rect(g, 6, 2, 8, 1, 'L'); rect(g, 8, 3, 6, 1, 'h'); rect(g, 7, 4, 1, 3, 'h'); rect(g, 6, 6, 2, 1, 'h')
  },
  helmet(g) {
    rect(g, 4, 3, 8, 1, 'H'); rect(g, 3, 4, 10, 3, 'H')
    rect(g, 3, 7, 3, 4, 'H'); rect(g, 10, 7, 3, 4, 'H')
    rect(g, 3, 4, 10, 1, 'L'); rect(g, 12, 5, 1, 6, 'h'); rect(g, 3, 10, 3, 1, 'h'); rect(g, 10, 10, 2, 1, 'h')
    rect(g, 4, 7, 1, 1, 'h')
  },
  chestplate(g) {
    rect(g, 1, 2, 4, 4, 'H'); rect(g, 11, 2, 4, 4, 'H')
    rect(g, 3, 3, 10, 2, 'H'); rect(g, 4, 5, 8, 8, 'H')
    rect(g, 6, 2, 4, 2, '.')
    rect(g, 1, 2, 4, 1, 'L'); rect(g, 11, 2, 4, 1, 'L'); rect(g, 4, 5, 8, 1, 'L')
    rect(g, 11, 6, 1, 7, 'h'); rect(g, 4, 12, 8, 1, 'h'); rect(g, 14, 3, 1, 3, 'h'); rect(g, 7, 6, 2, 5, 'h')
  },
  leggings(g) {
    rect(g, 3, 2, 10, 4, 'H'); rect(g, 3, 6, 4, 8, 'H'); rect(g, 9, 6, 4, 8, 'H')
    rect(g, 3, 2, 10, 1, 'L'); rect(g, 6, 6, 1, 8, 'h'); rect(g, 12, 3, 1, 11, 'h'); rect(g, 3, 13, 4, 1, 'h'); rect(g, 9, 13, 3, 1, 'h')
    rect(g, 7, 2, 2, 1, 'h')
  },
  boots(g) {
    rect(g, 2, 3, 4, 6, 'H'); rect(g, 1, 9, 6, 4, 'H')
    rect(g, 10, 3, 4, 6, 'H'); rect(g, 9, 9, 6, 4, 'H')
    rect(g, 2, 3, 4, 1, 'L'); rect(g, 10, 3, 4, 1, 'L')
    rect(g, 5, 4, 1, 5, 'h'); rect(g, 13, 4, 1, 5, 'h'); rect(g, 1, 12, 6, 1, 'h'); rect(g, 9, 12, 6, 1, 'h')
  },
  bow(g) {
    cells(g, 's', [[8, 1], [9, 1], [10, 2], [11, 3], [12, 4], [12, 5], [12, 6], [12, 7], [12, 8], [12, 9], [12, 10], [11, 11], [10, 12], [9, 13], [8, 13]])
    cells(g, 'S', [[11, 4], [11, 10]])
    line(g, 8, 2, 8, 12, 'w')
    put(g, 7, 1, 'S'); put(g, 7, 13, 'S')
  },
  crossbow(g) {
    line(g, 2, 8, 13, 8, 's'); line(g, 2, 9, 9, 9, 'S')
    rect(g, 12, 2, 2, 13, 's'); rect(g, 13, 3, 1, 11, 'S')
    line(g, 12, 3, 5, 8, 'w'); line(g, 12, 13, 5, 8, 'w')
    rect(g, 2, 6, 2, 3, 'S')
  },
  fishing_rod(g) {
    line(g, 2, 14, 12, 4, 's'); put(g, 1, 15, 'S')
    line(g, 13, 4, 14, 11, 'w'); put(g, 14, 12, 'H'); put(g, 13, 13, 'H'); put(g, 12, 13, 'H')
    cells(g, 'S', [[12, 3], [11, 4]])
  },
  trident(g) {
    line(g, 2, 14, 10, 6, 's'); put(g, 1, 15, 'S')
    line(g, 7, 3, 12, 8, 'T')
    line(g, 8, 4, 8, 1, 'T'); line(g, 12, 8, 15, 8, 'T'); line(g, 10, 6, 14, 2, 'T')
    put(g, 8, 0, 'T'); put(g, 15, 7, 'T'); put(g, 15, 1, 'T')
    cells(g, 't', [[9, 5], [10, 7], [11, 6]])
  },
  book(g) {
    rect(g, 3, 2, 10, 12, 'B'); rect(g, 3, 2, 2, 12, 'b'); rect(g, 12, 3, 1, 10, 'P'); rect(g, 4, 13, 9, 1, 'b')
    cells(g, 'G', [[7, 5], [8, 4], [8, 6], [9, 5], [8, 5], [10, 9], [6, 10]])
    rect(g, 3, 2, 10, 1, 'G')
  },
}

export const TIPOS_ICONO = Object.keys(FORMAS)

/** Devuelve la lista de píxeles [{x, y, fill}] del icono. */
export function pixeles(forma, material = 'neutro') {
  const g = grid()
  FORMAS[forma](g)
  const paleta = { ...(MATERIALES[material] || MATERIALES.neutro), ...FIJOS }
  const out = []
  const lleno = (x, y) => x >= 0 && x < N && y >= 0 && y < N && g[y][x] !== '.'
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      let c = g[y][x]
      if (c === '.') {
        // contorno oscuro alrededor de la silueta
        if (lleno(x - 1, y) || lleno(x + 1, y) || lleno(x, y - 1) || lleno(x, y + 1)) out.push({ x, y, fill: paleta.O })
        continue
      }
      if (material === 'chainmail' && 'HL'.includes(c) && (x + y) % 2) c = 'h'
      out.push({ x, y, fill: paleta[c] })
    }
  }
  return out
}
