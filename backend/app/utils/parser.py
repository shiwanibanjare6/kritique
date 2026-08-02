def parse_pull_request(payload: dict) -> dict:
    return {"repository": payload.get("repository", ""), "pull_request_number": payload.get("number", 0)}
