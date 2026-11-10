"""
Repurposed as a command-line tool for fetching pi-hole queries

"""

import argparse

import httpx

from pihole_client import PIHOLE_URL, login, get_queries
 
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
            for i, q in enumerate(queries, start=1):
                print(f"{i:>4}  {q['status']:<10}  {q['client']['ip']:<15}  {q['domain']}")
        finally:
            #free the session
            client.delete("/api/auth")

#main entrypoint
if __name__ == "__main__":
    main()
