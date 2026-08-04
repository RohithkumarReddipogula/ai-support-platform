import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

export const documentsAPI = {
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/documents/upload', form)
  },
  list: () => api.get('/documents'),
  delete: (id) => api.delete(`/documents/${id}`),
}

export const chatAPI = {
  send: (message, sessionId) =>
    api.post('/chat', { message, session_id: sessionId || null }),
  history: (sessionId) => api.get(`/chat/history/${sessionId}`),
}

export default api