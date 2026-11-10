"""
Holds functions for calling Pi-Hole API 

"""

import os
import time

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