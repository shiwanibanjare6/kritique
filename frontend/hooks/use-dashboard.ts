"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { PullRequest } from "@/types";

export function useDashboard() {
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getPullRequests();
        setPullRequests(data);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return {
    pullRequests,
    loading,
  };
}