import { useCallback, useEffect, useState } from "react"
import { api } from "../api"
import type { Draft, DraftCreate } from "../types"

/** Owns the list of the current user's drafts and the create/generate actions. */
export function useDrafts() {
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      setDrafts(await api.get<Draft[]>("/api/drafts"))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  async function create(input: DraftCreate): Promise<Draft> {
    const draft = await api.post<Draft>("/api/drafts", input)
    setDrafts((prev) => [draft, ...prev])
    return draft
  }

  return { drafts, loading, error, refresh, create }
}

/** Owns a single draft and the generate/edit/publish actions on it. */
export function useDraft(id: number) {
  const [draft, setDraft] = useState<Draft | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .get<Draft>(`/api/drafts/${id}`)
      .then(setDraft)
      .catch((e) => setError((e as Error).message))
  }, [id])

  async function run<T>(fn: () => Promise<T>): Promise<T | undefined> {
    setBusy(true)
    setError(null)
    try {
      return await fn()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  const generate = () =>
    run(async () =>
      setDraft(await api.post<Draft>(`/api/drafts/${id}/generate`)),
    )

  const save = (body: {
    title: string
    excerpt: string
    body_markdown: string
    tags: string[]
  }) => run(async () => setDraft(await api.put<Draft>(`/api/drafts/${id}`, body)))

  const publish = () =>
    run(async () => {
      const post = await api.post<{ slug: string }>(`/api/drafts/${id}/publish`)
      return post.slug
    })

  return { draft, busy, error, generate, save, publish }
}
