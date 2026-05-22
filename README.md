# Local Lead Finder — Python SDK

> **Find local businesses by category + location and get sales-ready leads with 30+ enrichment signals: lead score, website tech stack, real emails scraped from sites, normalised phone numbers, chain detection, brand age, mobile-friendliness, SEO audit, industry-specific outreach pitch — all for $4 per 1,000 leads.**

Python client for the [Local Lead Finder Pro Apify Actor](https://apify.com/apivault_labs/local-business-lead-finder) — the most-used lead-gen tool in the apivault_labs catalogue. Built for web agencies, SEO teams, cold-outreach SDRs, and CRM imports.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue?logo=apify)](https://apify.com/apivault_labs/local-business-lead-finder)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Pricing](https://img.shields.io/badge/pricing-$4%20per%201,000-orange)](https://apify.com/apivault_labs/local-business-lead-finder)

---

## What it does

Scrape **YellowPages** for local businesses in any US city, then auto-enrich every result with a stack of intelligence signals that turn raw listings into sales-ready leads:

- **Lead score (0-100)** + tier (`cold` / `warm` / `hot` / `on-fire`)
- **Website tech stack** — Wix, WordPress, Shopify, Squarespace, GoDaddy, Webflow, Weebly, Joomla, Drupal, ClickFunnels, GoHighLevel
- **Real emails** scraped from the website (mailto: links, plain-text, CloudFlare-decoded, obfuscated `info [at] domain` patterns)
- **Phone numbers** in E.164 format with `tel:` click-to-call URL
- **Chain detection** — flag national franchises (50+ brands) so agencies can skip them
- **Brand age** via Wayback Machine — established business with a dead site = prime replacement target
- **Mobile-friendliness audit** + **SEO hygiene audit** (5 signals each)
- **Industry-specific outreach pitch** — 10 industries with custom angles
- **Best-contact-channel recommendation** — one field that says "email this address" or "call this number"
- **CSV export** ready for HubSpot, Pipedrive, Salesforce, Close

A direct, pay-per-use alternative to:
- Manual YellowPages scraping (anti-bot, dedup, fragile)
- Generic local-data APIs ($99-$499/mo)
- Apollo.io / ZoomInfo for hyper-local outreach

**Pricing:** $4 per 1,000 leads ($0.004/lead). Enrichment is free — included in the per-result price.

---

## Quick start

```python
from local_lead_finder import LocalLeadFinderClient

client = LocalLeadFinderClient(api_token="apify_api_xxxxxx")

leads, summary = client.find_leads(
    category="plumbers",
    location="New York NY",
    pages=2,
    only_without_website=True,   # web-agency hot leads
    exclude_chains=True,          # skip Roto-Rooter etc.
    min_lead_score=50,            # skip cold leads
)

for lead in leads:
    print(f"{lead['Business Name']:<30} score={lead['leadScore']:>3} "
          f"tier={lead['leadTier']:<8} {lead['bestContact']['value']}")
    print(f"  pitch: {lead['outreachPitch']}\n")

print(f"Summary: {summary['totalLeads']} leads, "
      f"{summary['shadowbannedCount'] if False else summary['withoutWebsite']} without website, "
      f"avg score {summary['avgLeadScore']}")
```

Output:
```
Local Plumbing NYC             score= 73 tier=hot     +17185084834
  pitch: Hi Local Plumbing NYC — noticed you're listed on YellowPages
  as a Plumber in New York with 12 reviews averaging 4.5★...

ABC Plumbing Co                score= 68 tier=hot     +12125550100
  pitch: Hi ABC Plumbing Co — your YellowPages listing has a website
  link, but it isn't loading right now...
```

---

## Installation

```bash
pip install git+https://github.com/apivault-labs/local-lead-finder-python.git
```

Or clone and use directly:

```bash
git clone https://github.com/apivault-labs/local-lead-finder-python.git
cd local-lead-finder-python
pip install -r requirements.txt
```

Requires Python 3.9+ and the [`requests`](https://pypi.org/project/requests/) library.

---

## Get your API token (free)

1. Sign up at [apify.com](https://apify.com) — free tier includes $5 monthly credits, no card required
2. Go to [Account → Integrations](https://console.apify.com/account/integrations)
3. Copy your Personal API token

```bash
export APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

Or pass it explicitly:

```python
client = LocalLeadFinderClient(api_token="apify_api_xxxxxx")
```

---

## What you get for $0.002 per lead

### 📋 Core fields (always returned)
- `Business Name`, `Phone`, `Address`, `City`, `State`
- `Rating`, `Reviews Count`, `Category`
- `Website`, `Email`, `Hours`, `Years in Business`
- `Listing URL`, `hasWebsite`

### 🎯 Lead intelligence
- `leadScore` (0-100) — composite of 12 weighted signals
- `leadScoreReasons[]` — every contributing signal in plain English
- `leadTier` — `cold` / `warm` / `hot` / `on-fire`

### 🛠️ Website intelligence (when site exists)
- `websiteAlive`, `websiteStatus`, `websiteSslValid`
- `websiteTechStack[]` — Wix, WordPress, Shopify, Squarespace, GoDaddy, Webflow, Weebly, WordPress.com, Joomla, Drupal, ClickFunnels, GoHighLevel
- `mobileFriendly`, `mobileSignals[]` — viewport, responsive CSS, AMP, etc.
- `seoAudit: {hasMetaDescription, hasOgImage, hasH1, hasJsonLd, hasCanonical, seoScore}`
- `brandAgeYears` — Wayback Machine first snapshot
- `emailsFromWebsite[]` — real emails (mailto, plain-text, CF-decoded, obfuscated)
- `phonesFromWebsite[]` — phones from `tel:` links + page text
- `contactPageUrl` — auto-detected `/contact` link

### 📧 Outreach helpers
- `phoneE164` — `+17185084834` format
- `phoneTel` — `tel:+17185084834` click-to-call URL
- `emailGuesses[]` — `info@`, `contact@`, `hello@`, `office@` from domain
- `socialSearchUrls{}` — Facebook, Instagram, LinkedIn, Google Maps, Google Search deep links
- `outreachPitch` — auto-written 2-sentence cold opener with industry angle

### 🎯 Decision aids
- `bestContact: {channel, value, label}` — one field, the highest-confidence outreach path
- `isChain`, `chainBrand` — flag franchises like Roto-Rooter, Subway, RE/MAX

### 📍 Optional geocoding
- `lat`, `lng`, `geocodedAddress`, `osmUrl` (when `enrich_geocode=True`)

---

## Examples

See the [`examples/`](examples) folder for full code:

| File | What it does |
|---|---|
| [`quickstart.py`](examples/quickstart.py) | Find 30 plumbers in NY, print top 10 with pitches |
| [`bulk_cities.py`](examples/bulk_cities.py) | Same category across 5 cities, compare markets |
| [`replaceable_websites.py`](examples/replaceable_websites.py) | Filter to Wix / dead-site / non-mobile leads only |
| [`hot_leads_only.py`](examples/hot_leads_only.py) | Filter to `on-fire` and `hot` tiers, sort by score |
| [`export_to_csv.py`](examples/export_to_csv.py) | Save HubSpot/Pipedrive-ready CSV |
| [`agency_outreach.py`](examples/agency_outreach.py) | Generate per-lead outreach script for SDR team |
| [`territory_map.py`](examples/territory_map.py) | Geocode + cluster leads by lat/lng for territory routing |

---

## API reference

### `LocalLeadFinderClient(api_token=None, timeout=1200)`

| Param | Type | Description |
|---|---|---|
| `api_token` | `str` | Apify API token. Falls back to `APIFY_API_TOKEN` env var. |
| `timeout` | `int` | Max seconds to wait for the actor run. Default 1200. |
| `poll_interval` | `float` | Seconds between status polls. Default 3. |

### `client.find_leads(category, location, **kwargs)`

The main entry point. Returns `(leads, summary)`.

| Param | Type | Default | Description |
|---|---|---|---|
| `category` | `str` | required | Business type (`"plumbers"`, `"restaurants"`, etc.) |
| `location` | `str` | required | City + state (`"New York NY"`) |
| `pages` | `int` | 1 | YellowPages pages to scrape (max 10) |
| `only_without_website` | `bool` | `False` | Drop businesses with a website |
| `exclude_chains` | `bool` | `False` | Drop national franchises |
| `min_lead_score` | `int` | 0 | Drop leads below this score (0-100) |
| `max_results` | `int` | 0 | Cap results after sorting (0 = no cap) |
| `enrich_websites` | `bool` | `True` | Probe sites for tech stack, emails, mobile, SEO |
| `enrich_email_guesses` | `bool` | `True` | Generate `info@/contact@/hello@/office@` |
| `enrich_social_urls` | `bool` | `True` | 1-click FB/IG/LinkedIn/Maps search URLs |
| `include_outreach_pitch` | `bool` | `True` | Auto-write personalised cold opener |
| `enrich_brand_age` | `bool` | `True` | Wayback Machine first-snapshot year |
| `enrich_geocode` | `bool` | `False` | Nominatim lat/lng (slow — opt in) |
| `export_format` | `str` | `"default"` | `"default"`, `"csv"`, or `"both"` |

### `client.find_in_cities(category, cities, **kwargs)`

Run the same category across multiple cities. Returns `dict[city, (leads, summary)]`.

```python
results = client.find_in_cities(
    "dentists",
    ["New York NY", "Chicago IL", "Miami FL"],
    only_without_website=True,
)
for city, (leads, summary) in results.items():
    print(f"{city}: {summary['totalLeads']} leads")
```

### `client.filter_by_tier(leads, *tiers)`

Filter a list of leads by lead tier. Default is `("on-fire", "hot")`.

```python
hot_leads = client.filter_by_tier(leads, "on-fire", "hot")
```

### `client.filter_replaceable_websites(leads)`

Filter to leads where the website is a prime replacement target: Wix / Weebly / GoDaddy / WordPress.com / dead / not mobile-friendly.

### `client.estimate_cost(lead_count)`

Returns the estimated USD cost (`lead_count × $0.002`).

---

## Sample lead output

```json
{
    "Business Name": "Local Plumbing NYC",
    "Phone": "(718) 508-4834",
    "Address": "1 Chase Manhattan Plz, New York, NY 10005",
    "City": "New York",
    "State": "NY",
    "Rating": 4.5,
    "Reviews Count": 12,
    "Category": "Plumbers",
    "Website": "",
    "Email": "",
    "Hours": "Mon-Fri 8am-6pm",
    "Years in Business": "27 Years",
    "Listing URL": "https://www.yellowpages.com/...",

    "hasWebsite": false,
    "isChain": false,
    "chainBrand": null,
    "phoneE164": "+17185084834",
    "phoneTel": "tel:+17185084834",

    "websiteAlive": null,
    "websiteTechStack": [],
    "mobileFriendly": null,
    "seoAudit": null,
    "brandAgeYears": null,

    "emailsFromWebsite": [],
    "phonesFromWebsite": [],
    "contactPageUrl": null,

    "emailGuesses": [],
    "socialSearchUrls": {
        "facebook": "https://www.facebook.com/search/top?q=...",
        "instagram": "https://www.google.com/search?q=...+site%3Ainstagram.com",
        "linkedin": "https://www.google.com/search?q=...+site%3Alinkedin.com%2Fcompany",
        "googleMaps": "https://www.google.com/maps/search/...",
        "googleSearch": "https://www.google.com/search?q=..."
    },

    "leadScore": 73,
    "leadTier": "hot",
    "leadScoreReasons": [
        "no website (highest-value lead for web agencies)",
        "active business (12 reviews)",
        "high rating (4.5★)",
        "27 years in business — stable"
    ],
    "outreachPitch": "Hi Local Plumbing NYC — noticed you're listed on YellowPages as a Plumber in New York with 12 reviews averaging 4.5★, but you don't have a website yet — for a plumber, emergency calls — half your jobs come from someone Googling at 2am. I help local businesses go from zero to a Google-ranked site in under 2 weeks. Worth a 10-min chat?",
    "bestContact": {
        "channel": "phone",
        "value": "+17185084834",
        "label": "phone from YellowPages listing"
    }
}
```

### Aggregate summary record (always included unless `pages=1` and 1 result)

```json
{
    "_summary": true,
    "totalLeads": 100,
    "withoutWebsite": 47,
    "withDeadWebsite": 8,
    "withRealEmailScraped": 12,
    "chainCount": 5,
    "avgLeadScore": 56.3,
    "leadTierBreakdown": {"cold": 12, "warm": 31, "hot": 39, "on-fire": 18},
    "topTechStacks": [["Wix", 12], ["WordPress", 8], ["GoDaddy", 6], ["Squarespace", 4]],
    "category": "plumbers",
    "location": "New York NY"
}
```

---

## Use cases

### 🌐 Web Design & Development Agencies
Find businesses with no website (`leadScore` typically 60+) or stuck on DIY templates (Wix / GoDaddy). The `outreachPitch` field gives you a ready-to-send opener; `websiteTechStack` tells you what they're stuck on.

```python
hot_leads, _ = client.find_leads(
    category="dentists",
    location="Los Angeles CA",
    pages=10,
    only_without_website=True,
    exclude_chains=True,
    min_lead_score=55,
)
```

### 📈 SEO & Digital Marketing
Filter to leads with poor SEO score and you've got an instant pitch list:

```python
seo_targets = [
    L for L in leads
    if (L.get("seoAudit") or {}).get("seoScore", 100) < 40
    and L.get("websiteAlive")
]
```

### 📞 Cold Calling Teams
`exportFormat="csv"` drops straight into HubSpot or Pipedrive. Phone numbers are pre-normalised to E.164:

```python
leads, _ = client.find_leads(
    category="restaurants",
    location="Miami FL",
    pages=10,
    export_format="csv",
)
```

### 🏗️ Lead-Routing Automation
Pipe to Make / Zapier / n8n. Route `on-fire` (score ≥75) to your top closer:

```python
on_fire = client.filter_by_tier(leads, "on-fire")
```

### 📊 Market Research
Compare cities side-by-side:

```python
results = client.find_in_cities(
    "plumbers",
    ["New York NY", "Chicago IL", "Miami FL", "Phoenix AZ", "Dallas TX"],
    pages=3,
)
for city, (leads, summary) in results.items():
    print(f"{city}: {summary['avgLeadScore']} avg, "
          f"{summary['withoutWebsite']}/{summary['totalLeads']} no-site")
```

### 🔧 Maintenance & Hosting Pitches
Filter to dead websites — easy "we'll fix it for $X/mo" close:

```python
dead = [L for L in leads if L.get("websiteAlive") is False]
```

### 📍 Territory Routing
Enable geocoding and route by lat/lng to local sales reps:

```python
leads, _ = client.find_leads(
    category="hvac",
    location="Houston TX",
    pages=5,
    enrich_geocode=True,
)
```

---

## How lead score works

A composite 0-100 signal. Higher = hotter lead.

| Signal | Points |
|--------|--------|
| **No website** | +40 |
| **Website unreachable / dead** | +25 |
| **DIY builder (Wix / Weebly / GoDaddy / WordPress.com)** | +15 |
| **Squarespace** | +10 |
| **100+ reviews** | +15 |
| **30-99 reviews** | +10 |
| **5-29 reviews** | +5 |
| **Rating ≥ 4.0★** | +10 |
| **Rating 3.0-3.9★** | +5 |
| **10+ years in business** | +5 |
| **Address present** | +3 |
| **Hours present** | +3 |
| **Established brand (5+ yr) with dead site** | +10 |
| **Not mobile-friendly** | +8 |
| **Poor on-page SEO (<40)** | +5 |
| **Chain / franchise** | -30 (penalty) |
| **No phone number** | -20 (penalty) |

Tiers: `cold` (<35), `warm` (35-54), `hot` (55-74), `on-fire` (75+).

---

## Industry-specific outreach pitches

10 industries with tailored angles:

| Industry | Angle |
|---|---|
| **Plumbers / Electricians / HVAC** | emergency calls — half your jobs come from someone Googling at 2am |
| **Restaurants / Pizza** | online menus and reservation links — diners decide where to eat from their phone |
| **Dentists** | online booking — patients now expect to schedule a cleaning the same way they book an Uber |
| **Lawyers / Attorneys** | Google rankings for '[city] [practice area] attorney' — that's where 80% of clients start |
| **Auto Repair** | Google reviews + 'near me' — most car owners pick the nearest 4★ shop |
| **Salons / Hair / Barber** | Instagram-style portfolio gallery — clients book based on photos |
| **Gyms / Fitness** | membership signup forms + class schedules — gym shoppers compare 3-4 sites |
| **Landscaping / Roofing** | before/after photo galleries — homeowners hire based on portfolio |
| **Real Estate / Realtor** | IDX listings + lead capture — agents without sites lose 40% of online enquiries |
| **Cleaning Services** | online quote forms + booking — most customers want a price in 60 seconds |

The industry angle is woven into the dynamic pitch (no-website / dead-site / Wix / SEO templates).

---

## Pricing

Pay only for what you find:

| Volume | Cost |
|---|---|
| 100 leads | $0.40 |
| 1,000 leads | $4.00 |
| 10,000 leads | $40.00 |

Free Apify tier includes ~$5 monthly credit — that's **1,250 free leads per month**.

All enrichment (website probing, email scraping, tech stack, mobile audit, SEO audit, brand age, outreach pitches) is **free** — included in the per-lead price.

---

## How it works

1. Builds a YellowPages search URL from `category` + `location`
2. Scrapes 1–10 pages in parallel via Thunderbit (handles anti-bot)
3. Deduplicates by name + phone
4. For every lead with a website, runs a HEAD/GET probe:
   - Tech-stack pattern matching (12 platforms)
   - Real email extraction (mailto, plain-text, CloudFlare-decoded, obfuscated)
   - Phone extraction from `tel:` + page text
   - Mobile-friendly audit (5 signals)
   - SEO audit (5 signals)
   - Brand-age via Wayback Machine
   - Contact-page discovery
5. Computes lead score, classifies tier, generates personalised pitch
6. Sorts by score descending, filters by `min_lead_score` / `max_results`
7. Returns leads + an aggregate `_summary` record

Speed: ~10-30 seconds per page (parallel YellowPages fetches), ~1-2 sec per lead with website (parallel HTTP HEAD probes).

---

## FAQ

**Q: Does it work outside the US?**
A: YellowPages.com covers US businesses. For other countries, look for a local YellowPages equivalent.

**Q: How accurate is the email scraping?**
A: When the actor returns an email in `emailsFromWebsite[]`, it's been through 5 layers of false-positive filtering (TLD whitelist, lookbehind regex, CDN blacklist, plausibility checks). Verify with Hunter / NeverBounce before sending mass campaigns.

**Q: How does chain detection work?**
A: Substring match against ~50 national chain brands (Roto-Rooter, Subway, Domino's, Great Clips, Anytime Fitness, RE/MAX, Servpro, Verizon, AT&T, etc.) in the business name. Chains get -30 to lead score; with `exclude_chains=True` they're dropped.

**Q: Why is `mobileFriendly` `null` sometimes?**
A: When the lead has no website (`hasWebsite: false`) or the site is unreachable (`websiteAlive: false`). The audit only runs on alive websites.

**Q: What if the actor returns no emails for a lead?**
A: Many small businesses publish only a contact form, no email. The actor returns `emailGuesses` (`info@domain`, `contact@domain`) as a fallback — verify these with an email-finder service before using.

**Q: Can I disable enrichment to save time?**
A: Yes — set `enrich_websites=False` (skips website probes), `enrich_brand_age=False` (skips Wayback), `include_outreach_pitch=False` (skips pitch generation). Each one cuts ~1-2 seconds per lead.

**Q: How do I integrate with HubSpot / Pipedrive?**
A: Use `export_format="csv"`. The output has CRM-friendly column names (`Company`, `Industry`, `Lead Score`, `Lead Tier`, `Outreach Pitch`).

---

## Related Apify actors

- [Yelp Business Analyzer](https://apify.com/apivault_labs/yelp-business-scraper) — same lead intelligence for Yelp businesses
- [Domain Intelligence Scraper](https://apify.com/apivault_labs/domain-intelligence-scraper) — WHOIS, DNS, SSL for any domain
- [TikTok Shadow Ban Checker](https://apify.com/apivault_labs/tiktok-shadow-ban-checker) — paying revenue actor

See [all actors by apivault_labs](https://apify.com/apivault_labs).

---

## License

MIT — see [LICENSE](LICENSE).

This client is open source. The underlying Apify actor is a paid service ($0.002/lead).

---

## Keywords

`local-lead-generation` `local-business-scraper` `yellowpages-scraper` `lead-finder-api` `web-agency-leads` `seo-leads` `local-seo-leads` `cold-outreach-leads` `business-without-website` `website-tech-stack` `wix-detection` `wordpress-detection` `shopify-detection` `email-scraper` `phone-scraper` `lead-scoring` `lead-tier` `outreach-automation` `chain-detection` `mobile-audit` `seo-audit` `brand-age-wayback` `crm-export` `hubspot-import` `pipedrive-import` `salesforce-import` `apollo-alternative` `zoominfo-alternative` `hunter-alternative` `web-scraping` `apify` `apify-actor` `python-sdk`
