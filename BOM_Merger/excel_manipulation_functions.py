import re
import pandas as pd
import numpy as np

from openpyxl import load_workbook


import requests
import re
from openpyxl import load_workbook

import requests
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

        # Expand short Mouser URLs
        if isinstance(link, str) and link.startswith("https://mou.sr/"):
            try:
                response = requests.get(
                    link,
                    allow_redirects=False,
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0"}
                )

                if "Location" in response.headers:
                    link = response.headers["Location"]
                else:
                    print(f"No redirect found: {link}")

            except requests.RequestException as e:
                print(f"Could not expand URL: {link}")
                print(f"Error: {e}")

        links.append(link)

    wb.close()

    return links

# Extract a numerical value and add its unit
def extract_value(pattern, text, unit):

    match = re.search(pattern, text)

    if match:
        number = match.group(1).replace(',', '.')
        prefix = match.group(2) or ''
        prefix = prefix.replace('µ', 'u').replace('μ', 'u')

        return number + prefix + unit

    return np.nan


# Extract a text specification
def extract_text(pattern, text):

    match = re.search(pattern, text)

    if match:
        return match.group(0).replace(' ', '')

    return np.nan


# Transform BOM
def extract_data_Oscar(bom, tempDF):

    num = r'\d+(?:[.,]\d+)?'

    for index, row in bom.iterrows():

        # Ignore empty rows and Excel totals
        if pd.isna(row['Component']):
            continue

        # Initialize all columns as NaN
        data = {col: np.nan for col in tempDF.columns}

        component = str(row['Component']).strip().lower()
        designation = str(row['Designation'])
        footprint = str(row['Footprint'])

        # Common information
        data['Specification'] = row['Component']
        data['manufacturer id'] = row['Name']
        data['Price/unit'] = row['Price Unit']
        data['Buy qty'] = row['Quantity']
        data['Shop URL'] = row['URL']

        # Case code from footprint
        match = re.search(
            r'^(?:C|R|L|LED)_(\d{4})(?=_|$)',
            footprint
        )

        if match:
            data['case code'] = match.group(1)
        elif pd.notna(row['Footprint']):
            data['case code'] = footprint

        # CAPACITORS
        if component == 'capacitor':

            data['value'] = extract_value(
                rf'(?<![\w.])({num})\s*(?:([pnumµμ])\s*F?|F)(?![\w.])',
                designation,
                'F'
            )

            data['Voltage Rating'] = extract_text(
                rf'(?<![\w.]){num}\s*(?:kV|V)(?!\w)',
                designation
            )

            data['dielectric'] = extract_text(
                r'\b(?:[XYZ]\d[A-Z]|C0G|NP0|NPO|U2J)\b',
                designation
            )

        # RESISTORS AND POTENTIOMETERS
        elif component in ['resistor', 'potentiometer']:

            data['value'] = extract_value(
                rf'(?<![\w.])({num})\s*([kKMm]?)\s*(?:Ω|[Oo][Hh][Mm][Ss]?|R)?(?![\w.%])',
                designation,
                'Ω'
            )

        # INDUCTORS
        elif component == 'inductor':

            data['value'] = extract_value(
                rf'(?<![\w.])({num})\s*([pnumµμ]?)\s*H(?![\w.])',
                designation,
                'H'
            )

            data['Resistance'] = extract_value(
                rf'(?<![\w.])({num})\s*([kKMmuµμ]?)\s*(?:Ω|[Oo][Hh][Mm][Ss]?)(?![\w.])',
                designation,
                'Ω'
            )

        # Tolerance for passive components
        if component in [
            'capacitor', 'resistor',
            'potentiometer', 'inductor'
        ]:

            data['tolerance'] = extract_text(
                rf'(?:±|\+/-)?\s*{num}\s*%',
                designation
            )

        # Add the component to the DataFrame
        tempDF.loc[len(tempDF)] = data

    return tempDF

