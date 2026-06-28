import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useDraft } from "../hooks/useDrafts"
import { StatusBadge } from "../components/StatusBadge"

export function DraftPage() {
  const { id } = useParams()
  const draftId = Number(id)
  const navigate = useNavigate()
  const { draft, busy, error, generate, save, publish } = useDraft(draftId)

  // Local editable copy of the generated content.
  const [title, setTitle] = useState("")
  const [excerpt, setExcerpt] = useState("")
  const [body, setBody] = useState("")

  useEffect(() => {
    if (draft?.status === "ready" || draft?.status === "published") {
      setTitle(draft.title ?? "")
      setExcerpt(draft.excerpt ?? "")
      setBody(draft.body_markdown ?? "")
    }
  }, [draft])

  if (!draft) return <p>{error ?? "Loading…"}</p>

  const hasContent = draft.status === "ready" || draft.status === "published"

  async function handlePublish() {
    const slug = await publish()
    if (slug) navigate(`/posts/${slug}`)
  }

  return (
    <div className="stack">
      <div className="row between">
        <h1>{draft.topic}</h1>
        <StatusBadge status={draft.status} />
      </div>

      {error && <p className="error">{error}</p>}

      {!hasContent && (
        <div className="card">
          <p className="muted">
            Tone: {draft.tone} · Audience: {draft.audience}
          </p>
          <button onClick={generate} disabled={busy}>
            {busy ? "Writing your 5-minute read…" : "Generate with AI"}
          </button>
          {draft.status === "failed" && (
            <p className="error">Generation failed: {draft.error}</p>
          )}
        </div>
      )}

      {hasContent && (
        <div className="card stack">
          <label>
            Title
            <input value={title} onChange={(e) => setTitle(e.target.value)} />
          </label>
          <label>
            Excerpt
            <textarea
              rows={2}
              value={excerpt}
              onChange={(e) => setExcerpt(e.target.value)}
            />
          </label>
          <label>
            Body (Markdown) · ~{draft.reading_time_minutes} min read
            <textarea
              rows={20}
              value={body}
              onChange={(e) => setBody(e.target.value)}
            />
          </label>
          <div className="row">
            <button
              className="secondary"
              disabled={busy}
              onClick={() =>
                save({ title, excerpt, body_markdown: body, tags: draft.tags })
              }
            >
              Save edits
            </button>
            <button onClick={generate} className="secondary" disabled={busy}>
              Regenerate
            </button>
            {draft.status !== "published" && (
              <button onClick={handlePublish} disabled={busy}>
                Publish
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
