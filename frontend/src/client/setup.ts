/** Hand-written (not generated): wires the generated client's base URL + auth token. */
import { client } from "./client.gen"

const TOKEN_KEY = "blog_token"

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

client.setConfig({
  baseUrl: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  auth: () => tokenStore.get() ?? undefined,
})
