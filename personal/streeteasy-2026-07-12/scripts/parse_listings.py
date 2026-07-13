#!/usr/bin/env python3
"""Parse StreetEasy listing HTML pages into a structured JSON dataset."""
import re, json, os, sys, html as htmlmod

SCRATCH = os.environ.get("SE_WORKDIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data")
PAGES = os.path.join(SCRATCH, "pages")


def extract_obj(s, start):
    """Extract a balanced-brace JSON object starting at s[start] == '{'."""
    depth = 0; j = start; in_str = False; esc = False
    while j < len(s):
        ch = s[j]
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0: return s[start:j+1]
        j += 1
    return None


def find_json_after(joined, marker, offset_to_brace=None):
    i = joined.find(marker)
    if i < 0: return None
    b = joined.index('{', i + len(marker) - 1 if marker.endswith('{') else i)
    if marker.endswith('{'):
        b = i + len(marker) - 1
    raw = extract_obj(joined, b)
    if raw is None: return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def titlecase_enum(v):
    return v.replace('_', ' ').title() if isinstance(v, str) else v


def parse_page(path, listing_id):
    html = open(path, encoding="utf-8", errors="replace").read()
    out = {"listing_id": listing_id,
           "url": f"https://streeteasy.com/rental/{listing_id}"}

    # --- RSC flight payload ---
    chunks = re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', html)
    joined = "".join(json.loads(c) for c in chunks)

    listing = find_json_after(joined, '"listing":{"id"')
    building = find_json_after(joined, '"building":{"se"')

    # --- JSON-LD ---
    ld = None; apt = None
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        graph = d.get("@graph", [d])
        for node in graph:
            if node.get("@type") == "ItemPage":
                ld = node
            elif node.get("@type") in ("Apartment", "ApartmentComplex") and node.get("geo"):
                apt = apt or node
    geo = {}
    if apt:
        geo = apt.get("geo", {})
    if ld:
        main = ld.get("mainEntity", {})
        geo = geo or main.get("geo", {})
        about = ld.get("about", {})
        out["page_title_name"] = about.get("name")
        offers = about.get("offers", {})
        out["ld_price"] = offers.get("price")
        out["ld_valid_from"] = offers.get("validFrom")
        avail = offers.get("availability", "")
        out["ld_availability"] = avail.rsplit('/', 1)[-1] if avail else None

    out["latitude"] = geo.get("latitude")
    out["longitude"] = geo.get("longitude")

    if listing:
        pd = listing.get("propertyDetails") or {}
        addr = pd.get("address") or {}
        out["address_street"] = addr.get("street")
        out["unit"] = addr.get("displayUnit")
        out["city"] = (addr.get("city") or "").title() or None
        out["state"] = addr.get("state")
        out["zip"] = addr.get("zipCode")
        out["full_address"] = listing.get("listingAddress")
        out["status"] = listing.get("status")
        out["listed_date"] = listing.get("onMarketAt")
        out["days_on_market"] = listing.get("daysOnMarket")
        out["available_date"] = listing.get("availableAt")
        out["off_market_date"] = listing.get("offMarketAt")
        out["created_at"] = listing.get("createdAt")
        out["updated_at"] = listing.get("updatedAt")
        desc = listing.get("description")
        m = re.fullmatch(r'\$([0-9a-f]{1,4})', desc or "")
        if m:
            # RSC text row: "<id>:T<hexlen>,<text...>"
            tm = re.search(re.escape(m.group(1)) + r':T([0-9a-f]+),', joined)
            if tm:
                start = tm.end()
                length = int(tm.group(1), 16)  # UTF-8 byte length
                raw = joined[start:start + length].encode("utf-8")[:length]
                desc = raw.decode("utf-8", errors="ignore").strip()
            else:
                desc = None
        out["description"] = desc
        out["rooms"] = pd.get("roomCount")
        out["bedrooms"] = pd.get("bedroomCount")
        out["full_baths"] = pd.get("fullBathroomCount")
        out["half_baths"] = pd.get("halfBathroomCount")
        fb = pd.get("fullBathroomCount"); hb = pd.get("halfBathroomCount")
        out["baths"] = (fb or 0) + 0.5 * (hb or 0) if fb is not None else None
        out["sqft"] = pd.get("livingAreaSize")
        am = pd.get("amenities") or {}
        out["building_amenities"] = sorted(titlecase_enum(a) for a in am.get("list") or [])
        out["doorman_types"] = [titlecase_enum(a) for a in am.get("doormanTypes") or []]
        out["parking_types"] = [titlecase_enum(a) for a in am.get("parkingTypes") or []]
        out["shared_outdoor_space"] = [titlecase_enum(a) for a in am.get("sharedOutdoorSpaceTypes") or []]
        out["storage_types"] = [titlecase_enum(a) for a in am.get("storageSpaceTypes") or []]
        ft = pd.get("features") or {}
        out["unit_features"] = sorted(titlecase_enum(a) for a in ft.get("list") or [])
        out["private_outdoor_space"] = [titlecase_enum(a) for a in ft.get("privateOutdoorSpaceTypes") or []]
        out["views"] = [titlecase_enum(a) for a in ft.get("views") or []]
        out["fireplace_types"] = [titlecase_enum(a) for a in ft.get("fireplaceTypes") or []]

        pr = listing.get("pricing") or {}
        out["rent"] = pr.get("price")
        out["net_effective_rent"] = pr.get("netEffectiveRent")
        out["months_free"] = pr.get("monthsFree")
        out["lease_term_months"] = pr.get("leaseTermMonths")
        dep = pr.get("securityDeposit")
        if dep is None:
            for f in pr.get("moveInFees") or []:
                if (f.get("typeLabel") or "").lower() == "security deposit":
                    calc = f.get("calculation") or {}
                    dep = calc.get("feeQuantifier")
                    break
        out["security_deposit"] = dep
        out["total_monthly_price"] = pr.get("totalMonthlyPrice")
        out["price_changes"] = [
            {"price": c.get("price"), "date": (c.get("changedAt") or "")[:10]}
            for c in pr.get("priceChanges") or []]
        fees = []
        for f in (pr.get("moveInFees") or []) + (pr.get("monthlyFees") or []) + (pr.get("additionalFees") or []):
            calc = f.get("calculation") or {}
            amt = calc.get("feeQuantifier")
            label = f.get("typeLabel") or "Fee"
            if calc.get("calculationType") == "PERCENTAGE" and amt is not None:
                fees.append(f"{label}: {amt}%")
            elif amt is not None:
                fees.append(f"{label}: ${amt:,.0f}".replace(".0%", "%"))
            else:
                fees.append(label)
        out["fees"] = fees

        leg = (listing.get("legacy") or {})
        lic = leg.get("license") or {}
        out["brokerage"] = leg.get("sourceGroupLabel")
        out["broker_license_name"] = lic.get("businessName")
        out["broker_license_type"] = lic.get("licenseType")
        laddr = lic.get("address") or {}
        if laddr.get("street"):
            out["broker_address"] = ", ".join(x for x in [
                laddr.get("street"), laddr.get("displayUnit"), laddr.get("city"),
                laddr.get("state"), laddr.get("zipCode")] if x)

        media = listing.get("media") or {}
        photos = media.get("photos") or []
        out["photo_count"] = len(photos)
        if photos:
            out["photo_url"] = f"https://photos.zillowstatic.com/fp/{photos[0]['key']}-se_large_800_400.webp"
        out["video_count"] = len(media.get("videos") or [])
        out["tour_3d_url"] = media.get("tour3dUrl")
        out["floorplan_count"] = len(media.get("floorPlans") or [])
        out["mls_number"] = listing.get("mlsNumber")
        src = listing.get("listingSource") or {}
        out["listing_source_type"] = src.get("sourceType")
        out["open_houses"] = listing.get("upcomingOpenHouses") or []
        out["canonical_url"] = "https://streeteasy.com" + (listing.get("urlPath") or f"/rental/{listing_id}")

        hist = []
        for h in listing.get("propertyHistory") or []:
            for ev in h.get("rentalEventsOfInterest") or []:
                hist.append({"date": ev.get("date"), "price": ev.get("price"),
                             "status": ev.get("status"), "listing_id": h.get("listingId"),
                             "source": h.get("sourceGroupLabel")})
        out["unit_history"] = sorted(hist, key=lambda x: x["date"] or "", reverse=True)

        stats = (listing.get("recentListingsPriceStats") or {}).get("rentalPriceStats") or {}
        out["area_median_rent_same_beds"] = stats.get("medianPrice")

    if building:
        out["building_name"] = building.get("name")
        area = building.get("area") or {}
        out["neighborhood"] = area.get("name")
        out["building_floors"] = building.get("floorCount")
        out["building_units"] = building.get("residentialUnitCount")
        out["year_built"] = building.get("yearBuilt")
        out["building_slug"] = building.get("slug")

    # buildingType / formattedBuildingType
    m = re.search(r'"formattedBuildingType":"((?:[^"\\]|\\.)*)"', joined)
    if m: out["unit_type_display"] = json.loads('"' + m.group(1) + '"')
    m = re.search(r'"buildingType":"((?:[^"\\]|\\.)*)"[^}]*"isPremium"', joined)
    if m: out["unit_type"] = json.loads('"' + m.group(1) + '"')

    # Broker fee: FARE Act (2025) — tenant owes none unless they hired the broker.
    # Flag any fee whose label mentions "broker".
    out["broker_fee"] = "; ".join(f for f in out.get("fees", []) if "broker" in f.lower()) or None

    # Borough guess from zip
    z = out.get("zip") or ""
    borough = None
    if z.startswith("100") or z.startswith("101") or z.startswith("102"): borough = "Manhattan"
    elif z.startswith("112"): borough = "Brooklyn"
    elif z.startswith("104"): borough = "Bronx"
    elif z.startswith("111") or z.startswith("113") or z.startswith("114") or z.startswith("116"): borough = "Queens"
    elif z.startswith("103"): borough = "Staten Island"
    out["borough"] = borough

    return out


def main():
    ids = [f[:-5] for f in sorted(os.listdir(PAGES)) if f.endswith(".html")]
    rows = []
    for lid in ids:
        try:
            rows.append(parse_page(os.path.join(PAGES, lid + ".html"), lid))
        except Exception as e:
            print(f"ERROR {lid}: {e}", file=sys.stderr)
            rows.append({"listing_id": lid, "parse_error": str(e)})
    with open(os.path.join(SCRATCH, "listings.json"), "w") as f:
        json.dump(rows, f, indent=1)
    # Coverage report
    fields = ["full_address", "neighborhood", "rent", "bedrooms", "baths", "sqft",
              "listed_date", "available_date", "brokerage", "latitude", "unit_type",
              "year_built", "days_on_market", "status", "description"]
    print(f"{len(rows)} listings parsed")
    for fld in fields:
        missing = [r["listing_id"] for r in rows if r.get(fld) in (None, "", [])]
        print(f"  {fld}: {len(rows)-len(missing)}/{len(rows)} filled" +
              (f"  missing: {','.join(missing[:8])}" if missing else ""))

if __name__ == "__main__":
    main()