def extract_data_Bence(bom, tempDF):

    num = r'\d+(?:[.,]\d+)?'

    # Regular expressions
    cap = rf'(?<![\w.]){num}\s*[pnumµμ]?F\b'

    ind = rf'(?<![\w.]){num}\s*[pnumµμ]?H\b'

    res = rf'(?<![\w.]){num}\s*[kKMmµμu]?\s*(?:Ω|ohms?)(?!\w)'

    voltage = rf'(?<![\w.]){num}\s*[kKm]?\s*V(?:AC|DC)?\b'
    
    tolerance = rf'(?<![\w.])(?:±|\+/-)?\s*{num}\s*%'

    dielectric = r'\b(?:[XYZ]\d[A-Z]|C0G|NP0|NPO|U2J)\b'

    safety = r'\b(?:X[123]|Y[1234])\b'

    package = (
        r'(?<![\w.])'
        r'(?:0201|0402|0603|0805|1008|1206|1210|'
        r'1812|2010|2512|SMA|SMB|SMC|GBJ|'
        r'(?:TO|SOT|LQFP|QFN|SOIC|TSSOP|MSOP)'
        r'-\d+(?:-[A-Z0-9]+)*)'
        r'(?![\w.])'
    )

    # Extract and remove information from text
    def take(text, pattern):

        match = re.search(pattern, text)

        if not match:
            return np.nan, text

        value = match.group(0).strip()

        # Normalize units
        value = re.sub(r'\s+', '', value)
        value = value.replace('µ', 'u')
        value = value.replace('μ', 'u')
        value = value.replace(',', '.')
        value = re.sub(r'ohms?', 'Ω', value, flags=re.I)

        # Remove extracted information
        text = text[:match.start()] + ' ' + text[match.end():]

        return value, text

    # Iterate through BOM
    for index, row in bom.iterrows():

        # Initialize all columns as NaN
        data = {col: np.nan for col in tempDF.columns}

        # Common information
        data['manufacturer id'] = row['Manufacturer part']
        data['Buy qty'] = row['Buy qty']
        data['Shop URL'] = row['Shop']

        if pd.notna(row['Part / specification']):

            text = str(row['Part / specification']).strip()

            # Remove safety classifications
            text = re.sub(safety, '', text)

            # CAPACITORS
            if re.search(cap, text):

                data['value'], text = take(text, cap)
                data['dielectric'], text = take(text, dielectric)

            # INDUCTORS
            elif re.search(ind, text):

                data['value'], text = take(text, ind)
                data['Resistance'], text = take(text, res)

            # RESISTORS
            elif re.search(res, text) and not re.search(
                r'\b(?:GaN|MOSFET|diode|IGBT|transistor)\b',
                text,
                re.I
            ):

                data['value'], text = take(text, res)

            # OTHER COMPONENTS
            else:

                data['Resistance'], text = take(text, res)

            # VOLTAGE RATING
            # LDO voltage is kept as part of its specification
            if not re.search(r'\bLDO\b', text, re.I):

                data['Voltage Rating'], text = take(text, voltage)

            # TOLERANCE
            data['tolerance'], text = take(text, tolerance)

            # CASE CODE
            case_code, text = take(text, package)

            footprint = row.get('Footprint', np.nan)

            if pd.notna(footprint):
                match = re.match(
                    r'^(?:C|R|L|LED)_?(0201|0402|0603|0805|1008|1206|1210|1812|2010|2512)(?=_|-|$)',
                    str(footprint)
                )
                data['case code'] = match.group(1) if match else footprint
            else:
                data['case code'] = case_code

            # REMAINING SPECIFICATIONS
            parts = [
                ' '.join(part.split())
                for part in text.split('·')
                if part.strip()
            ]

            data['Specification'] = (
                ' · '.join(parts) if parts else np.nan
            )

        # Add row to DataFrame
        tempDF.loc[len(tempDF)] = data

    return tempDF
