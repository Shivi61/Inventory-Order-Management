import axios from 'axios'

// The backend URL is provided at build time. Defaults to localhost for dev.
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL })

// Pull the most useful message out of a FastAPI error response.
export function errorMessage(err) {
  const detail = err?.response?.data?.detail
  if (Array.isArray(detail)) {
    // Pydantic validation errors come back as a list.
    return detail.map((d) => d.msg).join(', ')
  }
  return detail || err.message || 'Something went wrong'
}

export default api
