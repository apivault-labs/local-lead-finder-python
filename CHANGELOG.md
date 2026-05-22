# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-05-22

### Added
- Initial release of the Python SDK for `apivault_labs/local-business-lead-finder` (actor v2.2)
- `LocalLeadFinderClient` with primary methods:
  - `find_leads(category, location, **kwargs)` — main entry point
  - `find_one_city(category, city_state, **kwargs)` — convenience wrapper
  - `find_in_cities(category, cities, **kwargs)` — multi-city sweep returning `dict[city, (leads, summary)]`
  - `filter_by_tier(leads, *tiers)` — client-side tier filter (`on-fire`, `hot`, `warm`, `cold`)
  - `filter_replaceable_websites(leads)` — client-side filter for Wix / Weebly / GoDaddy / dead / non-mobile sites
  - `estimate_cost(lead_count)` — pricing helper
- All 11 actor input parameters forwarded:
  `category`, `location`, `pages`, `onlyWithoutWebsite`, `enrichWebsites`,
  `enrichEmailGuesses`, `enrichSocialUrls`, `includeOutreachPitch`,
  `enrichBrandAge`, `enrichGeocode`, `excludeChains`, `minLeadScore`,
  `maxResults`, `exportFormat`, `maxConcurrency`
- Automatic split of dataset into per-lead records and the aggregate
  `_summary` record
- 7 example scripts covering the most common workflows
- MIT license
