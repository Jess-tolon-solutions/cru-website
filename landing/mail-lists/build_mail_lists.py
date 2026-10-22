#!/usr/bin/env python3
"""
Build Lob-ready mailing lists for Ceilings R Us V36 direct mail campaign.

Sources:
  - contacts.csv: V36 history from ceilings-outreach repo (~743 restaurants)
  - DBPR licensee extract: live data for addresses, license status, county

Outputs:
  - broward_v36.csv: Broward restaurants from V36 history
  - palmbeach_v36.csv: Palm Beach restaurants from V36 history
  - miamishores_mimo.csv: Miami Shores + MiMo restaurants NOT in V36 (100 total)
"""

import csv
import io
import os
import re
import urllib.request
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CONTACTS_CSV = os.path.join(HERE, "..", "..", "ceilings-outreach", "contacts.csv")

DBPR_LICENSEE_URLS = {
    1: "https://www2.myfloridalicense.com/sto/file_download/extracts/hrfood1.csv",
    2: "https://www2.myfloridalicense.com/sto/file_download/extracts/hrfood2.csv",
}

USER_AGENT = "CeilingsRUs-MailList/1.0"

# Address expansion patterns
ADDRESS_EXPANSIONS = [
    (re.compile(r'\bSR\s+(\d)', re.I), r'State Road \1'),
    (re.compile(r'\bS\s+SR\s+(\d)', re.I), r'South State Road \1'),
    (re.compile(r'\bN\s+SR\s+(\d)', re.I), r'North State Road \1'),
    (re.compile(r'\bE\s+SR\s+(\d)', re.I), r'East State Road \1'),
    (re.compile(r'\bW\s+SR\s+(\d)', re.I), r'West State Road \1'),
    (re.compile(r'\bST\b', re.I), 'Street'),
    (re.compile(r'\bAVE\b', re.I), 'Avenue'),
    (re.compile(r'\bBLVD\b', re.I), 'Boulevard'),
    (re.compile(r'\bDR\b', re.I), 'Drive'),
    (re.compile(r'\bRD\b', re.I), 'Road'),
    (re.compile(r'\bCT\b', re.I), 'Court'),
    (re.compile(r'\bPL\b', re.I), 'Place'),
    (re.compile(r'\bLN\b', re.I), 'Lane'),
    (re.compile(r'\bPKWY\b', re.I), 'Parkway'),
    (re.compile(r'\bHWY\b', re.I), 'Highway'),
    (re.compile(r'\bTER\b', re.I), 'Terrace'),
    (re.compile(r'\bCIR\b', re.I), 'Circle'),
    (re.compile(r'\bNE\b'), 'NE'),  # Keep directionals as-is
    (re.compile(r'\bNW\b'), 'NW'),
    (re.compile(r'\bSE\b'), 'SE'),
    (re.compile(r'\bSW\b'), 'SW'),
]

# Fast food / chain patterns to skip for MiMo
FAST_FOOD_CHAINS = re.compile(
    r'\b(MCDONALD|BURGER KING|WENDY|TACO BELL|KFC|POPEYE|SUBWAY|DUNKIN|'
    r'STARBUCKS|CHIPOTLE|CHICK-?FIL-?A|DOMINO|PAPA JOHN|LITTLE CAESAR|'
    r'PIZZA HUT|SONIC|ARBY|JACK IN THE BOX|FIVE GUYS|SHAKE SHACK|'
    r'PANERA|PANDA EXPRESS|WINGSTOP|BUFFALO WILD|CHECKERS|RALLY|'
    r'JIMMY JOHN|JERSEY MIKE|FIREHOUSE|TROPICAL SMOOTHIE|SMOOTHIE KING|'
    r'AUNTIE ANNE|CINNABON|KRISPY KREME|DAIRY QUEEN|BASKIN|COLDSTONE|'
    r'7-?ELEVEN|WAWA|CIRCLE K|SHELL|CHEVRON|BP|EXXON|MOBIL|'
    r'CVS|WALGREEN|PUBLIX|WINN-?DIXIE|WHOLE FOODS)\b', re.I)


