
import { Routes, Route, Link, useNavigate } from "react-router-dom"
import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"

export default function App(){
  return (
    <div className="max-w-5xl mx-auto p-6">
      <nav className="flex justify-between mb-6">
        <h1 className="text-2xl font-bold">Smart Internship Engine</h1>
        <div className="space-x-4">
          <Link to="/" className="underline">Login</Link>
          <Link to="/dashboard" className="underline">Dashboard</Link>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<Login/>} />
        <Route path="/dashboard" element={<Dashboard/>} />
      </Routes>
    </div>
  )
}
