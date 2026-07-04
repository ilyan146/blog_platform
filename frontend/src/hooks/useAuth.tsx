import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react"
import { login, me, register } from "../client"
import type { TokenResponse, UserPublic } from "../client"
import { tokenStore } from "../client/setup"

interface AuthState {
  user: UserPublic | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (
    email: string,
    displayName: string,
    password: string,
  ) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserPublic | null>(null)
  const [loading, setLoading] = useState(true)

  // Restore session on first load if a token is present.
  useEffect(() => {
    if (!tokenStore.get()) {
      setLoading(false)
      return
    }
    me({ throwOnError: true })
      .then(({ data }) => setUser(data))
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false))
  }, [])

  async function handle(response: Promise<{ data: TokenResponse }>) {
    const { data } = await response
    tokenStore.set(data.access_token)
    setUser(data.user)
  }

  const value: AuthState = {
    user,
    loading,
    login: (email, password) =>
      handle(login({ body: { email, password }, throwOnError: true })),
    register: (email, display_name, password) =>
      handle(
        register({
          body: { email, display_name, password },
          throwOnError: true,
        }),
      ),
    logout: () => {
      tokenStore.clear()
      setUser(null)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
