# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

from __future__ import annotations

import argparse

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset SpectraStrike local demo runtime stores.")
    parser.add_argument("--base-url", default="https://127.0.0.1:18443/ui/api")
    args = parser.parse_args()

    session = requests.Session()
    auth = session.post(
        f"{args.base_url}/v1/auth/demo",
        headers={"origin": args.base_url.replace("/ui/api", "/ui")},
        timeout=15,
        verify=False,
    )
    auth.raise_for_status()
    token = str(auth.json().get("access_token", "")).strip()
    if not token:
        raise RuntimeError("demo auth did not return access token")

    reset = session.post(
        f"{args.base_url}/execution/reset",
        headers={
            "authorization": f"Bearer {token}",
            "origin": args.base_url.replace("/ui/api", "/ui"),
        },
        timeout=20,
        verify=False,
    )
    reset.raise_for_status()
    print(reset.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
