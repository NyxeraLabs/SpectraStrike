# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

from __future__ import annotations

import argparse
import os
import time

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def _accept_legal(session: requests.Session, api_base: str) -> None:
    payload = {
        "accepted_by": os.getenv("SPECTRASTRIKE_LEGAL_ACCEPTED_BY", "demo-reset"),
        "accepted_documents": {
            "eula": "2026.1",
            "aup": "2026.1",
            "privacy": "2026.1",
        },
    }
    response = session.post(
        f"{api_base}/v1/auth/legal/accept",
        json=payload,
        timeout=15,
        verify=False,
        allow_redirects=False,
    )
    if response.status_code not in {200, 202}:
        response.raise_for_status()


def _try_bootstrap_login(session: requests.Session, api_base: str) -> str:
    username = os.getenv("UI_AUTH_BOOTSTRAP_USERNAME", "operator")
    password = os.getenv("UI_AUTH_BOOTSTRAP_PASSWORD", "Operator!ChangeMe123")
    login = session.post(
        f"{api_base}/v1/auth/login",
        json={"username": username, "password": password},
        timeout=15,
        verify=False,
        allow_redirects=False,
    )
    if 300 <= login.status_code < 400:
        raise RuntimeError(
            f"http_{login.status_code}_redirect_to_{login.headers.get('location', '')}"
        )
    if login.status_code == 403:
        body = {}
        try:
            body = login.json()
        except Exception:  # noqa: BLE001
            body = {}
        if isinstance(body, dict) and body.get("error") == "LEGAL_ACCEPTANCE_REQUIRED":
            _accept_legal(session, api_base)
            login = session.post(
                f"{api_base}/v1/auth/login",
                json={"username": username, "password": password},
                timeout=15,
                verify=False,
                allow_redirects=False,
            )
    login.raise_for_status()
    token = str(login.json().get("access_token", "")).strip()
    if not token:
        raise RuntimeError("bootstrap login did not return access token")
    return token


def _candidate_base_urls(base_url: str) -> list[str]:
    candidates = [
        base_url.rstrip("/"),
        os.getenv("SPECTRASTRIKE_UI_API_BASE_URL", "").rstrip("/"),
        os.getenv("UI_ADMIN_API_BASE_URL", "").rstrip("/"),
        "https://nginx:8443/ui/api",
        "https://spectrastrike_nginx:8443/ui/api",
        "http://ui-web:3000/ui/api",
        "http://spectrastrike_ui_web:3000/ui/api",
        "https://127.0.0.1:18443/ui/api",
        "https://localhost:18443/ui/api",
        "http://127.0.0.1:3000/ui/api",
        "http://localhost:3000/ui/api",
    ]
    out: list[str] = []
    for item in candidates:
        if item and item not in out:
            out.append(item)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset SpectraStrike local demo runtime stores.")
    parser.add_argument("--base-url", default="https://127.0.0.1:18443/ui/api")
    args = parser.parse_args()

    session = requests.Session()
    api_base = ""
    token = ""
    candidate_errors: list[str] = []
    for candidate in _candidate_base_urls(args.base_url):
        last_error = "unknown"
        for _ in range(20):
            try:
                token = _try_bootstrap_login(session, candidate)
                if token:
                    api_base = candidate
                    break
            except Exception as exc:  # noqa: BLE001
                last_error = f"{type(exc).__name__}:{exc}"
                time.sleep(0.8)
        if token:
            break
        candidate_errors.append(f"{candidate} -> {last_error}")
    if not token:
        joined = "; ".join(candidate_errors) if candidate_errors else "no candidates attempted"
        raise RuntimeError(
            "authentication failed for all candidate endpoints. "
            "Expected /v1/auth/login availability and bootstrap credentials. "
            f"details: {joined}"
        )

    reset = session.post(
        f"{api_base}/execution/reset",
        headers={
            "authorization": f"Bearer {token}",
        },
        timeout=20,
        verify=False,
        allow_redirects=False,
    )
    reset.raise_for_status()
    print(reset.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
