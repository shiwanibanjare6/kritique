"use client";

import { useEffect, useState } from "react";

export function SlowHint() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setVisible(true), 4_000);
    return () => window.clearTimeout(timer);
  }, []);

  if (!visible) return null;
  return (
    <p className="text-sm text-muted-foreground" role="status">
      Waking up the server, the first load can take up to 30 seconds
    </p>
  );
}
