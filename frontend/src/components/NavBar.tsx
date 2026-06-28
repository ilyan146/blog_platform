import { Link } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"

export function NavBar() {
  const { user, logout } = useAuth()
  return (
    <nav className="nav">
      <Link to="/" className="brand">
        AI Blog Platform
      </Link>
      <div className="nav-links">
        {user ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <button className="link-btn" onClick={logout}>
              Log out ({user.display_name})
            </button>
          </>
        ) : (
          <Link to="/login">Log in</Link>
        )}
      </div>
    </nav>
  )
}
