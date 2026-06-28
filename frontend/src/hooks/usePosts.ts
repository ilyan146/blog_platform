import { useEffect, useState } from "react"
import { api } from "../api"
import type { Post, PostSummary } from "../types"

export function usePosts() {
  const [posts, setPosts] = useState<PostSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get<PostSummary[]>("/api/posts")
      .then(setPosts)
      .finally(() => setLoading(false))
  }, [])

  return { posts, loading }
}

export function usePost(slug: string) {
  const [post, setPost] = useState<Post | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .get<Post>(`/api/posts/${slug}`)
      .then(setPost)
      .catch((e) => setError((e as Error).message))
  }, [slug])

  return { post, error }
}
