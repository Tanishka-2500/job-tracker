const BASE_URL = 'http://localhost:8000/api'

async function req(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json()
}

export const jobsAPI = {
  getAll: (filters = {}) => {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') params.append(k, v)
    })
    return req(`/jobs?${params}`)
  },
  get: (id) => req(`/jobs/${id}`),
  update: (id, data) => req(`/jobs/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => req(`/jobs/${id}`, { method: 'DELETE' }),
}

export const rolesAPI = {
  getAll: () => req('/roles'),
  create: (data) => req('/roles', { method: 'POST', body: JSON.stringify(data) }),
  toggle: (id) => req(`/roles/${id}`, { method: 'PATCH' }),
  delete: (id) => req(`/roles/${id}`, { method: 'DELETE' }),
}

export const statsAPI = {
  get: () => req('/stats'),
}

export const scrapeAPI = {
  trigger: () => req('/scrape', { method: 'POST' }),
  status: () => req('/scrape/status'),
}
