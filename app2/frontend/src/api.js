const baseUrl = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

export async function processSelection(selection, token, signal) {
  const response = await fetch(`${baseUrl}/api/procesar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(selection),
    signal,
  })
  let data
  try {
    data = await response.json()
  } catch {
    throw new Error('No se ha recibido una respuesta utilizable. Puedes volver a intentarlo.')
  }
  if (!response.ok) {
    const message = data?.error?.mensaje
    throw new Error(typeof message === 'string' ? message : 'No se ha podido completar la consulta.')
  }
  if (!data?.resultado || !Array.isArray(data.resultado.pasos) || !Array.isArray(data.resultado.advertencias)) {
    throw new Error('La respuesta recibida no se puede mostrar.')
  }
  return data.resultado
}
