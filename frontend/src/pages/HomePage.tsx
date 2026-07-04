import { useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { api } from "../api"
import { queryKeys } from "../queryKeys"
import type { PostSummary } from "../types"

export function HomePage() {
  const { isPending, error, data: posts = [] } = useQuery({
    queryKey: queryKeys.posts,
    queryFn: () => api.get<PostSummary[]>("/api/posts"),
  })

  if (isPending) return <p>Loading…</p>

  if (error) return <p className="error">An error has occurred: {error.message}</p>

  return (
    <div className="stack">
      <h1>Latest posts</h1>
      {posts.length === 0 ? (
        <p className="muted">No posts published yet.</p>
      ) : (
        <ul className="list">
          {posts.map((p) => (
            <li key={p.id}>
              <Link to={`/posts/${p.slug}`} className="post-card">
                <h3>{p.title}</h3>
                <p className="muted">{p.excerpt}</p>
                <small>{p.reading_time_minutes} min read</small>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
