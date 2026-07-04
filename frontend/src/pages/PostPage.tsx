import { useQuery } from "@tanstack/react-query"
import { useParams } from "react-router-dom"
import { api } from "../api"
import { queryKeys } from "../queryKeys"
import { Markdown } from "../components/Markdown"
import type { Post } from "../types"

export function PostPage() {
  const { slug } = useParams()
  const { isPending, error, data: post } = useQuery({
    queryKey: queryKeys.post(slug!),
    queryFn: () => api.get<Post>(`/api/posts/${slug}`),
    enabled: !!slug,
  })

  if (isPending) return <p>Loading…</p>

  if (error) return <p className="error">An error has occurred: {error.message}</p>

  return (
    <article className="stack">
      <h1>{post.title}</h1>
      <p className="muted">{post.reading_time_minutes} min read</p>
      <Markdown source={post.body_markdown} />
    </article>
  )
}
