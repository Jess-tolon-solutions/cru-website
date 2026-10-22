#!/usr/bin/env python3
"""Build client-ready Excel file for Jonathan to review."""

import csv
import os
import re
from openpyxl import Workbook
from openpyxl.styles import Font, Fill, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(HERE, "Ceilings-R-Us_Direct-Mail-List_Oct-2026.xlsx")

# Colors
HEADER_FILL = PatternFill(start_color="116782", end_color="116782", fill_type="solid")
ZEBRA_FILL = PatternFill(start_color="EEF5F7", end_color="EEF5F7", fill_type="solid")
TITLE_COLOR = "116782"

# Borders
THIN_BORDER = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)

# Fonts
HEADER_FONT = Font(name='Arial', size=10, bold=True, color='FFFFFF')
DATA_FONT = Font(name='Arial', size=10)
TITLE_FONT = Font(name='Arial', size=14, bold=True, color=TITLE_COLOR)
SUBTITLE_FONT = Font(name='Arial', size=11, color='666666')


def clean_name(name):
    """Clean up restaurant name: Title Case, fix LLC/Inc."""
    # Title case
    name = name.strip().title()
    # Fix common suffixes
    name = re.sub(r'\bLlc\b', 'LLC', name)
    name = re.sub(r'\bInc\b', 'Inc.', name)
    name = re.sub(r'\bCorp\b', 'Corp.', name)
    name = re.sub(r"'S\b", "'s", name)  # Fix possessives
    name = re.sub(r"'S\b", "'s", name)
    return name


def get_miami_neighborhood(address, city, segment):
    """Determine Miami neighborhood based on address."""
    if segment == "miami_shores":
        return "Miami Shores"

    address_upper = address.upper()

    # Extract building number
    match = re.match(r'^(\d+)', address.strip())
    building_num = int(match.group(1)) if match else 0

    # Design District: NE 36th-41st St area, NE 2nd Ave 3600-4200
    if "NE 2" in address_upper or "NE 1" in address_upper:
        if 3600 <= building_num <= 4200:
            return "Design District"
        elif 2200 <= building_num <= 3599:
            return "Midtown"
        elif 4201 <= building_num <= 5800:
            return "MiMo–Upper East Side"
        elif building_num > 5800:
            return "MiMo–Upper East Side"

    # Biscayne Blvd
    if "BISCAYNE" in address_upper:
        if building_num < 5000:
            return "Midtown"
        elif 5000 <= building_num <= 6200:
            return "MiMo–Upper East Side"
        elif building_num > 6200:
            return "MiMo–Upper East Side"

    # Default based on zip
    city_upper = city.upper()
    if "MIAMI SHORES" in city_upper:
        return "Miami Shores"

    return "MiMo–Upper East Side"


def apply_header_style(cell):
    """Apply header styling to a cell."""
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = Alignment(horizontal='left', vertical='center')
    cell.border = THIN_BORDER


def apply_data_style(cell, row_num):
    """Apply data styling with zebra striping."""
    cell.font = DATA_FONT
    cell.alignment = Alignment(horizontal='left', vertical='center')
    cell.border = THIN_BORDER
    if row_num % 2 == 0:
        cell.fill = ZEBRA_FILL


def auto_fit_columns(ws):
    """Auto-fit column widths."""
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width


def setup_page(ws):
    """Setup page for printing."""
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = '1:1'
    ws.freeze_panes = 'A2'


def load_csv(filename):
    """Load CSV file."""
    filepath = os.path.join(HERE, filename)
    with open(filepath, 'r') as f:
        return list(csv.DictReader(f))


