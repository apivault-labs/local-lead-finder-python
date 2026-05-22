"""
Geocode leads and group them by neighborhood for sales-territory routing.

This example uses ``enrich_geocode=True`` which queries OpenStreetMap
Nominatim — slow but adds lat/lng to every lead. Useful when you need
to assign leads to local sales reps by area or plot them on a map.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/territory_map.py
"""

import json

from local_lead_finder import LocalLeadFinderClient


def main() -> None:
    client = LocalLeadFinderClient(timeout=2400)

    leads, summary = client.find_leads(
        category="restaurants",
        location="Brooklyn NY",
        pages=2,
        enrich_geocode=True,           # slower — opt in
        exclude_chains=True,
        max_results=50,
    )

    geocoded = [
        {
            "name": L.get("Business Name"),
            "lat": L.get("lat"),
            "lng": L.get("lng"),
            "address": L.get("geocodedAddress") or L.get("Address"),
            "tier": L.get("leadTier"),
            "score": L.get("leadScore"),
            "phone": L.get("phoneE164"),
            "osm": L.get("osmUrl"),
        }
        for L in leads
        if L.get("lat") is not None and L.get("lng") is not None
    ]

    print(f"Geocoded {len(geocoded)} of {len(leads)} leads\n")

    # Print as GeoJSON-ish for easy import into Mapbox / Leaflet / Kepler
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [g["lng"], g["lat"]],
                },
                "properties": g,
            }
            for g in geocoded
        ],
    }

    print(json.dumps(feature_collection, indent=2, ensure_ascii=False))

    if summary:
        print(f"\nMarket summary: {summary['totalLeads']} leads, "
              f"avg score {summary['avgLeadScore']}/100",
              file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
