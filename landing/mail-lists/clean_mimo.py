#!/usr/bin/env python3
"""Clean miamishores_mimo.csv and backfill from MiMo area."""

import csv
import io
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(HERE, "miamishores_mimo.csv")
OUTPUT_FILE = os.path.join(HERE, "miamishores_mimo.csv")
V36_BROWARD = os.path.join(HERE, "broward_v36.csv")
V36_PALMBEACH = os.path.join(HERE, "palmbeach_v36.csv")

DBPR_URL = "https://www2.myfloridalicense.com/sto/file_download/extracts/hrfood1.csv"

# Patterns for non-restaurants to remove
REMOVE_PATTERNS = [
    # Gyms/fitness
    (re.compile(r'\b(ATHLETIC|FITNESS|GYM|CROSSFIT|YOGA|PILATES)\b', re.I), "gym/fitness"),
    # Hospitals/medical
    (re.compile(r'\b(HOSPITAL|MEDICAL|HEALTH\s*CENTER|CLINIC)\b', re.I), "hospital/medical"),
    # Schools/education
    (re.compile(r'\b(SCHOOL|UNIVERSITY|COLLEGE|ACADEMY|LEARNING)\b', re.I), "school"),
    # Churches/religious
    (re.compile(r'\b(CHURCH|TEMPLE|MOSQUE|SYNAGOGUE|CHAPEL)\b', re.I), "church"),
    # Hotels (employee cafeterias)
    (re.compile(r'\b(HOTEL|INN\b|SUITES|MOTEL|RESORT)\b', re.I), "hotel"),
    # Convenience stores/gas stations
    (re.compile(r'\b(SUPERMARKET|CONVENIENCE|GAS\s*STATION|SHELL|CHEVRON|BP|EXXON|MOBIL|7.?ELEVEN|WAWA|CIRCLE\s*K)\b', re.I), "convenience/gas"),
    # Caterers with no dining room
    (re.compile(r'\b(CATERING|CATERER|SPECIAL\s*EVENTS|CULINARY\s*GROUP|MANAGEMENT\s*SPECIALISTS|EUREST|ARAMARK|SODEXO|COMPASS\s*GROUP)\b', re.I), "caterer"),
    # National fast-food chains
    (re.compile(r'\b(MCDONALD|BURGER\s*KING|WENDY|TACO\s*BELL|KFC|POPEYE|SUBWAY|DUNKIN|STARBUCKS|CHIPOTLE|CHICK.?FIL.?A|DOMINO|PAPA\s*JOHN|LITTLE\s*CAESAR|PIZZA\s*HUT|SONIC|ARBY|JACK\s*IN\s*THE\s*BOX|FIVE\s*GUYS|SHAKE\s*SHACK|PANERA|PANDA\s*EXPRESS|WINGSTOP|BUFFALO\s*WILD|CHECKERS|RALLY|JIMMY\s*JOHN|JERSEY\s*MIKE|FIREHOUSE|POLLO\s*TROPICAL|DOMINOS)\b', re.I), "fast-food chain"),
    # Food trucks
    (re.compile(r'\b(TRUCK|MOBILE\s*FOOD)\b', re.I), "food truck"),
    # Non-food businesses
    (re.compile(r'\b(PLANT\s*THE\s*FUTURE)\b', re.I), "non-restaurant"),
]

# Specific removals requested
SPECIFIC_REMOVALS = {
    "ATHLETICSFIT",
    "HSA HOSPITALS-NORTH SHORE MED CTR",
    "LITTLE CAESARS PIZZA #2298",
    "JIMMY JOHN",  # Also caught by pattern but be explicit
    "DOMINOS PIZZA",
}


def should_remove(company_name):
    """Check if company should be removed. Returns (should_remove, reason)."""
    name_upper = company_name.upper()

    # Check specific removals
    for specific in SPECIFIC_REMOVALS:
        if specific in name_upper:
            return True, "specifically requested"

    # Check patterns
    for pattern, reason in REMOVE_PATTERNS:
        if pattern.search(name_upper):
            return True, reason

    return False, None


def fetch_dbpr():
    """Fetch DBPR data for backfill."""
    print("  Fetching DBPR data for backfill...")
    req = urllib.request.Request(DBPR_URL, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=120).read().decode("latin-1")
    return list(csv.DictReader(io.StringIO(data)))


def extract_building_number(address):
    """Extract building number from address."""
    match = re.match(r'^(\d+)', address.strip())
    return int(match.group(1)) if match else 0


def normalize_address(address):
    """Normalize address for deduplication (Blvd vs Boulevard, etc.)."""
    addr = address.upper().strip()
    # Normalize abbreviations
    addr = re.sub(r'\bBOULEVARD\b', 'BLVD', addr)
    addr = re.sub(r'\bSTREET\b', 'ST', addr)
    addr = re.sub(r'\bAVENUE\b', 'AVE', addr)
    addr = re.sub(r'\bDRIVE\b', 'DR', addr)
    addr = re.sub(r'\bROAD\b', 'RD', addr)
    addr = re.sub(r'\bCOURT\b', 'CT', addr)
    addr = re.sub(r'\bSUITE\b', 'STE', addr)
    # Remove extra spaces
    addr = re.sub(r'\s+', ' ', addr)
    return addr


def make_addr_key(row):
    """Create normalized address key for deduplication."""
    addr = normalize_address(row.get('address_line1', ''))
    city = row.get('address_city', '').upper().strip()
    zip_code = row.get('address_zip', '')[:5]
    return f"{addr}|{city}|{zip_code}"


