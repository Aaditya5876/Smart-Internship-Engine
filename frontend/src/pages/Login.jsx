
import { useState } from "react"
import { login, setToken } from "../api"
import { useNavigate } from "react-router-dom"

export default function Login(){
  const nav = useNavigate()
  const [email,setEmail] = useState("student@thesis.local")
  const [password,setPassword] = useState("student123")
  const [err,setErr] = useState("")

  async function onSubmit(e){
    e.preventDefault()
    try{
      const t = await login(email,password)
      setToken(t.access_token)
      nav("/dashboard")
    }catch(e){
      setErr(String(e))
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Login</h2>
      <form onSubmit={onSubmit} className="space-y-3">
        <input className="w-full border p-2" value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
        <input className="w-full border p-2" value={password} type="password" onChange={e=>setPassword(e.target.value)} placeholder="password" />
        <button className="bg-blue-600 text-white px-4 py-2 rounded">Login</button>
        {err && <div className="text-red-600 text-sm">{err}</div>}
      </form>
      <p className="text-sm mt-3">Demo users: admin@thesis.local, uni@thesis.local, company@thesis.local, student@thesis.local</p>
    </div>
  )
}
