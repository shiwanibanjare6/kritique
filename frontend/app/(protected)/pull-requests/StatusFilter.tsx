"use client";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function StatusFilter({
  value,
  onChange,
}: Props) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-lg border bg-white px-4 py-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <option value="all">All PRs</option>
      <option value="open">Open</option>
      <option value="closed">Closed</option>
      <option value="reviewed">Reviewed</option>
      <option value="unreviewed">Not Reviewed</option>
    </select>
  );
}