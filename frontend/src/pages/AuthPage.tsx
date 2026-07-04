import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { getErrorMessage } from "../lib/apiErrors"
import { useAuth } from "../hooks/useAuth"

export function AuthPage() {
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState<"login" | "register">("login")
  const [email, setEmail] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      if (mode === "login") await login(email, password)
      else await register(email, displayName, password)
      navigate("/dashboard")
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card narrow">
      <h1>{mode === "login" ? "Log in" : "Create account"}</h1>
      <form onSubmit={handleSubmit} className="form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        {mode === "register" && (
          <input
            placeholder="Display name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
          />
        )}
        <input
          type="password"
          placeholder="Password (min 8 chars)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="error">{error}</p>}
        <button disabled={busy}>
          {busy ? "..." : mode === "login" ? "Log in" : "Sign up"}
        </button>
      </form>
      <button
        className="link-btn"
        onClick={() => setMode(mode === "login" ? "register" : "login")}
      >
        {mode === "login"
          ? "Need an account? Sign up"
          : "Have an account? Log in"}
      </button>
    </div>
  )
}
