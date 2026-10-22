from django.shortcuts import render
from django.http import QueryDict
import requests

API_URL = "https://property-listings-api.vercel.app/api/v1/properties"


def property(request):
    city = request.GET.get("city", "").strip()
    listing_type = request.GET.get("listing_type", "").strip().lower()

    try:
        page = max(1, int(request.GET.get("page", 1)))
    except (ValueError, TypeError):
        page = 1

    limit = 20
    offset = (page - 1) * limit

    context = {
        "properties": [],
        "pagination": {"total": 0, "limit": limit, "offset": offset,
                       "hasMore": False},
        "current_city": city,
        "listing_type": listing_type,
        "current_page": page,
        "previous_url": None,
        "next_url": None,
        "api_error": None,
    }

    try:
        response = requests.get(
            API_URL,
            params={"limit": limit, "offset": offset},
            timeout=20,
        )
        response.raise_for_status()

        result = response.json()
        all_properties = result.get("data", [])

        # Filter the properties returned by the API.
        if city:
            all_properties = [
                item for item in all_properties
                if item.get("city", "").strip().lower() == city.lower()
            ]

        if listing_type:
            all_properties = [
                item for item in all_properties
                if item.get("listingType", "").strip().lower()
                == listing_type
            ]

        meta = result.get("meta", {})
        pagination = meta.get("pagination", {})

        context["properties"] = all_properties
        context["pagination"] = pagination
        context["pagination"]["total"] = len(all_properties)

        # Build links while preserving selected filters.
        query = QueryDict("", mutable=True)
        if city:
            query["city"] = city
        if listing_type:
            query["listing_type"] = listing_type

        if page > 1:
            query["page"] = page - 1
            context["previous_url"] = "?" + query.urlencode()

        # API pagination indicates whether another page exists.
        if pagination.get("hasMore"):
            query["page"] = page + 1
            context["next_url"] = "?" + query.urlencode()

        print("API success:", result.get("success"))
        print("Properties received:", len(result.get("data", [])))
        print("Properties after filtering:", len(all_properties))
        print("Pagination:", pagination)

    except (requests.RequestException, ValueError) as exc:
        context["api_error"] = (
            "The property service could not be reached. Please try again."
        )
        print("Property API error:", repr(exc))

    return render(request, "properties/property.html", context)
