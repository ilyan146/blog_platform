import type { DraftStatus } from "../types"

const COLORS: Record<DraftStatus, string> = {
  pending: "#6b7280",
  generating: "#2563eb",
  ready: "#16a34a",
  failed: "#dc2626",
  published: "#7c3aed",
}

export function StatusBadge({ status }: { status: DraftStatus }) {
  return (
    <span
      style={{
        background: COLORS[status],
        color: "white",
        padding: "2px 10px",
        borderRadius: 999,
        fontSize: 12,
        textTransform: "capitalize",
      }}
    >
      {status}
    </span>
  )
}