def main():
    print("Building Excel file...")

    # Load data
    broward = load_csv("broward_v36.csv")
    palmbeach = load_csv("palmbeach_v36.csv")
    miami = load_csv("miamishores_mimo.csv")

    print(f"  Broward: {len(broward)} rows")
    print(f"  Palm Beach: {len(palmbeach)} rows")
    print(f"  Miami: {len(miami)} rows")

    # Removed items (from clean_mimo.py run)
    removed = [
        ("Jimmy Johns", "Fast-food chain"),
        ("Dominos Pizza #8635", "Fast-food chain"),
        ("Dominos Pizza #8635", "Fast-food chain (duplicate)"),
        ("Moshi Moshi", "Duplicate"),
        ("Dogma Grill", "Duplicate"),
        ("Pinch Kitchen", "Duplicate"),
        ("Gold Rush", "Duplicate"),
        ("Doggi's Arepa Bar", "Duplicate"),
        ("Luna Pasta E Dolci", "Duplicate"),
        ("Osteria", "Duplicate"),
        ("El Bagel", "Duplicate"),
        ("New Yorker", "Duplicate"),
        ("Uptown 66 Taqueria", "Duplicate"),
        ("Caracas Bakery", "Duplicate"),
        ("Charruas Grill", "Duplicate"),
        ("Chicken Kitchen", "Duplicate"),
        ("Luna Pasta E Dolci", "Duplicate"),
    ]

    # Create workbook
    wb = Workbook()

    # =========== TAB 1: SUMMARY ===========
    ws_summary = wb.active
    ws_summary.title = "Summary"

    # Title
    ws_summary['A1'] = "Ceilings R Us — Direct Mail Pilot"
    ws_summary['A1'].font = TITLE_FONT
    ws_summary['A2'] = "Mailing list for review · October 2026"
    ws_summary['A2'].font = SUBTITLE_FONT

    # Table header row
    headers = ["List", "Promo Code", "QR Destination", "Cards", "Est. Cost"]
    for col, header in enumerate(headers, 1):
        cell = ws_summary.cell(row=4, column=col, value=header)
        apply_header_style(cell)

    # Data rows
    cost_per_card = 1.026
    data = [
        ("Broward", "MAIL10-BRO", "ceilingsrus.net/mail-bro", len(broward)),
        ("Palm Beach", "MAIL10-PB", "ceilingsrus.net/mail-pb", len(palmbeach)),
        ("Miami Shores + MiMo", "MAIL10-MIA", "ceilingsrus.net/mail-mia", len(miami)),
    ]

    for row_num, (list_name, promo, qr, count) in enumerate(data, 5):
        ws_summary.cell(row=row_num, column=1, value=list_name)
        ws_summary.cell(row=row_num, column=2, value=promo)
        ws_summary.cell(row=row_num, column=3, value=qr)
        ws_summary.cell(row=row_num, column=4, value=count)
        cost_cell = ws_summary.cell(row=row_num, column=5)
        cost_cell.value = count * cost_per_card
        cost_cell.number_format = '"$"#,##0.00'

        for col in range(1, 6):
            apply_data_style(ws_summary.cell(row=row_num, column=col), row_num)

    # Total row
    total_row = 8
    ws_summary.cell(row=total_row, column=1, value="Total")
    ws_summary.cell(row=total_row, column=1).font = Font(name='Arial', size=10, bold=True)
    ws_summary.cell(row=total_row, column=4, value=f"=SUM(D5:D7)")
    ws_summary.cell(row=total_row, column=5, value=f"=SUM(E5:E7)")
    ws_summary.cell(row=total_row, column=5).number_format = '"$"#,##0.00'
    for col in range(1, 6):
        cell = ws_summary.cell(row=total_row, column=col)
        cell.border = THIN_BORDER
        cell.font = Font(name='Arial', size=10, bold=True)

    # Miami breakdown
    miami_shores_count = len([r for r in miami if r.get('segment') == 'miami_shores'])
    mimo_count = len([r for r in miami if r.get('segment') == 'mimo'])

    ws_summary['A10'] = "Miami Shores + MiMo breakdown:"
    ws_summary['A10'].font = Font(name='Arial', size=10, bold=True)
    ws_summary['A11'] = f"  Miami Shores: {miami_shores_count}"
    ws_summary['A11'].font = DATA_FONT
    ws_summary['A12'] = f"  MiMo / Upper East Side / Design District / Midtown: {mimo_count}"
    ws_summary['A12'].font = DATA_FONT

    ws_summary['A14'] = "Mailed First-Class via Lob to the restaurant's business address, Attn: Owner / General Manager."
    ws_summary['A14'].font = Font(name='Arial', size=10, italic=True)

    auto_fit_columns(ws_summary)
    ws_summary.column_dimensions['A'].width = 25
    ws_summary.column_dimensions['C'].width = 30

    # =========== TAB 2: BROWARD ===========
    ws_broward = wb.create_sheet("Broward")
    headers = ["#", "Restaurant", "Street Address", "Suite/Unit", "City", "Zip"]
    for col, header in enumerate(headers, 1):
        cell = ws_broward.cell(row=1, column=col, value=header)
        apply_header_style(cell)

    # Sort by City, then Restaurant
    broward_sorted = sorted(broward, key=lambda x: (x.get('address_city', '').upper(), x.get('company', '').upper()))

    for row_num, row in enumerate(broward_sorted, 2):
        ws_broward.cell(row=row_num, column=1, value=row_num - 1)
        ws_broward.cell(row=row_num, column=2, value=clean_name(row.get('company', '')))
        ws_broward.cell(row=row_num, column=3, value=row.get('address_line1', '').title())
        ws_broward.cell(row=row_num, column=4, value=row.get('address_line2', '').title())
        ws_broward.cell(row=row_num, column=5, value=row.get('address_city', '').title())
        ws_broward.cell(row=row_num, column=6, value=row.get('address_zip', '')[:5])

        for col in range(1, 7):
            apply_data_style(ws_broward.cell(row=row_num, column=col), row_num)

    ws_broward.auto_filter.ref = ws_broward.dimensions
    auto_fit_columns(ws_broward)
    setup_page(ws_broward)

    # =========== TAB 3: PALM BEACH ===========
    ws_pb = wb.create_sheet("Palm Beach")
    headers = ["#", "Restaurant", "Street Address", "Suite/Unit", "City", "Zip"]
    for col, header in enumerate(headers, 1):
        cell = ws_pb.cell(row=1, column=col, value=header)
        apply_header_style(cell)

    # Sort by City, then Restaurant
    pb_sorted = sorted(palmbeach, key=lambda x: (x.get('address_city', '').upper(), x.get('company', '').upper()))

    for row_num, row in enumerate(pb_sorted, 2):
        ws_pb.cell(row=row_num, column=1, value=row_num - 1)
        ws_pb.cell(row=row_num, column=2, value=clean_name(row.get('company', '')))
        ws_pb.cell(row=row_num, column=3, value=row.get('address_line1', '').title())
        ws_pb.cell(row=row_num, column=4, value=row.get('address_line2', '').title())
        ws_pb.cell(row=row_num, column=5, value=row.get('address_city', '').title())
        ws_pb.cell(row=row_num, column=6, value=row.get('address_zip', '')[:5])

        for col in range(1, 7):
            apply_data_style(ws_pb.cell(row=row_num, column=col), row_num)

    ws_pb.auto_filter.ref = ws_pb.dimensions
    auto_fit_columns(ws_pb)
    setup_page(ws_pb)

    # =========== TAB 4: MIAMI SHORES + MIMO ===========
    ws_miami = wb.create_sheet("Miami Shores + MiMo")
    headers = ["#", "Restaurant", "Street Address", "Suite/Unit", "City", "Zip", "Area"]
    for col, header in enumerate(headers, 1):
        cell = ws_miami.cell(row=1, column=col, value=header)
        apply_header_style(cell)

    # Add neighborhood to each row
    miami_with_area = []
    for row in miami:
        area = get_miami_neighborhood(
            row.get('address_line1', ''),
            row.get('address_city', ''),
            row.get('segment', '')
        )
        miami_with_area.append({**row, 'area': area})

    # Sort by Area, then Restaurant name
    area_order = {"Miami Shores": 0, "Design District": 1, "Midtown": 2, "MiMo–Upper East Side": 3}
    miami_sorted = sorted(miami_with_area, key=lambda x: (area_order.get(x['area'], 99), x.get('company', '').upper()))

    for row_num, row in enumerate(miami_sorted, 2):
        ws_miami.cell(row=row_num, column=1, value=row_num - 1)
        ws_miami.cell(row=row_num, column=2, value=clean_name(row.get('company', '')))
        ws_miami.cell(row=row_num, column=3, value=row.get('address_line1', '').title())
        ws_miami.cell(row=row_num, column=4, value=row.get('address_line2', '').title())
        ws_miami.cell(row=row_num, column=5, value=row.get('address_city', '').title())
        ws_miami.cell(row=row_num, column=6, value=row.get('address_zip', '')[:5])
        ws_miami.cell(row=row_num, column=7, value=row.get('area', ''))

        for col in range(1, 8):
            apply_data_style(ws_miami.cell(row=row_num, column=col), row_num)

    ws_miami.auto_filter.ref = ws_miami.dimensions
    auto_fit_columns(ws_miami)
    setup_page(ws_miami)

    # =========== TAB 5: REMOVED ===========
    ws_removed = wb.create_sheet("Removed")
    headers = ["#", "Restaurant", "Reason"]
    for col, header in enumerate(headers, 1):
        cell = ws_removed.cell(row=1, column=col, value=header)
        apply_header_style(cell)

    for row_num, (restaurant, reason) in enumerate(removed, 2):
        ws_removed.cell(row=row_num, column=1, value=row_num - 1)
        ws_removed.cell(row=row_num, column=2, value=clean_name(restaurant))
        ws_removed.cell(row=row_num, column=3, value=reason)

        for col in range(1, 4):
            apply_data_style(ws_removed.cell(row=row_num, column=col), row_num)

    ws_removed.auto_filter.ref = ws_removed.dimensions
    auto_fit_columns(ws_removed)
    setup_page(ws_removed)

    # Save
    wb.save(OUTPUT_FILE)
    print(f"\nSaved to: {OUTPUT_FILE}")

    # Verify by reopening
    print("\n--- VERIFICATION ---")
    from openpyxl import load_workbook
    wb2 = load_workbook(OUTPUT_FILE)
    for sheet_name in wb2.sheetnames:
        ws = wb2[sheet_name]
        # Count data rows (exclude header)
        if sheet_name == "Summary":
            print(f"  {sheet_name}: (summary tab)")
        else:
            data_rows = ws.max_row - 1
            print(f"  {sheet_name}: {data_rows} rows")

    # Area breakdown for Miami
    print("\n--- MIAMI AREA BREAKDOWN ---")
    area_counts = {}
    for row in miami_with_area:
        area = row.get('area', 'Unknown')
        area_counts[area] = area_counts.get(area, 0) + 1
    for area in ["Miami Shores", "Design District", "Midtown", "MiMo–Upper East Side"]:
        print(f"  {area}: {area_counts.get(area, 0)}")


if __name__ == "__main__":
    main()
