/** Formats a score for display without changing its underlying value. */
export function formatScore(score: number): string {
  return Number.isInteger(score) ? String(score) : score.toFixed(2);
}
