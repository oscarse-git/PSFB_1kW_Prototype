import re
from openpyxl import load_workbook

def get_urls(file, bom):
    wb = load_workbook(file)
    ws = wb["BOM"]
    col = bom.columns.get_loc("Shop") + 1
    links = []
    for i in range(len(bom)):
        cell = ws.cell(row=i + 2, column=col)

        if cell.hyperlink:
            link = cell.hyperlink.target

        elif cell.data_type == "f":
            match = re.search(r'HYPERLINK\("([^"]+)"', cell.value, re.I)
            link = match.group(1) if match else None

        else:
            link = cell.value

        links.append(link)

    return links