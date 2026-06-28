export type DraftStatus =
  | "pending"
  | "generating"
  | "ready"
  | "failed"
  | "published"

export interface User {
  id: number
  email: string
  display_name: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Draft {
  id: number
  status: DraftStatus
  error: string | null
  topic: string
  audience: string
  tone: string
  key_points: string[]
  title: string | null
  excerpt: string | null
  body_markdown: string | null
  tags: string[]
  reading_time_minutes: number | null
  created_at: string
  updated_at: string
}

export interface DraftCreate {
  topic: string
  audience?: string
  tone?: string
  key_points?: string[]
}

export interface PostSummary {
  id: number
  slug: string
  title: string
  excerpt: string
  tags: string[]
  reading_time_minutes: number
  published_at: string
}

export interface Post extends PostSummary {
  body_markdown: string
}
