import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Outlet } from "react-router-dom"
import { NavBar } from "./components/NavBar"

const queryClient = new QueryClient()

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <NavBar />
      <main className="container">
        <Outlet />
      </main>
    </QueryClientProvider>
  )
}
