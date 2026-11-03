"""
Step 1: explore the Pi-hole v6 API.

Logs in, prints a summary, shows what one raw query looks like,
then groups recent blocked queries by device. Always logs out at the end.
"""
import json
import os
import time
from collections import Counter, defaultdict

import argparse
import httpx
from dotenv import load_dotenv

load_dotenv()
PIHOLE_URL = os.environ["PIHOLE_URL"].rstrip("/")
PIHOLE_PASSWORD = os.environ["PIHOLE_PASSWORD"]

# Pi-hole statuses that mean "this query was blocked"
BLOCKED = {"GRAVITY", "REGEX", "DENYLIST", "EXTERNAL_BLOCKED_IP",
           "EXTERNAL_BLOCKED_NULL", "EXTERNAL_BLOCKED_NXRA",
           "GRAVITY_CNAME", "REGEX_CNAME", "DENYLIST_CNAME", "SPECIAL_DOMAIN"}


def login(client: httpx.Client) -> str:
    r = client.post("/api/auth", json={"password": PIHOLE_PASSWORD})
    r.raise_for_status()
    session = r.json()["session"]
    if not session["valid"]:
        raise SystemExit(f"Login failed: {session.get('message')}")
    return session["sid"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore Pi-hole queries")
    parser.add_argument("--hours", type=float, default=24,
                        help="how many hours back to fetch (default: 24)")
    parser.add_argument("--length", type=int, default=500,
                        help="max number of queries to fetch (default: 500)")
    args = parser.parse_args()

    with httpx.Client(base_url=PIHOLE_URL, timeout=10) as client:
        sid = login(client)
        client.headers["X-FTL-SID"] = sid
        passed_seconds = args.hours * 3600
        try:
            since = int(time.time() - passed_seconds)
            data = client.get("/api/queries", params={"from": since, "length": args.length}).json()
            queries = data["queries"]
            print(f"{len(queries)} Queries Retrieved from the past {args.hours} hours")
            for i, item in enumerate(queries, start=1):
                print(f"Query #{i}", item, '\n')
        finally:
            # Free the session so they don't pile up
            client.delete("/api/auth")


if __name__ == "__main__":
    main()
