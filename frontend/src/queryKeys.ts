/** Centralized React Query cache keys, so invalidation stays consistent across pages. */
export const queryKeys = {
  posts: ["posts"] as const,
  post: (slug: string) => ["posts", slug] as const,
  drafts: ["drafts"] as const,
  draft: (id: number) => ["drafts", id] as const,
}
