"""
Find businesses with REPLACEABLE websites — Wix / Weebly / GoDaddy /
WordPress.com / dead / not-mobile-friendly. Web agencies pitch these
with a "let's redo this properly" angle.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/replaceable_websites.py
"""

from local_lead_finder import LocalLeadFinderClient


def main() -> None:
    client = LocalLeadFinderClient(timeout=1500)

    leads, summary = client.find_leads(
        category="dentists",
        location="Los Angeles CA",
        pages=3,
        only_without_website=False,   # we WANT websites — to detect bad ones
        enrich_websites=True,
        exclude_chains=True,
    )

    replaceable = client.filter_replaceable_websites(leads)

    print(f"\nFound {len(replaceable)} replaceable websites "
          f"out of {len(leads)} total leads\n")

    print(f"{'Business':<28} {'Tech':<25} {'Mobile':<8} {'SEO':>4} {'Score':>6}")
    print("-" * 76)
    for lead in replaceable:
        name = (lead.get("Business Name") or "?")[:28]
        tech = ", ".join(lead.get("websiteTechStack") or [])[:25] or "(dead)"
        mobile = ("Yes" if lead.get("mobileFriendly") else
                  "No" if lead.get("mobileFriendly") is False else "—")
        seo = (lead.get("seoAudit") or {}).get("seoScore", "—")
        score = lead.get("leadScore") or 0
        print(f"{name:<28} {tech:<25} {mobile:<8} {seo:>4} {score:>6}")

    if summary and summary.get("topTechStacks"):
        print(f"\nTop tech stacks in this market: {summary['topTechStacks'][:5]}")


if __name__ == "__main__":
    main()
