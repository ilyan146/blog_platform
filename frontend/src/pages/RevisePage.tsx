import { useMutation } from "@tanstack/react-query"
import { useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { saveRevisionAsDraftMutation } from "../client/@tanstack/react-query.gen"
import { getErrorMessage } from "../lib/apiErrors"
import {
  streamRevision,
  type RevisionDoneEvent,
  type RevisionProgressEvent,
} from "../lib/reviseStream"

export function RevisePage() {
  const navigate = useNavigate()
  const [draftText, setDraftText] = useState("")
  const [progress, setProgress] = useState<RevisionProgressEvent[]>([])
  const [result, setResult] = useState<RevisionDoneEvent | null>(null)
  const [streamError, setStreamError] = useState<string | null>(null)
  const [streaming, setStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const saveMutation = useMutation({
    ...saveRevisionAsDraftMutation(),
    onSuccess: (draft) => navigate(`/drafts/${draft.id}`),
  })

  async function handleRevise() {
    setProgress([])
    setResult(null)
    setStreamError(null)
    setStreaming(true)
    const controller = new AbortController()
    abortRef.current = controller
    try {
      await streamRevision(
        draftText,
        (event) => {
          if (event.type === "done") setResult(event)
          else if (event.type === "error") setStreamError(event.message)
          else setProgress((prev) => [...prev, event])
        },
        controller.signal,
      )
    } catch (err) {
      setStreamError(getErrorMessage(err))
    } finally {
      setStreaming(false)
    }
  }

  function handleInsertIntoEditor() {
    if (result) setDraftText(result.body_markdown)
  }

  return (
    <div className="stack">
      <h1>Revise your draft into a 5-minute read</h1>
      <p className="muted">
        Paste your own draft below. Drop in links for the agent to research as
        context — it'll rework your draft into a polished 5-minute read.
      </p>

      <div className="split">
        <div className="card stack">
          <label>
            Your draft
            <textarea
              rows={22}
              value={draftText}
              onChange={(e) => setDraftText(e.target.value)}
              placeholder="Write or paste your draft here. Include links like https://... for context."
            />
          </label>
          <button onClick={handleRevise} disabled={streaming || draftText.trim().length === 0}>
            {streaming ? "Revising…" : "Revise with AI"}
          </button>
        </div>

        <div className="card stack">
          <h3>Agent progress</h3>
          {progress.length === 0 && !streaming && (
            <p className="muted">Progress will appear here once you click "Revise with AI".</p>
          )}
          <ul className="list">
            {progress.map((event, i) => (
              <li key={i} className="list-item">
                <span>
                  {event.type === "tool_call" ? "🔎" : "✓"} {event.tool}
                </span>
                {event.detail && <span className="muted">{event.detail}</span>}
              </li>
            ))}
          </ul>

          {streamError && <p className="error">{streamError}</p>}

          {result && (
            <div className="stack">
              <h4>{result.title}</h4>
              <p className="muted">
                {result.reading_time_minutes} min read · {result.tags.join(", ")}
              </p>
              <p>{result.excerpt}</p>
              <div className="row">
                <button className="secondary" onClick={handleInsertIntoEditor}>
                  Insert into editor
                </button>
                <button
                  disabled={saveMutation.isPending}
                  onClick={() =>
                    saveMutation.mutate({
                      body: {
                        title: result.title,
                        excerpt: result.excerpt,
                        body_markdown: result.body_markdown,
                        tags: result.tags,
                      },
                    })
                  }
                >
                  {saveMutation.isPending ? "Saving…" : "Save as draft"}
                </button>
              </div>
              {saveMutation.error && (
                <p className="error">{getErrorMessage(saveMutation.error)}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
