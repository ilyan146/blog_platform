import { useParams } from "react-router-dom"
import { usePost } from "../hooks/usePosts"
import { Markdown } from "../components/Markdown"

export function PostPage() {
  const { slug } = useParams()
  const { post, error } = usePost(slug!)

  if (error) return <p className="error">{error}</p>
  if (!post) return <p>Loading…</p>

  return (
    <article className="stack">
      <h1>{post.title}</h1>
      <p className="muted">{post.reading_time_minutes} min read</p>
      <Markdown source={post.body_markdown} />
    </article>
  )
}
