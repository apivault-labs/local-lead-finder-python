"""
LocalLeadFinderClient — synchronous wrapper around the Apify
``apivault_labs/local-business-lead-finder`` actor (v2.2).

The actor handles all heavy work (YellowPages scraping, dedup, website
probing, tech-stack detection, email/phone scraping, chain detection,
mobile audit, SEO audit, brand age via Wayback, industry-specific
outreach pitch composition, lead scoring) on Apify infrastructure.
This client forwards inputs, polls until the run finishes, then
downloads the dataset and splits it into per-lead records and the
optional aggregate summary.

Pricing: $4 per 1,000 leads (= $0.004/lead). All enrichment included.
"""

from __future__ import annotations

import os
import time
from typing import Any, Iterable, Sequence

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    LocalLeadFinderError,
)


ACTOR_ID = "apivault_labs~local-business-lead-finder"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}

PRICE_PER_LEAD_USD = 0.004

# Lead-tier helpers — match the actor's classify_lead_tier()
TIER_THRESHOLDS = {"on-fire": 75, "hot": 55, "warm": 35, "cold": 0}


class LocalLeadFinderClient:
    """Synchronous client for the Local Lead Finder Apify actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. If omitted, falls back to the
        ``APIFY_API_TOKEN`` environment variable.
    timeout : int, optional
        Maximum seconds to wait for an actor run to finish. Default 1200
        (20 min) — enrichment over many leads can take 5-10 minutes.
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    base_url : str, optional
        Override the Apify API base URL (mostly for testing).
    """

    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 1200,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "local-lead-finder-python/0.1.0",
        })

    # ------------------------------------------------------------------ public

    def find_leads(
        self,
        *,
        category: str,
        location: str,
        pages: int = 1,
        only_without_website: bool = False,
        # Enrichment toggles
        enrich_websites: bool = True,
        enrich_email_guesses: bool = True,
        enrich_social_urls: bool = True,
        include_outreach_pitch: bool = True,
        enrich_brand_age: bool = True,
        enrich_geocode: bool = False,
        # Filters
        exclude_chains: bool = False,
        min_lead_score: int = 0,
        max_results: int = 0,
        # Output
        export_format: str = "default",
        # Concurrency / timing
        max_concurrency: int = 3,
        actor_timeout_secs: int = 600,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Find local businesses for a (category, location) pair.

        Parameters
        ----------
        category : str
            Business type. Examples: ``"plumbers"``, ``"restaurants"``,
            ``"dentists"``, ``"lawyers"``, ``"hair-salons"``,
            ``"auto-repair"``, ``"landscaping"``.
        location : str
            City + state. Examples: ``"New York NY"``, ``"Los Angeles CA"``,
            ``"Miami FL"``.
        pages : int, optional
            YellowPages result pages to scrape (each ~30 businesses, max 10).
        only_without_website : bool, optional
            If ``True``, drop businesses that have a website (the hottest
            leads for web agencies).
        enrich_websites : bool, optional
            HEAD/GET probe of every website with tech stack detection,
            real-email scraping, mobile-friendly + SEO audit.
        enrich_email_guesses : bool, optional
            Generate ``info@``, ``contact@``, ``hello@``, ``office@`` from domain.
        enrich_social_urls : bool, optional
            Build 1-click search links for FB/IG/LinkedIn/Maps/Google.
        include_outreach_pitch : bool, optional
            Auto-write a personalised cold opener tailored to the
            detected gap and the business's industry.
        enrich_brand_age : bool, optional
            Wayback Machine query for first-seen year.
        enrich_geocode : bool, optional
            OpenStreetMap Nominatim geocoding (off by default — slow).
        exclude_chains : bool, optional
            Drop national chains (Roto-Rooter, Subway, Domino's, etc.).
        min_lead_score : int, optional
            Drop leads below this composite score (0-100).
        max_results : int, optional
            Hard cap after sorting by leadScore. ``0`` = no cap.
        export_format : str, optional
            ``"default"`` (full JSON), ``"csv"`` (HubSpot/Pipedrive columns),
            or ``"both"`` (default + nested ``_csv``).
        max_concurrency : int, optional
            Parallel YellowPages page fetches (1-5).
        actor_timeout_secs : int, optional
            Max actor runtime hint (passed to Apify).

        Returns
        -------
        tuple[list[dict], dict | None]
            ``(leads, summary)``. ``summary`` contains aggregate stats
            (totalLeads, withoutWebsite, avgLeadScore, leadTierBreakdown,
            topTechStacks, chainCount) or ``None`` if no leads were found.
        """
        if not category or not category.strip():
            raise ValueError("category is required")
        if not location or not location.strip():
            raise ValueError("location is required")

        payload = {
            "category": category.strip(),
            "location": location.strip(),
            "pages": max(1, min(10, int(pages))),
            "onlyWithoutWebsite": bool(only_without_website),
            "enrichWebsites": bool(enrich_websites),
            "enrichEmailGuesses": bool(enrich_email_guesses),
            "enrichSocialUrls": bool(enrich_social_urls),
            "includeOutreachPitch": bool(include_outreach_pitch),
            "enrichBrandAge": bool(enrich_brand_age),
            "enrichGeocode": bool(enrich_geocode),
            "excludeChains": bool(exclude_chains),
            "minLeadScore": max(0, min(100, int(min_lead_score))),
            "maxResults": max(0, int(max_results)),
            "exportFormat": export_format,
            "maxConcurrency": max(1, min(5, int(max_concurrency))),
        }

        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        records = self._fetch_dataset(run["defaultDatasetId"])
        return self._split_summary(records)

    def find_one_city(
        self,
        category: str,
        city_state: str,
        **kwargs: Any,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Convenience wrapper: ``find_leads(category=..., location=...)``."""
        return self.find_leads(category=category, location=city_state, **kwargs)

    def find_in_cities(
        self,
        category: str,
        cities: Iterable[str],
        **kwargs: Any,
    ) -> dict[str, tuple[list[dict[str, Any]], dict[str, Any] | None]]:
        """Run the same category across multiple cities. Returns a dict
        ``{city: (leads, summary)}`` so the caller can compare markets.

        Each city is one separate Apify run — this is a thin loop, not
        a parallel fan-out (Apify's per-account run quota would cap
        parallelism anyway).
        """
        out: dict[str, tuple[list[dict[str, Any]], dict[str, Any] | None]] = {}
        for city in cities:
            if not city or not city.strip():
                continue
            try:
                out[city] = self.find_leads(category=category, location=city, **kwargs)
            except (ActorRunError, ActorTimeoutError) as e:
                # Don't let one bad city kill the whole sweep
                out[city] = ([], {"_error": str(e), "city": city})
        return out

    def filter_by_tier(
        self,
        leads: Sequence[dict[str, Any]],
        *tiers: str,
    ) -> list[dict[str, Any]]:
        """Filter a list of leads by lead tier.

        Tiers: ``"on-fire"`` (≥75), ``"hot"`` (55-74), ``"warm"`` (35-54),
        ``"cold"`` (<35). Pass one or more tiers — they are OR'd together.
        """
        if not tiers:
            tiers = ("on-fire", "hot")
        wanted = {t.lower() for t in tiers}
        return [r for r in leads if (r.get("leadTier") or "").lower() in wanted]

    def filter_replaceable_websites(
        self,
        leads: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Return only leads where the website is a prime replacement target:
        Wix / Weebly / GoDaddy / WordPress.com / dead site / not mobile-friendly.
        """
        replaceable: list[dict[str, Any]] = []
        DIY_BUILDERS = {"Wix", "Weebly", "GoDaddy", "WordPress.com"}
        for r in leads:
            tech = set(r.get("websiteTechStack") or [])
            if (
                tech & DIY_BUILDERS
                or r.get("websiteAlive") is False
                or r.get("mobileFriendly") is False
            ):
                replaceable.append(r)
        return replaceable

    def estimate_cost(self, lead_count: int) -> float:
        """Return the estimated USD cost for ``lead_count`` leads.

        Pricing is $0.004 per lead ($4 / 1000). Enrichment is free.
        """
        return round(lead_count * PRICE_PER_LEAD_USD, 4)

    # ------------------------------------------------------------------ internal

    @staticmethod
    def _split_summary(
        records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Separate the aggregate `_summary` record from per-lead records."""
        leads: list[dict[str, Any]] = []
        summary: dict[str, Any] | None = None
        for rec in records:
            if isinstance(rec, dict) and rec.get("_summary"):
                summary = rec
            else:
                leads.append(rec)
        return leads, summary

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(url, params=params, json=payload, timeout=30)
        except requests.RequestException as e:
            raise LocalLeadFinderError(f"Failed to start actor run: {e}") from e

        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: {r.text[:300]}"
            )

        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(f"Apify response missing run id: {r.text[:300]}")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise LocalLeadFinderError(f"Failed to poll run status: {e}") from e

            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling run: {r.text[:300]}"
                )

            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )

            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within {self._timeout}s "
                    f"(last status={status}). The run may still be running on Apify; "
                    "increase `timeout=` or fetch the dataset manually."
                )

            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise LocalLeadFinderError(f"Failed to download dataset: {e}") from e

        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching dataset: "
                f"{r.text[:300]}"
            )

        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e

        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload (not a list): {type(data).__name__}"
            )
        return data
