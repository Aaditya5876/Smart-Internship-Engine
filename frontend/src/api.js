
import axios from "axios"
const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"

export async function login(email, password){
  const { data } = await axios.post(`${API}/auth/login`, { email, password })
  return data
}

export function setToken(tok){
  axios.defaults.headers.common["Authorization"] = `Bearer ${tok}`
}

export async function listStudents(){
  const { data } = await axios.get(`${API}/students/`)
  return data
}

export async function listJobs(){
  const { data } = await axios.get(`${API}/jobs/`)
  return data
}

export async function recommend(client_id, student_uid, top_k=5){
  const { data } = await axios.post(`${API}/recs/recommend`, { client_id, student_uid, top_k })
  return data
}

export async function sendFeedback(student_uid, job_uid, liked, notes=""){
  const { data } = await axios.post(`${API}/feedback/submit`, { student_uid, job_uid, liked, notes })
  return data
}
