"""
Local Lead Finder — Python SDK

Official Python client for the apivault_labs/local-business-lead-finder Apify
actor. Find local businesses by category + location and get sales-ready leads
with 30+ enrichment signals: lead score (0-100), website tech stack, real
emails scraped from sites, normalised phone numbers, chain detection, brand
age, mobile-friendliness, SEO audit, industry-specific outreach pitch and
best-contact-channel recommendation.

Built for web agencies, SEO teams, cold-outreach SDRs, and CRM imports.

Quick start:

    from local_lead_finder import LocalLeadFinderClient

    client = LocalLeadFinderClient(api_token="apify_api_xxxxxx")

    leads, summary = client.find_leads(
        category="plumbers",
        location="New York NY",
        pages=2,
        only_without_website=True,
        min_lead_score=50,
    )
    for lead in leads:
        print(lead["leadScore"], lead["bestContact"]["value"])
        print(lead["outreachPitch"])

See https://github.com/apivault-labs/local-lead-finder-python for full docs.
"""

from .client import LocalLeadFinderClient
from .exceptions import (
    LocalLeadFinderError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "LocalLeadFinderClient",
    "LocalLeadFinderError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
