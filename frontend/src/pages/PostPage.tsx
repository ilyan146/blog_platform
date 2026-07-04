import { useQuery } from "@tanstack/react-query"
import { useParams } from "react-router-dom"
import { getPostOptions } from "../client/@tanstack/react-query.gen"
import { getErrorMessage } from "../lib/apiErrors"
import { Markdown } from "../components/Markdown"

export function PostPage() {
  const { slug } = useParams()
  const { isPending, error, data: post } = useQuery({
    ...getPostOptions({ path: { slug: slug! } }),
    enabled: !!slug,
  })

  if (isPending) return <p>Loading…</p>

  if (error)
    return <p className="error">An error has occurred: {getErrorMessage(error)}</p>

  return (
    <article className="stack">
      <h1>{post.title}</h1>
      <p className="muted">{post.reading_time_minutes} min read</p>
      <Markdown source={post.body_markdown} />
    </article>
  )
}
