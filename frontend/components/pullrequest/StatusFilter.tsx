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
      className="rounded-lg border border-gray-300 bg-white px-4 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <option value="all">All Pull Requests</option>
      <option value="open">Open</option>
      <option value="closed">Closed</option>
      <option value="reviewed">Reviewed</option>
      <option value="unreviewed">Not Reviewed</option>
    </select>
  );
}