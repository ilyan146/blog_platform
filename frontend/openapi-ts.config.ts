import { defineConfig } from "@hey-api/openapi-ts"

// Generates a typed API client + TanStack Query options from the backend's
// OpenAPI schema. Regenerate after backend contract changes with:
//   uv run --package blog-platform-backend python backend/scripts/export_openapi.py
//   npm run generate-client
export default defineConfig({
  input: "./openapi.json",
  output: "src/client",
  plugins: [
    "@hey-api/client-fetch",
    "@hey-api/typescript",
    "@hey-api/sdk",
    "@tanstack/react-query",
  ],
})
