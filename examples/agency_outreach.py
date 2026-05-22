"""
Generate a per-lead outreach script bundle for your SDR team.

Each lead becomes one block with: contact channel, suggested email subject,
the auto-generated pitch, and the lead's score reasons (so the SDR knows
WHY this lead matters).

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/agency_outreach.py
"""

from local_lead_finder import LocalLeadFinderClient


def email_subject_for(lead: dict) -> str:
    """Pick an email subject that matches the detected gap."""
    reasons = " ".join(lead.get("leadScoreReasons") or [])
    if "no website" in reasons:
        return f"Quick question about your online presence, {lead.get('Business Name')}"
    if "dead" in reasons:
        return f"Heads-up: your website is down — happy to help"
    if "DIY website builder" in reasons:
        techs = lead.get("websiteTechStack") or []
        first = techs[0] if techs else "your current builder"
        return f"Have you outgrown {first}?"
    if "poor on-page SEO" in reasons:
        return f"Free 5-min SEO audit for {lead.get('Business Name')}"
    if "not mobile-friendly" in reasons:
        return f"Your site might be losing mobile customers"
    return f"Saw your YellowPages listing — quick idea"


def main() -> None:
    client = LocalLeadFinderClient(timeout=1500)

    leads, _ = client.find_leads(
        category="dentists",
        location="Houston TX",
        pages=3,
        exclude_chains=True,
        min_lead_score=45,
        max_results=20,
    )

    print(f"=== Outreach Bundle ({len(leads)} leads) ===\n")

    for i, lead in enumerate(leads, 1):
        bc = lead.get("bestContact") or {}
        print(f"--- LEAD {i} of {len(leads)} ---")
        print(f"Company:    {lead.get('Business Name')}")
        print(f"Tier:       [{lead.get('leadTier')}] score={lead.get('leadScore')}/100")
        print(f"Channel:    {bc.get('channel')} ({bc.get('label')})")
        print(f"Contact:    {bc.get('value')}")
        print(f"Why hot:    {' | '.join(lead.get('leadScoreReasons') or [])}")
        print(f"Subject:    {email_subject_for(lead)}")
        print(f"Pitch:")
        print(f"  {(lead.get('outreachPitch') or '').strip()}")
        print()


if __name__ == "__main__":
    main()
