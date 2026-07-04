import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { api } from "../api"
import { queryKeys } from "../queryKeys"
import { StatusBadge } from "../components/StatusBadge"
import type { Draft } from "../types"

export function DraftPage() {
  const { id } = useParams()
  const draftId = Number(id)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const {
    isPending,
    error,
    data: draft,
  } = useQuery({
    queryKey: queryKeys.draft(draftId),
    queryFn: () => api.get<Draft>(`/api/drafts/${draftId}`),
  })

  const generateMutation = useMutation({
    mutationFn: () => api.post<Draft>(`/api/drafts/${draftId}/generate`),
    onSuccess: (d) => queryClient.setQueryData(queryKeys.draft(draftId), d),
  })

  const saveMutation = useMutation({
    mutationFn: (body: {
      title: string
      excerpt: string
      body_markdown: string
      tags: string[]
    }) => api.put<Draft>(`/api/drafts/${draftId}`, body),
    onSuccess: (d) => queryClient.setQueryData(queryKeys.draft(draftId), d),
  })

  const publishMutation = useMutation({
    mutationFn: () =>
      api.post<{ slug: string }>(`/api/drafts/${draftId}/publish`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.drafts })
      queryClient.invalidateQueries({ queryKey: queryKeys.posts })
    },
  })

  const busy =
    generateMutation.isPending ||
    saveMutation.isPending ||
    publishMutation.isPending
  const mutationError = (generateMutation.error ??
    saveMutation.error ??
    publishMutation.error) as Error | null

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

  if (error) return <p className="error">An error has occurred: {error.message}</p>

  const hasContent = draft.status === "ready" || draft.status === "published"

  async function handlePublish() {
    try {
      const post = await publishMutation.mutateAsync()
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

      {mutationError && <p className="error">{mutationError.message}</p>}

      {!hasContent && (
        <div className="card">
          <p className="muted">
            Tone: {draft.tone} · Audience: {draft.audience}
          </p>
          <button onClick={() => generateMutation.mutate()} disabled={busy}>
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
                  title,
                  excerpt,
                  body_markdown: body,
                  tags: draft.tags,
                })
              }
            >
              Save edits
            </button>
            <button
              onClick={() => generateMutation.mutate()}
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
