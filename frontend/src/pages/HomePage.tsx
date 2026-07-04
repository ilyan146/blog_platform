import { useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { listPostsOptions } from "../client/@tanstack/react-query.gen"
import { getErrorMessage } from "../client/errors"

export function HomePage() {
  const { isPending, error, data: posts = [] } = useQuery(listPostsOptions())

  if (isPending) return <p>Loading…</p>

  if (error)
    return <p className="error">An error has occurred: {getErrorMessage(error)}</p>

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
