/** Minimal, dependency-free Markdown rendering for the MVP.
 *  Renders the raw Markdown preserving whitespace. Swap for `react-markdown`
 *  later if rich rendering is needed. */
export function Markdown({ source }: { source: string }) {
  return <article className="markdown">{source}</article>
}
