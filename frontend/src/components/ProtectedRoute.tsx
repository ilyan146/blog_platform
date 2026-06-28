import { Navigate, Outlet } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"

/** Gate for authenticated-only routes. */
export function ProtectedRoute() {
  const { user, loading } = useAuth()
  if (loading) return <p style={{ padding: 24 }}>Loading…</p>
  return user ? <Outlet /> : <Navigate to="/login" replace />
}
