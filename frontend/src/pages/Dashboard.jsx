
import { useEffect, useState } from "react"
import { listStudents, listJobs, recommend, sendFeedback } from "../api"

export default function Dashboard(){
  const [students,setStudents] = useState([])
  const [jobs,setJobs] = useState([])
  const [studentUid,setStudentUid] = useState("S1")
  const [clientId,setClientId] = useState("client_U1")
  const [items,setItems] = useState([])
  const [msg,setMsg] = useState("")

  useEffect(()=>{
    listStudents().then(setStudents).catch(()=>{})
    listJobs().then(setJobs).catch(()=>{})
  },[])

  async function onRec(){
    setMsg("")
    const data = await recommend(clientId, studentUid, 5)
    setItems(data)
  }

  async function onLike(job_uid, liked){
    await sendFeedback(studentUid, job_uid, liked, liked ? "liked" : "not matched")
    setMsg(`Feedback saved for ${job_uid}`)
  }

  return (
    <div className="grid grid-cols-1 gap-6">
      <div className="bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-2">Get Recommendations</h3>
        <div className="flex gap-3">
          <input className="border p-2" value={clientId} onChange={e=>setClientId(e.target.value)} placeholder="client id (e.g., client_U1)"/>
          <input className="border p-2" value={studentUid} onChange={e=>setStudentUid(e.target.value)} placeholder="student uid (e.g., S1)" />
          <button className="bg-green-600 text-white px-3 rounded" onClick={onRec}>Recommend</button>
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow">
        <h3 className="font-semibold mb-3">Results</h3>
        {items.length === 0 && <p className="text-sm">No results yet.</p>}
        <div className="space-y-3">
          {items.map(it => (
            <div key={it.job_uid} className="border p-3 rounded">
              <div className="font-semibold">{it.role} @ {it.company}</div>
              <div className="text-sm">Skills: {it.required_skills}</div>
              <div className="text-sm">Salary: {it.salary_min} – {it.salary_max}</div>
              <div className="text-sm">Score: {it.score.toFixed(3)}</div>
              <div className="mt-2 space-x-2">
                <button className="bg-blue-600 text-white px-2 py-1 rounded" onClick={()=>onLike(it.job_uid, true)}>Like</button>
                <button className="bg-gray-600 text-white px-2 py-1 rounded" onClick={()=>onLike(it.job_uid, false)}>Skip</button>
              </div>
            </div>
          ))}
        </div>
        {msg && <div className="mt-2 text-green-700 text-sm">{msg}</div>}
      </div>
    </div>
  )
}
