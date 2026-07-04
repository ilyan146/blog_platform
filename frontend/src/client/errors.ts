/** Hand-written (not generated): extracts a readable message from an error
 * thrown by the generated API client (which throws the parsed JSON error body,
 * not an `Error` instance — see client/client.gen.ts's `throw jsonError ?? textError`).
 */
export function getErrorMessage(error: unknown): string {
  if (error && typeof error === "object" && "detail" in error) {
    const { detail } = error as { detail: unknown }
    if (typeof detail === "string") return detail
    if (Array.isArray(detail)) {
      return detail
        .map((d) =>
          d && typeof d === "object" && "msg" in d ? String(d.msg) : String(d),
        )
        .join(", ")
    }
  }
  if (error instanceof Error) return error.message
  return "Something went wrong."
}
