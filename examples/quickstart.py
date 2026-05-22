"""
Quickstart: find 30 plumbers in New York and print the top 10 with pitches.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from local_lead_finder import LocalLeadFinderClient


def main() -> None:
    client = LocalLeadFinderClient()  # picks up APIFY_API_TOKEN from env

    print(f"Searching plumbers in New York NY (estimated cost: "
          f"${client.estimate_cost(60)})...\n")

    leads, summary = client.find_leads(
        category="plumbers",
        location="New York NY",
        pages=2,
        only_without_website=False,
        exclude_chains=True,
        max_results=10,
    )

    for i, lead in enumerate(leads, 1):
        score = lead.get("leadScore") or 0
        tier = lead.get("leadTier") or "?"
        name = (lead.get("Business Name") or "?")[:30]
        contact = (lead.get("bestContact") or {}).get("value") or "—"
        print(f"{i:>2}. [{tier:<8}] score={score:>3}  {name:<30}  {contact}")
        pitch = lead.get("outreachPitch")
        if pitch:
            print(f"      💡 {pitch[:200]}")
        print()

    if summary:
        print("=== Summary ===")
        print(f"  total leads:        {summary['totalLeads']}")
        print(f"  without website:    {summary['withoutWebsite']}")
        print(f"  dead websites:      {summary['withDeadWebsite']}")
        print(f"  real emails found:  {summary['withRealEmailScraped']}")
        print(f"  chain franchises:   {summary['chainCount']}")
        print(f"  avg lead score:     {summary['avgLeadScore']}/100")
        print(f"  tier breakdown:     {summary['leadTierBreakdown']}")
        if summary.get("topTechStacks"):
            print(f"  top tech stacks:    {summary['topTechStacks'][:3]}")


if __name__ == "__main__":
    main()
