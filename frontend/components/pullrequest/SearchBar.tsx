"use client";

import { Search } from "lucide-react";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function SearchBar({
  value,
  onChange,
}: Props) {
  return (
    <div className="flex items-center rounded-xl border bg-white px-4 py-3 shadow">

      <Search
        size={18}
        className="text-gray-400"
      />

      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search by title, author or repository..."
        className="ml-3 w-full outline-none"
      />

    </div>
  );
}