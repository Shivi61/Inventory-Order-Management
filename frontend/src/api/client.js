import axios from 'axios'

// The backend root is provided at build time. All routes live under /api/v1.
const root = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: `${root}/api/v1` })

// Pull the most useful message out of a backend error response.
export function errorMessage(err) {
  const data = err?.response?.data
  if (data?.message) return data.message
  const detail = data?.detail
  if (Array.isArray(detail)) {
    // Pydantic validation errors come back as a list.
    return detail.map((d) => d.msg).join(', ')
  }
  return detail || err.message || 'Something went wrong'
}

export default api
