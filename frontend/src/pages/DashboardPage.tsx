import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { api } from "../api"
import { queryKeys } from "../queryKeys"
import { StatusBadge } from "../components/StatusBadge"
import type { Draft, DraftCreate } from "../types"

export function DashboardPage() {
  const queryClient = useQueryClient()
  const {
    isPending,
    error,
    data: drafts = [],
  } = useQuery({
    queryKey: queryKeys.drafts,
    queryFn: () => api.get<Draft[]>("/api/drafts"),
  })
  const createDraft = useMutation({
    mutationFn: (input: DraftCreate) => api.post<Draft>("/api/drafts", input),
    onSuccess: (draft) =>
      queryClient.setQueryData<Draft[]>(queryKeys.drafts, (prev) => [
        draft,
        ...(prev ?? []),
      ]),
  })
  const navigate = useNavigate()
  const [topic, setTopic] = useState("")
  const [tone, setTone] = useState("conversational")
  const [busy, setBusy] = useState(false)

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    try {
      const draft = await createDraft.mutateAsync({ topic, tone })
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
      {isPending ? (
        <p>Loading…</p>
      ) : error ? (
        <p className="error">An error has occurred: {error.message}</p>
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
