import React from "react"
import ReactDOM from "react-dom/client"
import { createBrowserRouter, RouterProvider } from "react-router-dom"
import { App } from "./App"
import "./client/setup"
import { AuthProvider } from "./hooks/useAuth"
import { ProtectedRoute } from "./components/ProtectedRoute"
import { AuthPage } from "./pages/AuthPage"
import { DashboardPage } from "./pages/DashboardPage"
import { DraftPage } from "./pages/DraftPage"
import { HomePage } from "./pages/HomePage"
import { PostPage } from "./pages/PostPage"
import "./styles.css"

const router = createBrowserRouter([
  {
    element: <App />,
    children: [
      { path: "/", element: <HomePage /> },
      { path: "/login", element: <AuthPage /> },
      { path: "/posts/:slug", element: <PostPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: "/dashboard", element: <DashboardPage /> },
          { path: "/drafts/:id", element: <DraftPage /> },
        ],
      },
    ],
  },
])

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </React.StrictMode>,
)
