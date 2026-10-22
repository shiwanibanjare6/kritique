"use client";

import { useEffect } from "react";

export function BackendWarmup() {
  useEffect(() => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!baseUrl) return;

    void fetch(`${baseUrl.replace(/\/$/, "")}/health`, {
      mode: "no-cors",
      keepalive: true,
    }).catch(() => undefined);
  }, []);

  return null;
}
