"""
Step 1: explore the Pi-hole v6 API.

Logs in, prints a summary, shows what one raw query looks like,
then groups recent blocked queries by device. Always logs out at the end.
"""
import json
import os
from collections import Counter, defaultdict

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
    with httpx.Client(base_url=PIHOLE_URL, timeout=10) as client:
        sid = login(client)
        client.headers["X-FTL-SID"] = sid
        try:
            # 1. Overall stats
            summary = client.get("/api/stats/summary").json()
            q = summary["queries"]
            print(f"Total queries: {q['total']}  blocked: {q['blocked']}  "
                  f"({q['percent_blocked']:.1f}%)\n")

            # 2. Recent queries from the query log
            data = client.get("/api/queries", params={"length": 500}).json()
            queries = data["queries"]
            print(f"Fetched {len(queries)} recent queries.")
            if queries:
                print("One raw query looks like this:")
                print(json.dumps(queries[0], indent=2))

            # 3. Blocked domains per device
            per_device = defaultdict(Counter)
            for item in queries:
                if item.get("status") in BLOCKED:
                    ip = item["client"]["ip"]
                    per_device[ip][item["domain"]] += 1

            print("\nTop blocked domains per device:")
            for ip, domains in per_device.items():
                print(f"\n  {ip}  ({sum(domains.values())} blocked)")
                for domain, count in domains.most_common(5):
                    print(f"    {count:>4}  {domain}")
        finally:
            # Free the session so they don't pile up
            client.delete("/api/auth")


if __name__ == "__main__":
    main()
