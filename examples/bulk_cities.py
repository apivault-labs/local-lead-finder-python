"""
Run the same category across multiple cities and compare markets.

Useful for choosing where to target your outreach efforts — markets with
the most no-website businesses are easiest to penetrate.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/bulk_cities.py
"""

from local_lead_finder import LocalLeadFinderClient


CATEGORY = "plumbers"
CITIES = [
    "New York NY",
    "Chicago IL",
    "Miami FL",
    "Phoenix AZ",
    "Dallas TX",
]


def main() -> None:
    client = LocalLeadFinderClient(timeout=2400)
    print(f"Searching '{CATEGORY}' in {len(CITIES)} cities...\n")

    results = client.find_in_cities(
        CATEGORY,
        CITIES,
        pages=2,
        only_without_website=False,
        exclude_chains=True,
    )

    print(f"{'City':<22} {'Total':>7} {'No-site':>8} {'Dead':>6} "
          f"{'AvgScore':>9} {'Hot+':>5}")
    print("-" * 65)

    rows = []
    for city, (leads, summary) in results.items():
        if not summary:
            print(f"{city:<22}  ERROR or no data")
            continue
        hot_plus = summary["leadTierBreakdown"].get("hot", 0) + \
                   summary["leadTierBreakdown"].get("on-fire", 0)
        rows.append({
            "city": city,
            "total": summary["totalLeads"],
            "no_site": summary["withoutWebsite"],
            "dead": summary["withDeadWebsite"],
            "avg": summary["avgLeadScore"],
            "hot_plus": hot_plus,
        })

    rows.sort(key=lambda r: -r["hot_plus"])

    for r in rows:
        print(f"{r['city']:<22} {r['total']:>7} {r['no_site']:>8} {r['dead']:>6} "
              f"{r['avg']:>9} {r['hot_plus']:>5}")

    if rows:
        winner = rows[0]
        print(f"\n🏆 Best market: {winner['city']} — {winner['hot_plus']} hot+ leads")


if __name__ == "__main__":
    main()
