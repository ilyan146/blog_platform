import { Link } from "react-router-dom"
import { usePosts } from "../hooks/usePosts"

export function HomePage() {
  const { posts, loading } = usePosts()

  return (
    <div className="stack">
      <h1>Latest posts</h1>
      {loading ? (
        <p>Loading…</p>
      ) : posts.length === 0 ? (
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
