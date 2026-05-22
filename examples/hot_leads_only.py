"""
Filter to ONLY 'on-fire' and 'hot' tier leads.

Use case: same-day call list for your top closer. These are leads with
no-website / dead-site / strong establishment signals.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/hot_leads_only.py
"""

from local_lead_finder import LocalLeadFinderClient


def main() -> None:
    client = LocalLeadFinderClient(timeout=1500)

    leads, summary = client.find_leads(
        category="lawyers",
        location="Chicago IL",
        pages=5,
        only_without_website=True,    # web-agency hot path
        exclude_chains=True,
        min_lead_score=55,            # actor-side cut; tier filter below
    )

    hot = client.filter_by_tier(leads, "on-fire", "hot")

    if not hot:
        print(f"No hot leads from {len(leads)} returned.")
        if summary:
            print(f"Try removing 'only_without_website' or lowering 'min_lead_score'.")
            print(f"Tier breakdown was: {summary['leadTierBreakdown']}")
        return

    print(f"\n🔥 {len(hot)} hot+ leads ready for outreach:\n")

    for lead in hot:
        name = lead.get("Business Name") or "?"
        score = lead.get("leadScore") or 0
        tier = lead.get("leadTier") or "?"
        bc = lead.get("bestContact") or {}
        rating = lead.get("Rating") or "?"
        reviews = lead.get("Reviews Count") or 0

        print(f"⭐ [{tier:<8}] {score}/100  {name}")
        print(f"   {rating}★ × {reviews} reviews  ·  {lead.get('Address') or ''}")
        print(f"   📞 {bc.get('value') or '?'}  ({bc.get('label') or ''})")
        print(f"   💡 {(lead.get('outreachPitch') or '')[:280]}")
        print()


if __name__ == "__main__":
    main()
