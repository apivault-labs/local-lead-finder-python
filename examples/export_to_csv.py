"""
Export leads to a CSV ready for HubSpot, Pipedrive, Salesforce or Close.

The actor's `export_format='csv'` mode already produces flattened rows
with CRM-friendly column names — this example just writes them to disk.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/export_to_csv.py > leads.csv
"""

import csv
import sys

from local_lead_finder import LocalLeadFinderClient


def main() -> None:
    client = LocalLeadFinderClient(timeout=1500)

    leads, _ = client.find_leads(
        category="hvac",
        location="Phoenix AZ",
        pages=3,
        only_without_website=False,
        exclude_chains=True,
        export_format="csv",
        max_results=100,
    )

    if not leads:
        print("No leads.", file=sys.stderr)
        return

    # Use the first lead's keys — they're already flat CRM column names
    columns = list(leads[0].keys())

    writer = csv.DictWriter(sys.stdout, fieldnames=columns)
    writer.writeheader()
    for row in leads:
        writer.writerow(row)


if __name__ == "__main__":
    main()
