def get_diff_summary(diff: str) -> str:
    return diff[:80] if diff else ""