def main():
    print("=" * 60)
    print("Cleaning miamishores_mimo.csv")
    print("=" * 60)

    # Load current file
    with open(INPUT_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\nLoaded {len(rows)} rows")

    # Load V36 addresses to exclude (normalized)
    v36_addresses = set()
    for v36_file in [V36_BROWARD, V36_PALMBEACH]:
        if os.path.exists(v36_file):
            with open(v36_file, "r") as f:
                for row in csv.DictReader(f):
                    addr = normalize_address(row.get('address_line1', ''))
                    city = row.get('address_city', '').upper().strip()
                    zip_code = row.get('address_zip', '')[:5]
                    v36_addresses.add(f"{addr}|{city}|{zip_code}")

    # Deduplicate first (normalize addresses like Blvd vs Boulevard)
    seen_addresses = set()
    deduped_rows = []
    duplicates_removed = []
    for row in rows:
        addr_key = make_addr_key(row)
        if addr_key not in seen_addresses:
            seen_addresses.add(addr_key)
            deduped_rows.append(row)
        else:
            duplicates_removed.append(row["company"])

    if duplicates_removed:
        print(f"\n--- DUPLICATES REMOVED ({len(duplicates_removed)}) ---")
        for company in duplicates_removed:
            print(f"  {company}")

    rows = deduped_rows

    # Separate Miami Shores and MiMo
    miami_shores = [r for r in rows if r.get("segment") == "miami_shores"]
    mimo = [r for r in rows if r.get("segment") == "mimo"]

    print(f"\nAfter deduplication:")
    print(f"  Miami Shores: {len(miami_shores)}")
    print(f"  MiMo: {len(mimo)}")

    # Clean both lists
    removed = []

    clean_miami_shores = []
    for row in miami_shores:
        should_rm, reason = should_remove(row["company"])
        if should_rm:
            removed.append((row["company"], "miami_shores", reason))
        else:
            clean_miami_shores.append(row)

    clean_mimo = []
    for row in mimo:
        should_rm, reason = should_remove(row["company"])
        if should_rm:
            removed.append((row["company"], "mimo", reason))
        else:
            clean_mimo.append(row)

    print(f"\n--- REMOVED ({len(removed)}) ---")
    for company, segment, reason in removed:
        print(f"  [{segment}] {company} - {reason}")

    # Current count after removal
    clean_count = len(clean_miami_shores) + len(clean_mimo)
    need_backfill = 100 - clean_count

    print(f"\nAfter cleaning: {clean_count} rows")
    print(f"Need to backfill: {need_backfill}")

    # Backfill from MiMo (Biscayne Blvd NE 50th-87th = buildings 5000-8700)
    if need_backfill > 0:
        dbpr_rows = fetch_dbpr()

        # Track addresses we already have (normalized)
        existing_addresses = set()
        for row in clean_miami_shores + clean_mimo:
            addr_key = make_addr_key(row)
            existing_addresses.add(addr_key)

        # Also exclude V36 addresses (already normalized)
        existing_addresses.update(v36_addresses)

        backfill = []
        for row in dbpr_rows:
            if len(backfill) >= need_backfill:
                break

            # Normalize row
            row = {k.strip() if k else "": v.strip() if v else "" for k, v in row.items()}

            # Must be active
            status = row.get("Primary Status Code", "")
            if status != "20":
                continue

            address = row.get("Location Street Address", "").upper()
            zip_code = row.get("Location Zip Code", "")[:5]
            city = row.get("Location City", "")
            name = row.get("Business Name", "")

            # Must be in MiMo area (33137, 33138)
            if zip_code not in ("33137", "33138"):
                continue

            # Must be on Biscayne Blvd (5000-8700) or NE 2nd Ave (2200-8500)
            building_num = extract_building_number(address)
            if "BISCAYNE" in address:
                if not (5000 <= building_num <= 8700):
                    continue
            elif "NE 2" in address or "NE 2ND" in address or "N E 2" in address:
                if not (2200 <= building_num <= 8500):
                    continue
            elif "NE 1" in address or "NE 1ST" in address:
                # Also include NE 1st Ave (Midtown area)
                if not (3000 <= building_num <= 4200):
                    continue
            else:
                # Skip other streets
                continue

            # Check if should be removed
            should_rm, reason = should_remove(name)
            if should_rm:
                continue

            # Check for duplicate address (normalized)
            addr_key = f"{normalize_address(address)}|{city.upper()}|{zip_code}"
            if addr_key in existing_addresses:
                continue
            existing_addresses.add(addr_key)

            # Add to backfill
            backfill.append({
                "name": "Owner / General Manager",
                "company": name.title(),
                "address_line1": address.title(),
                "address_line2": row.get("Location Address Line 2", "").title(),
                "address_city": city.title(),
                "address_state": "FL",
                "address_zip": zip_code,
                "segment": "mimo"
            })

        print(f"\nBackfilled: {len(backfill)} restaurants from Biscayne Blvd (5000-8700)")
        if backfill:
            print("  New additions:")
            for row in backfill:
                print(f"    - {row['company']} ({row['address_line1']})")

        clean_mimo.extend(backfill)

    # Combine and write
    final_rows = clean_miami_shores + clean_mimo
    final_count = len(final_rows)

    print(f"\n--- FINAL COUNT: {final_count} ---")
    print(f"  Miami Shores: {len(clean_miami_shores)}")
    print(f"  MiMo: {len(clean_mimo)}")

    # Write output
    fieldnames = ["name", "company", "address_line1", "address_line2",
                  "address_city", "address_state", "address_zip", "segment"]

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"\nSaved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
