import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useDrafts } from "../hooks/useDrafts"
import { StatusBadge } from "../components/StatusBadge"

export function DashboardPage() {
  const { drafts, loading, create } = useDrafts()
  const navigate = useNavigate()
  const [topic, setTopic] = useState("")
  const [tone, setTone] = useState("conversational")
  const [busy, setBusy] = useState(false)

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    try {
      const draft = await create({ topic, tone })
      navigate(`/drafts/${draft.id}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="stack">
      <div className="card">
        <h2>Start a new post</h2>
        <form onSubmit={handleCreate} className="form row">
          <input
            placeholder="What should the post be about?"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            required
            minLength={3}
          />
          <select value={tone} onChange={(e) => setTone(e.target.value)}>
            <option value="conversational">Conversational</option>
            <option value="professional">Professional</option>
            <option value="technical">Technical</option>
            <option value="storytelling">Storytelling</option>
          </select>
          <button disabled={busy}>{busy ? "..." : "Create"}</button>
        </form>
      </div>

      <h2>Your drafts</h2>
      {loading ? (
        <p>Loading…</p>
      ) : drafts.length === 0 ? (
        <p className="muted">No drafts yet. Create one above.</p>
      ) : (
        <ul className="list">
          {drafts.map((d) => (
            <li key={d.id}>
              <Link to={`/drafts/${d.id}`} className="list-item">
                <span>{d.title ?? d.topic}</span>
                <StatusBadge status={d.status} />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