def fetch_csv(url):
    """Download and parse a DBPR CSV extract."""
    print(f"  Fetching: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    data = urllib.request.urlopen(req, timeout=120).read().decode("latin-1", errors="replace")
    return list(csv.DictReader(io.StringIO(data)))


def normalize_header(row):
    """Normalize column names (DBPR has inconsistent spacing)."""
    return {k.strip() if k else "": v.strip() if v else "" for k, v in row.items()}


def expand_address(addr):
    """Expand DBPR shorthand in addresses."""
    if not addr:
        return ""
    result = addr
    for pattern, replacement in ADDRESS_EXPANSIONS:
        result = pattern.sub(replacement, result)
    return result.title()


def extract_street_number(address):
    """Extract street number from NE/NW address for Miami Shores filtering."""
    match = re.search(r'\b(NE|NW)\s+(\d+)', address, re.I)
    if match:
        return int(match.group(2))
    return None


def extract_building_number(address):
    """Extract building/house number from address for MiMo filtering."""
    match = re.match(r'^(\d+)', address.strip())
    if match:
        return int(match.group(1))
    return None


def is_active_license(status_code, expiry_date):
    """Check if license is currently active."""
    if not status_code:
        return False
    # DBPR status codes: 20 = Active, 45/46 = likely inactive/expired
    # Also check expiry date if available
    if status_code in ("20", "AC", "CU", "ACT", "A"):
        # If expiry date is provided, verify it's in the future
        if expiry_date:
            try:
                from datetime import datetime
                exp = datetime.strptime(expiry_date, "%m/%d/%Y")
                if exp < datetime.now():
                    return False
            except:
                pass  # Can't parse date, assume active
        return True
    return False


def create_lob_row(name, address, address2, city, state, zip_code, segment=None):
    """Create a Lob-ready row."""
    row = {
        "name": "Owner / General Manager",
        "company": name.title() if name else "",
        "address_line1": expand_address(address) if address else "",
        "address_line2": expand_address(address2) if address2 else "",
        "address_city": city.title() if city else "",
        "address_state": state.upper() if state else "FL",
        "address_zip": zip_code[:5] if zip_code else ""
    }
    if segment:
        row["segment"] = segment
    return row


def is_valid_address(row):
    """Check if address is valid for mailing."""
    if not row["address_line1"] or not row["address_city"] or not row["address_zip"]:
        return False
    if len(row["address_zip"]) < 5:
        return False
    if "PO BOX" in row["address_line1"].upper():
        return False
    return True


def main():
    print("=" * 70)
    print("Building Lob-ready mailing lists for V36 campaign")
    print("=" * 70)

    # Tracking
    dropped = {
        "no_dbpr_match": [],
        "license_expired": [],
        "permanently_closed": [],
        "bad_address": [],
        "duplicate": [],
        "not_broward_palmbeach": [],
    }

    # -------------------------------------------------------------------------
    # STEP 1: Load V36 history from contacts.csv
    # -------------------------------------------------------------------------
    print(f"\n[STEP 1] Loading V36 history from contacts.csv...")
    print(f"  Source: {CONTACTS_CSV}")

    if not os.path.exists(CONTACTS_CSV):
        print(f"  ERROR: contacts.csv not found at {CONTACTS_CSV}")
        print("  Please ensure ceilings-outreach repo is cloned next to cru-website")
        return

    with open(CONTACTS_CSV, "r", encoding="utf-8-sig") as f:
        contacts = list(csv.DictReader(f))

    print(f"  Loaded {len(contacts)} V36 restaurants")

    # Build lookup by license number
    v36_by_license = {}
    for row in contacts:
        license_num = row.get("License", "").strip()
        if license_num:
            v36_by_license[license_num] = row

    # -------------------------------------------------------------------------
    # STEP 2: Fetch DBPR licensee extracts
    # -------------------------------------------------------------------------
    print(f"\n[STEP 2] Fetching DBPR licensee extracts...")

    dbpr_by_license = {}
    for district, url in DBPR_LICENSEE_URLS.items():
        rows = fetch_csv(url)
        print(f"    District {district}: {len(rows)} licenses")
        for row in rows:
            row = normalize_header(row)
            license_num = row.get("License Number", "").strip()
            if license_num:
                # DBPR uses "SEA1234567" format, contacts.csv uses "1234567"
                # Store by numeric part for matching
                numeric_license = license_num.replace("SEA", "").strip()
                dbpr_by_license[numeric_license] = row

    print(f"  Total DBPR licenses: {len(dbpr_by_license)}")

    # -------------------------------------------------------------------------
    # STEP 3: Join and filter for V36 lists
    # -------------------------------------------------------------------------
    print(f"\n[STEP 3] Joining V36 history with DBPR data...")

    broward_v36 = []
    palmbeach_v36 = []
    v36_addresses = set()  # For exclusion in Miami Shores/MiMo
    seen_addresses = set()  # For deduplication

    for license_num, contact in v36_by_license.items():
        restaurant = contact.get("Restaurant", "").strip()
        business_status = contact.get("Business Status", "").strip().upper()

        # Filter: permanently closed
        if "CLOSED" in business_status and "PERMANENTLY" in business_status:
            dropped["permanently_closed"].append(f"{restaurant} (License: {license_num})")
            continue

        # Filter: must have DBPR match
        dbpr = dbpr_by_license.get(license_num)
        if not dbpr:
            dropped["no_dbpr_match"].append(f"{restaurant} (License: {license_num})")
            continue

        # Filter: license must be active
        status = dbpr.get("Primary Status Code", "")
        expiry = dbpr.get("License Expiry Date", "")
        if not is_active_license(status, expiry):
            dropped["license_expired"].append(f"{restaurant} (License: {license_num}, Status: {status})")
            continue

        # Get location address (NOT mailing address)
        address = dbpr.get("Location Street Address", "").strip()
        address2 = dbpr.get("Location Address Line 2", "").strip()
        city = dbpr.get("Location City", "").strip()
        state = dbpr.get("Location State Code", "").strip() or "FL"
        zip_code = dbpr.get("Location Zip Code", "").strip()
        county = dbpr.get("Location County", "").strip().upper()

        # Use DBA name from DBPR (more accurate than contacts.csv)
        dba_name = dbpr.get("Business Name", "").strip() or restaurant

        # Create address key for deduplication
        addr_key = f"{address}|{city}|{zip_code}".upper()

        # Filter: valid address
        lob_row = create_lob_row(dba_name, address, address2, city, state, zip_code)
        if not is_valid_address(lob_row):
            dropped["bad_address"].append(f"{dba_name} ({address}, {city})")
            continue

        # Filter: dedupe by street address
        if addr_key in seen_addresses:
            dropped["duplicate"].append(f"{dba_name} ({address})")
            continue
        seen_addresses.add(addr_key)
        v36_addresses.add(addr_key)

        # Route to correct county file
        if county == "BROWARD":
            broward_v36.append(lob_row)
        elif county == "PALM BEACH":
            palmbeach_v36.append(lob_row)
        else:
            dropped["not_broward_palmbeach"].append(f"{dba_name} (County: {county})")

    print(f"  Broward V36: {len(broward_v36)} restaurants")
    print(f"  Palm Beach V36: {len(palmbeach_v36)} restaurants")

    # -------------------------------------------------------------------------
    # STEP 4: Build Miami Shores / MiMo list
    # -------------------------------------------------------------------------
    print(f"\n[STEP 4] Building Miami Shores / MiMo list...")

    miami_shores = []
    mimo = []

    # Filter District 1 (Miami-Dade) for Miami Shores and MiMo
    d1_rows = fetch_csv(DBPR_LICENSEE_URLS[1])

    for row in d1_rows:
        row = normalize_header(row)
        license_num = row.get("License Number", "").strip()
        # DBPR uses "SEA1234567" format, contacts.csv uses "1234567"
        numeric_license = license_num.replace("SEA", "").strip()

        # Skip if in V36 list
        if numeric_license in v36_by_license:
            continue

        # Must be active license
        status = row.get("Primary Status Code", "")
        if not is_active_license(status, ""):
            continue

        # Get location info
        address = row.get("Location Street Address", "").strip()
        address2 = row.get("Location Address Line 2", "").strip()
        city = row.get("Location City", "").strip().upper()
        zip_code = row.get("Location Zip Code", "").strip()[:5]
        dba_name = row.get("Business Name", "").strip()

        # Skip chains/fast food for cleaner list
        if FAST_FOOD_CHAINS.search(dba_name):
            continue

        # Create address key for deduplication
        addr_key = f"{address}|{city}|{zip_code}".upper()
        if addr_key in v36_addresses or addr_key in seen_addresses:
            continue

        lob_row = create_lob_row(dba_name, address, address2, city, "FL", zip_code)
        if not is_valid_address(lob_row):
            continue

        # Miami Shores: NE/NW streets between NE 87th and NE 107th in zips 33138, 33150, 33153
        # Note: Many Miami Shores addresses list city as "MIAMI" not "MIAMI SHORES"
        street_num = extract_street_number(address)
        building_num = extract_building_number(address)

        if zip_code in ("33138", "33150", "33153"):
            # Check for NE/NW street pattern (87-107)
            if street_num and 87 <= street_num <= 107:
                lob_row["segment"] = "miami_shores"
                miami_shores.append(lob_row)
                seen_addresses.add(addr_key)
                continue
            # Also check building numbers in 8700-10700 range (maps to NE 87th-107th area)
            if building_num and 8700 <= building_num <= 10700:
                if "NE" in address.upper() or "NW" in address.upper():
                    lob_row["segment"] = "miami_shores"
                    miami_shores.append(lob_row)
                    seen_addresses.add(addr_key)
                    continue

        # MiMo: Biscayne Blvd and NE/NW streets in zips 33137, 33138
        # Prioritize Biscayne Blvd (insert at front), then NE/NW streets
        if zip_code in ("33137", "33138"):
            addr_upper = address.upper()
            if "BISCAYNE" in addr_upper:
                # Biscayne Blvd - primary MiMo area (all buildings)
                lob_row["segment"] = "mimo"
                mimo.insert(0, lob_row)  # Priority
                seen_addresses.add(addr_key)
            elif ("NE" in addr_upper or "NW" in addr_upper) and building_num:
                # NE/NW streets in Upper East Side / MiMo area (2000-9000)
                if 2000 <= building_num <= 9000:
                    lob_row["segment"] = "mimo"
                    mimo.append(lob_row)
                    seen_addresses.add(addr_key)

    print(f"  Miami Shores: {len(miami_shores)} restaurants")
    print(f"  MiMo: {len(mimo)} restaurants")

    # Combine to target 100
    miamishores_mimo = miami_shores[:]
    remaining = 100 - len(miamishores_mimo)
    miamishores_mimo.extend(mimo[:remaining])

    miami_shores_count = len(miami_shores)
    mimo_count = len(miamishores_mimo) - miami_shores_count

    if len(miamishores_mimo) < 100:
        print(f"  WARNING: Only {len(miamishores_mimo)} found, target was 100")

    # -------------------------------------------------------------------------
    # STEP 5: Write CSV files
    # -------------------------------------------------------------------------
    print(f"\n[STEP 5] Writing CSV files...")

    lob_columns = ["name", "company", "address_line1", "address_line2",
                   "address_city", "address_state", "address_zip"]

    # Broward
    broward_path = os.path.join(HERE, "broward_v36.csv")
    with open(broward_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=lob_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(broward_v36)
    print(f"  {broward_path}: {len(broward_v36)} rows")

    # Palm Beach
    palmbeach_path = os.path.join(HERE, "palmbeach_v36.csv")
    with open(palmbeach_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=lob_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(palmbeach_v36)
    print(f"  {palmbeach_path}: {len(palmbeach_v36)} rows")

    # Miami Shores + MiMo
    mimo_path = os.path.join(HERE, "miamishores_mimo.csv")
    with open(mimo_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=lob_columns + ["segment"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(miamishores_mimo)
    print(f"  {mimo_path}: {len(miamishores_mimo)} rows")

    # -------------------------------------------------------------------------
    # FINAL REPORT
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)

    print(f"\nSource files:")
    print(f"  V36 History: {CONTACTS_CSV}")
    print(f"  DBPR District 1: {DBPR_LICENSEE_URLS[1]}")
    print(f"  DBPR District 2: {DBPR_LICENSEE_URLS[2]}")

    print(f"\nRow counts:")
    print(f"  broward_v36.csv:      {len(broward_v36)} rows")
    print(f"  palmbeach_v36.csv:    {len(palmbeach_v36)} rows")
    print(f"  miamishores_mimo.csv: {len(miamishores_mimo)} rows")
    print(f"    - Miami Shores:     {miami_shores_count}")
    print(f"    - MiMo:             {mimo_count}")

    print(f"\nRows dropped per filter:")
    for reason, items in dropped.items():
        print(f"  {reason}: {len(items)}")

    # Show samples of dropped rows
    for reason, items in dropped.items():
        if items:
            print(f"\n  Sample {reason}:")
            for item in items[:3]:
                print(f"    - {item}")

    # List Miami Shores restaurant names
    if miami_shores:
        print(f"\nMiami Shores restaurants ({len(miami_shores)}):")
        for row in miami_shores:
            print(f"  - {row['company']}")

    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)


if __name__ == "__main__":
    main()
