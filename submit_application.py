#!/usr/bin/env python3

import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from urllib import error, request


SUBMISSION_URL = "https://b12.io/apply/submission"


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_signing_secret() -> bytes:
    secret = os.environ.get("B12_SIGNING_SECRET", "hello-there-from-b12")
    return secret.encode("utf-8")


def iso8601_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def build_payload() -> dict[str, str]:
    github_server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    github_repository = require_env("GITHUB_REPOSITORY")
    github_run_id = require_env("GITHUB_RUN_ID")

    repository_link = f"{github_server_url}/{github_repository}"
    action_run_link = f"{github_server_url}/{github_repository}/actions/runs/{github_run_id}"

    return {
        "action_run_link": action_run_link,
        "email": require_env("APPLICANT_EMAIL"),
        "name": require_env("APPLICANT_NAME"),
        "repository_link": repository_link,
        "resume_link": require_env("RESUME_LINK"),
        "timestamp": iso8601_utc_now(),
    }


def canonical_json_bytes(payload: dict[str, str]) -> bytes:
    body = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return body.encode("utf-8")


def build_signature(body: bytes, secret: bytes) -> str:
    digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def post_submission(body: bytes, signature: str) -> None:
    req = request.Request(
        SUBMISSION_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "X-Signature-256": signature,
        },
    )

    try:
        with request.urlopen(req) as resp:
            response_text = resp.read().decode("utf-8")
            print(f"HTTP {resp.status}")
            print(response_text)

            if resp.status != 200:
                raise RuntimeError(f"Unexpected status code: {resp.status}")
    except error.HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}", file=sys.stderr)
        print(response_text, file=sys.stderr)
        raise
    except error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc}") from exc


def main() -> None:
    payload = build_payload()
    body = canonical_json_bytes(payload)
    signature = build_signature(body, get_signing_secret())

    print("Submitting canonical payload:")
    print(body.decode("utf-8"))
    print(f"X-Signature-256: {signature}")

    post_submission(body, signature)


if __name__ == "__main__":
    main()
