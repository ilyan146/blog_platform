import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import {
  editDraftMutation,
  generateDraftMutation,
  getDraftOptions,
  getDraftQueryKey,
  listDraftsQueryKey,
  listPostsQueryKey,
  publishDraftMutation,
} from "../client/@tanstack/react-query.gen"
import { getErrorMessage } from "../client/errors"
import { StatusBadge } from "../components/StatusBadge"

export function DraftPage() {
  const { id } = useParams()
  const draftId = Number(id)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const {
    isPending,
    error,
    data: draft,
  } = useQuery(getDraftOptions({ path: { draft_id: draftId } }))

  const generateMutation = useMutation({
    ...generateDraftMutation(),
    onSuccess: (d) =>
      queryClient.setQueryData(getDraftQueryKey({ path: { draft_id: draftId } }), d),
  })

  const saveMutation = useMutation({
    ...editDraftMutation(),
    onSuccess: (d) =>
      queryClient.setQueryData(getDraftQueryKey({ path: { draft_id: draftId } }), d),
  })

  const publishMutation = useMutation({
    ...publishDraftMutation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: listDraftsQueryKey() })
      queryClient.invalidateQueries({ queryKey: listPostsQueryKey() })
    },
  })

  const busy =
    generateMutation.isPending ||
    saveMutation.isPending ||
    publishMutation.isPending
  const mutationError =
    generateMutation.error ?? saveMutation.error ?? publishMutation.error

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

  if (isPending) return <p>Loading…</p>

  if (error)
    return <p className="error">An error has occurred: {getErrorMessage(error)}</p>

  const hasContent = draft.status === "ready" || draft.status === "published"

  async function handlePublish() {
    try {
      const post = await publishMutation.mutateAsync({
        path: { draft_id: draftId },
      })
      navigate(`/posts/${post.slug}`)
    } catch {
      // surfaced via publishMutation.error below
    }
  }

  return (
    <div className="stack">
      <div className="row between">
        <h1>{draft.topic}</h1>
        <StatusBadge status={draft.status} />
      </div>

      {mutationError && (
        <p className="error">{getErrorMessage(mutationError)}</p>
      )}

      {!hasContent && (
        <div className="card">
          <p className="muted">
            Tone: {draft.tone} · Audience: {draft.audience}
          </p>
          <button
            onClick={() => generateMutation.mutate({ path: { draft_id: draftId } })}
            disabled={busy}
          >
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
                saveMutation.mutate({
                  path: { draft_id: draftId },
                  body: {
                    title,
                    excerpt,
                    body_markdown: body,
                    tags: draft.tags,
                  },
                })
              }
            >
              Save edits
            </button>
            <button
              onClick={() => generateMutation.mutate({ path: { draft_id: draftId } })}
              className="secondary"
              disabled={busy}
            >
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
