#!/usr/bin/env python3
"""Measure HTTP endpoint latency and response sizes using httpx only."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx


def percentile(values: list[float], percentile_value: float) -> float | None:
    """Return the nearest-rank percentile (p95 uses rank ceil(0.95 * n))."""
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percentile_value * len(ordered)) - 1)
    return ordered[index]


def endpoint_url(base_url: str, endpoint: str) -> str:
    if endpoint.startswith(("http://", "https://")):
        return endpoint
    return urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))


async def measure(client: httpx.AsyncClient, endpoint: str, runs: int) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    for _ in range(runs):
        started = time.perf_counter()
        try:
            response = await client.get(endpoint)
            duration_ms = (time.perf_counter() - started) * 1000
            response_bytes = len(response.content)
            samples.append(
                {
                    "status_code": response.status_code,
                    "latency_ms": round(duration_ms, 3),
                    "response_size_kb": round(response_bytes / 1024, 3),
                }
            )
        except httpx.HTTPError as error:
            duration_ms = (time.perf_counter() - started) * 1000
            samples.append(
                {
                    "error": type(error).__name__,
                    "latency_ms": round(duration_ms, 3),
                    "response_size_kb": None,
                }
            )

    latencies = [sample["latency_ms"] for sample in samples]
    sizes = [sample["response_size_kb"] for sample in samples if sample["response_size_kb"] is not None]
    return {
        "endpoint": endpoint,
        "runs": runs,
        "responses_received": len(sizes),
        "latency_ms": {
            "min": round(min(latencies), 3) if latencies else None,
            "median": round(statistics.median(latencies), 3) if latencies else None,
            "p95": round(percentile(latencies, 0.95), 3) if latencies else None,
        },
        "response_size_kb": {
            "min": round(min(sizes), 3) if sizes else None,
            "median": round(statistics.median(sizes), 3) if sizes else None,
            "p95": round(percentile(sizes, 0.95), 3) if sizes else None,
        },
        "samples": samples,
    }


async def run(args: argparse.Namespace) -> dict[str, Any]:
    headers: dict[str, str] = {}
    for value in args.header:
        name, separator, content = value.partition(":")
        if not separator or not name.strip():
            raise ValueError("Each --header must use the form 'Name: value'.")
        headers[name.strip()] = content.strip()

    urls = [endpoint_url(args.base_url, endpoint) for endpoint in args.endpoints]
    timeout = httpx.Timeout(args.timeout)
    async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True) as client:
        results = [await measure(client, url, args.runs) for url in urls]

    return {
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "runs_per_endpoint": args.runs,
        "results": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure endpoint latency and response sizes.")
    parser.add_argument("--base-url", required=True, help="Base URL, for example https://api.example.com")
    parser.add_argument("--runs", type=int, default=10, help="Requests per endpoint (default: 10)")
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-request timeout in seconds (default: 30)")
    parser.add_argument(
        "--header",
        action="append",
        default=[],
        help="Request header in 'Name: value' form; may be repeated",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("metrics/results"))
    parser.add_argument("endpoints", nargs="+", help="Endpoint paths or complete URLs")
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be at least 1")
    return args


def main() -> None:
    args = parse_args()
    try:
        result = asyncio.run(run(args))
    except ValueError as error:
        raise SystemExit(str(error)) from error

    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = args.output_dir / f"{timestamp}.json"
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    for item in result["results"]:
        latency = item["latency_ms"]
        size = item["response_size_kb"]
        print(
            f"{item['endpoint']} | latency ms min/median/p95: "
            f"{latency['min']}/{latency['median']}/{latency['p95']} | "
            f"response KB min/median/p95: {size['min']}/{size['median']}/{size['p95']} | "
            f"responses received: {item['responses_received']}/{item['runs']}"
        )
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
