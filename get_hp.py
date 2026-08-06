"""
HP(公式サイト)取得モジュール。Google Places API を使用。
"""

import os
import requests

PLACES_API_KEY = os.environ.get("PLACES_API_KEY", "")


def get_hp(company_name, address=""):
    if not company_name or not PLACES_API_KEY:
        print(f"DEBUG: company_name={company_name}, API_KEY exists={bool(PLACES_API_KEY)}")
        return None, None

    try:
        result = _search_places(company_name, address)
        if result:
            return result.get("url"), result.get("tel")
    except Exception as e:
        print(f"DEBUG ERROR: {type(e).__name__}: {e}")

    return None, None


def _search_places(company_name, address):
    city_match = None
    for pref_marker in ['県', '都', '府', '道']:
        if pref_marker in address:
            idx = address.index(pref_marker)
            city_match = address[:idx + 3]
            break

    city = city_match if city_match else ""
    query = f"{company_name} {city}".strip()

    url = "https://places.googleapis.com/v1/places:searchText"
    payload = {
        "textQuery": query,
        "languageCode": "ja"
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.websiteUri,places.nationalPhoneNumber,places.businessStatus"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"DEBUG: status={resp.status_code}, body={resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()

        if not data.get("places"):
            return None

        place = data["places"][0]

        if place.get("businessStatus") == "CLOSED_PERMANENTLY":
            return None

        return {
            "url": place.get("websiteUri") or "",
            "tel": place.get("nationalPhoneNumber") or "",
        }

    except requests.RequestException as e:
        print(f"DEBUG REQUEST ERROR: {e}")
        return None
