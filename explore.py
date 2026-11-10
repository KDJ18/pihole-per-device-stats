"""
Fetches DNS queries using the Pi-Hole API with paging.

"""

import os
import time
import argparse

import httpx
from dotenv import load_dotenv

load_dotenv()
PIHOLE_URL = os.environ["PIHOLE_URL"].rstrip("/")
PIHOLE_PASSWORD = os.environ["PIHOLE_PASSWORD"]

#blocked query statuses
BLOCKED = {"GRAVITY", "REGEX", "DENYLIST", "EXTERNAL_BLOCKED_IP",
           "EXTERNAL_BLOCKED_NULL", "EXTERNAL_BLOCKED_NXRA",
           "GRAVITY_CNAME", "REGEX_CNAME", "DENYLIST_CNAME", "SPECIAL_DOMAIN"}

#login function that checks credentials and returns session id if valid
def login(client: httpx.Client) -> str:
    r = client.post("/api/auth", json={"password": PIHOLE_PASSWORD})
    r.raise_for_status()
    session = r.json()["session"]
    if not session["valid"]:
        raise SystemExit(f"Login failed: {session.get('message')}")
    return session["sid"]

def get_queries(client: httpx.Client, hours: float, length: int) -> list[dict]:
    passed_seconds = hours * 3600
    current_length = length
    queries = []
    since = int(time.time() - passed_seconds)
    start = 0

    while current_length > 0:
        chunk = min(500, current_length)
        data = client.get("/api/queries", params={"from": since ,"start": start ,"length": chunk}).json()
        batch = data["queries"] # current list of queries
        queries.extend(batch) #extends the queries list by appending the current batch
        start += len(batch) # the start position for query requests
        current_length -= len(batch)

        ##if the the api runs out of queries it exits
        if len(batch) < chunk:
            break
    return queries



def main() -> None:
    #create argument parser object to capture hours and length input when starting this script
    parser = argparse.ArgumentParser(description="Explore Pi-hole queries")
    parser.add_argument("--hours", type=float, default=24,
                        help="how many hours back to fetch (default: 24)")
    parser.add_argument("--length", type=int, default=500,
                        help="max number of queries to fetch (default: 500)")
    args = parser.parse_args()

    #create client object of type 'httpx.Client' to interact with pi-hole api
    with httpx.Client(base_url=PIHOLE_URL, timeout=10) as client:
        #save session id for client and set headers
        sid = login(client)
        client.headers["X-FTL-SID"] = sid
        hours = args.hours
        length = args.length

        try:
            #function to read x amount of queries and return query list
            queries = get_queries(client, hours, length)
            print(f"{len(queries)} Queries Retrieved from the past {hours} hours")
        finally:
            #free the session
            client.delete("/api/auth")

#main entrypoint
if __name__ == "__main__":
    main()
