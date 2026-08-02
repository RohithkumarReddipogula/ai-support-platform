import axios from 'axios'
const api=axios.create({baseURL:'http://localhost:8000/api/v1'})
api.interceptors.request.use((c)=>{const t=localStorage.getItem('token');if(t)c.headers.Authorization='Bearer '+t;return c})
api.interceptors.response.use(r=>r,e=>{if(e.response?.status===401){localStorage.removeItem('token');window.location.href='/login'}return Promise.reject(e)})
export const authAPI={register:d=>api.post('/auth/register',d),login:d=>api.post('/auth/login',d),me:()=>api.get('/auth/me')}
export const documentsAPI={upload:f=>{const fm=new FormData();fm.append('file',f);return api.post('/documents/upload',fm)},list:()=>api.get('/documents'),delete:id=>api.delete('/documents/'+id)}
export const chatAPI={send:(m,s)=>api.post('/chat',{message:m,session_id:s||null}),history:s=>api.get('/chat/history/'+s)}
export default api