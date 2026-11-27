import re
import time
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse, parse_qs, unquote, quote

import pandas as pd


outCols = ['Manufacturer id', 'Supplier Code', 'Part/Specification',
           'Buy qty', 'Unit Price', 'Total Cost', 'Shop URL']

FIELDS = ('kind', 'value', 'case', 'dielectric', 'voltage', 'tolerance', 'extra')
PASSIVES = {'capacitor', 'resistor', 'inductor', 'led'}
MOUSER_REQUEST_INTERVAL = 2.1  # seconds; Mouser allows 30 requests/minute
# Safety limit for mandatory minimums/multiples. Adjustable by the user.
MAX_ORDER_FACTOR = 2
MAX_EXTRA_UNITS = 10


def _text(x):
    return '' if pd.isna(x) else str(x).strip()


def _norm(x):
    return re.sub(r'\s+', '', x.replace('μ', 'u').replace('µ', 'u').replace('Ω', 'Ω')).casefold()


def _case(x):
    if re.fullmatch(r'\d+(?:\.0+)?', x):
        n = str(int(float(x)))
        return n.zfill(4) if len(n) <= 4 else n
    return x.upper()


def _number_unit(x, unit):
    """Convert equivalent SI values to the same comparison key."""
    x = x.replace('μ', 'u').replace('µ', 'u').replace('Ω', 'Ω').replace(' ', '').replace(',', '.')
    x = re.sub(r'^(?:±|\+/-)', '', x)
    m = re.fullmatch(r'([+-]?\d+(?:\.\d+)?)([pnumkKMGT]?)(.*)', x)
    if not m:
        return _norm(x)
    number, prefix, suffix = m.groups()
    if unit == 'V':
        suffix = suffix.upper()
        if suffix == 'VDC':
            suffix = 'V'  # unqualified V treated as DC rating
        if suffix not in ('V', 'VAC'):
            return _norm(x)
    elif suffix.casefold() != unit.casefold():
        return _norm(x)
    factors = {'': 0, 'p': -12, 'n': -9, 'u': -6, 'm': -3,
               'k': 3, 'K': 3, 'M': 6, 'G': 9, 'T': 12}
    return (Decimal(number).scaleb(factors[prefix]), suffix.casefold())


def _url(x):
    m = re.search(r'https?://[^\s<>\]\)]+', x)
    if not m:
        return ''
    u = m.group(0)
    host = (urlparse(u).hostname or '').lower()
    return u if host == 'mouser.dk' or host.endswith('.mouser.dk') or host == 'mouser.com' or host.endswith('.mouser.com') else ''


def _url_id(u):
    p = urlparse(u)
    if p.path.rstrip('/') == '/c':
        return parse_qs(p.query).get('q', [''])[0]
    if '/productdetail/' in p.path.lower():
        return unquote(p.path.rstrip('/').split('/')[-1])
    return ''


def _search_url(mpn):
    return 'https://www.mouser.dk/c/?q=' + quote(mpn, safe='')


def _mpn_key(mpn):
    return mpn.strip().upper()


def _kind(spec, value):
    s = spec.casefold()
    if re.search(r'\bled\b', s):
        return 'led'
    # Do not treat potentiometers, transformers or chokes as ordinary passives.
    if re.search(r'potentiometer|transformer|choke|ferrite bead|thermistor|varistor|diode', s):
        return ''
    v = value.strip().replace('Ω', 'Ω')
    if v.lower().endswith('f') or s == 'capacitor':
        return 'capacitor'
    if v.endswith('Ω') or s == 'resistor':
        return 'resistor'
    if v.lower().endswith('h') or re.search(r'\binductor\b', s):
        return 'inductor'
    return ''


def _extra(kind, spec):
    if kind == 'led':
        # Ignore only functional indicator labels, not colour or technology.
        return _norm(re.sub(r'\b(?:LED|OK|STATUS)\b', '', spec, flags=re.I))
    if kind in PASSIVES:
        return '' if spec.casefold() in ('', kind) else _norm(spec)
    return ''  # active descriptions may be aliases for the same MPN


def _row(r, source, idx):
    spec = _text(r['Specification'])
    value = _text(r['value'])
    kind = _kind(spec, value)
    case = _case(_text(r['case code']))
    dielectric = _text(r['dielectric']).upper().replace('COG', 'C0G')
    voltage = _text(r['Voltage Rating'])
    tolerance = _text(r['tolerance'])
    mpn = _text(r['manufacturer id'])
    url = _url(_text(r['Shop URL']))
    if not mpn:
        mpn = _url_id(url)
    unit = {'capacitor': 'F', 'resistor': 'Ω', 'inductor': 'H'}.get(kind)
    key = dict(kind=kind, value=_number_unit(value, unit) if value and unit else _norm(value),
               case=_norm(case), dielectric=_norm(dielectric),
               voltage=_number_unit(voltage, 'V') if voltage else '',
               tolerance=_number_unit(tolerance, '%') if tolerance else '',
               extra=_extra(kind, spec))
    return dict(mpn=mpn, url=url, spec=spec, value=value, case=case,
                dielectric=dielectric, voltage=voltage, tolerance=tolerance,
                key=key, qty=int(r['Buy qty']), source=f'{source}[{idx}]')


def _conflicts(a, b):
    return [k for k in FIELDS if a[k] != '' and b[k] != '' and a[k] != b[k]]


def _covers(a, b):
    return all(b[k] == '' or a[k] == b[k] for k in FIELDS)


def _score(k):
    return sum(k[f] != '' for f in FIELDS)


def _group(rows):
    key = {k: next((r['key'][k] for r in rows if r['key'][k] != ''), '') for k in FIELDS}
    return {'rows': rows, 'key': key}


def _same_mpn(a, b):
    return bool(a['mpn'] and b['mpn'] and _mpn_key(a['mpn']) == _mpn_key(b['mpn']))


def _can_substitute(a, b):
    """Allow passive merges when known specifications do not conflict.

    Empty fields mean unknown, so a sparse row can join a more fully specified
    row. The merged group retains every known value, and candidate selection
    still requires a part that covers those combined requirements.
    """
    if a['kind'] not in PASSIVES or a['kind'] != b['kind']:
        return False
    if _conflicts(a, b):
        return False
    # Require a known nominal value and footprint to avoid broad matches.
    if not (a['value'] and b['value'] and a['value'] == b['value']):
        return False
    if not (a['case'] and b['case'] and a['case'] == b['case']):
        return False
    if a['kind'] == 'led':
        # Do not substitute generic LEDs or LEDs without known package/colour.
        return bool(a['extra'] and b['extra'] and a['extra'] == b['extra'])
    return True


def _specification(group, selected):
    rows = [selected] + [r for r in group['rows'] if r is not selected]
    def pick(field):
        return next((r[field] for r in rows if r[field]), '')
    def units(s):
        s = s.replace('μ', 'µ')
        s = re.sub(r'(?<=\d)u(?=[FH])', 'µ', s)
        return re.sub(r'(?<=\d)(?=[pnumµkKMGT]?[FVHΩ])', ' ', s)
    kind = group['key']['kind']
    spec = selected['spec'] or pick('spec')
    if kind in PASSIVES - {'led'} and spec.casefold() == kind:
        spec = ''
    if kind in PASSIVES - {'led'} and not spec:
        spec = next((r['spec'] for r in rows if r['key']['extra']), '')
    if kind == 'inductor' and not spec:
        spec = 'inductor'
    vals = [units(pick('value')), units(pick('voltage')), pick('dielectric'), pick('tolerance'), pick('case')]
    if kind in PASSIVES - {'led'}:
        # Bence style: value · voltage · dielectric · tolerance · case.
        pieces = [v for v in vals if v]
        if spec:
            pieces.append(spec)
    else:
        pieces = [spec] + [v for v in vals if v]
    return ' · '.join(dict.fromkeys(p for p in pieces if p)) or selected['mpn']


def _int(x, default=None):
    try:
        n = Decimal(str(x))
        return int(n) if n.is_finite() and n == int(n) and n >= 0 else default
    except (InvalidOperation, ValueError, TypeError, OverflowError):
        return default


def _minimum_order(part, required):
    minimum = max(1, _int(part.get('Min'), 1))
    multiple = max(1, _int(part.get('Mult'), 1))
    return ((max(required, minimum) + multiple - 1) // multiple) * multiple


def _order_limit(required):
    return max(required * MAX_ORDER_FACTOR, required + MAX_EXTRA_UNITS)


def _best_order(part, required):
    """Return (qty, Decimal unit price, Decimal total, currency, in_stock)."""
    base = _minimum_order(part, required)
    if base > _order_limit(required):
        return None  # MOQ/multiple requires manual review, not automatic buying
    multiple = max(1, _int(part.get('Mult'), 1))
    stock = _int(part.get('AvailabilityInStock'))
    breaks = []
    for p in part.get('PriceBreaks') or []:
        try:
            q = _int(p.get('Quantity'))
            price = Decimal(str(p['RawPrice']))
            currency = p.get('Currency', '')
            if q and price.is_finite() and price > 0 and currency == 'DKK':
                breaks.append((q, price, currency))
        except (KeyError, InvalidOperation, TypeError):
            continue
    breaks.sort(key=lambda x: x[0])

    def quote_order(qty):
        eligible = [b for b in breaks if b[0] <= qty]
        if not eligible:
            return None
        _, price, currency = eligible[-1]
        return qty, price, qty * price, currency, stock is not None and qty <= stock

    baseline = quote_order(base)
    if baseline is None:
        return None  # do not assume a distant price break is a valid base price
    if not baseline[4]:
        return baseline  # no speculative overbuying for unavailable/unknown stock
    candidates = [baseline]
    for q, _, _ in breaks:
        qty = max(base, ((q + multiple - 1) // multiple) * multiple)
        if base < qty <= min(stock, _order_limit(required)):
            order = quote_order(qty)
            if order and order[2] < baseline[2]:
                candidates.append(order)
    return min(candidates, key=lambda x: (x[2], x[0]))


def merge_boms(bom1, bom2, verbose=True):
    """Merge normalized DataFrames, query Mouser and return (mergedBOM, errorDict).

    Set verbose=False to disable terminal progress messages.
    """
    from api_handling_functions import extraer_Datos

    mergedBOM = pd.DataFrame(columns=outCols)
    errorDict = {}
    active_row = None
    started = time.monotonic()
    api_requests = 0
    cache_hits = 0

    def report(message):
        if verbose:
            print(message, flush=True)

    def elapsed():
        seconds = int(time.monotonic() - started)
        return f'{seconds // 60:02d}:{seconds % 60:02d}'

    def progress(done, total):
        fraction = done / total if total else 1
        filled = int(24 * fraction)
        bar = '#' * filled + '-' * (24 - filled)
        return f'[{bar}] {done}/{total} ({fraction:.0%})'

    report(f'Starting BOM merge: {len(bom1)} + {len(bom2)} input rows')
    report('[1/4] Reading and normalizing BOMs...')

    def log(category, **info):
        if active_row is not None:
            info['merged_rows'] = [active_row]
        errorDict.setdefault(category, []).append(info)

    required_cols = {'Specification', 'manufacturer id', 'value', 'case code',
                     'dielectric', 'Voltage Rating', 'tolerance', 'Buy qty', 'Shop URL'}
    rows = []
    for source, bom in [('bom1', bom1), ('bom2', bom2)]:
        missing = required_cols.difference(bom.columns)
        if missing:
            raise ValueError(f'{source}: missing columns {sorted(missing)}')
        for idx, r in bom.iterrows():
            qty = _int(r['Buy qty'])
            if qty is None:
                log('missing or invalid buy qty', source=f'{source}[{idx}]',
                    manufacturer_id=_text(r['manufacturer id']), specification=_text(r['Specification']))
                continue
            if qty == 0:
                continue
            rows.append(_row(r, source, idx))

    report(f'      {len(rows)} rows with valid positive purchase quantities.')
    report('[2/4] Grouping exact manufacturer part numbers...')

    # 1. Exact manufacturer part number first. Conflicting known specs stay separate.
    exact = []
    for r in rows:
        matches = []
        for g in exact:
            if not any(_same_mpn(r, s) for s in g['rows']):
                continue
            conflicts = _conflicts(g['key'], r['key'])
            if conflicts:
                log('wrong footprint' if 'case' in conflicts else 'conflicting specifications',
                    manufacturer_id=r['mpn'], source=r['source'], fields=conflicts,
                    existing_sources=[s['source'] for s in g['rows']])
            else:
                matches.append(g)
        if len(matches) == 1:
            g = matches[0]
            g.update(_group(g['rows'] + [r]))
        else:
            if len(matches) > 1:
                log('ambiguous match', manufacturer_id=r['mpn'], source=r['source'])
            exact.append(_group([r]))

    report(f'      {len(exact)} groups after exact matching.')
    report('[3/4] Querying Mouser and matching compatible passive components...')

    # 3. Mouser lookup. Cache identical searches. Use MPN search first, URL as fallback.
    cache = {}
    last_request = None
    def lookup(query_url):
        nonlocal last_request, api_requests, cache_hits
        if query_url not in cache:
            try:
                if last_request is not None:
                    time.sleep(max(0, MOUSER_REQUEST_INTERVAL - (time.monotonic() - last_request)))
                last_request = time.monotonic()
                api_requests += 1
                report(f'      Mouser request #{api_requests}: {_url_id(query_url) or "part lookup"}')
                data = extraer_Datos(query_url)
                if not isinstance(data, dict):
                    raise ValueError('No API response')
                if data.get('Errors'):
                    raise ValueError(str(data['Errors']))
                cache[query_url] = (data.get('SearchResults', {}).get('Parts') or [], None)
            except Exception as exc:
                # Avoid leaking API keys embedded in HTTP exception URLs.
                msg = re.sub(r'(?i)(apiKey=)[^&\s]+', r'\1[REDACTED]', str(exc))
                cache[query_url] = ([], msg)
                report('      Mouser API error (see errorDict for details).')
        else:
            cache_hits += 1
            report(f'      Cache hit: {_url_id(query_url) or "part lookup"}')
        return cache[query_url]

    def find_parts(r):
        mpn, url = r['mpn'], r['url']
        queries = list(dict.fromkeys(q for q in [_search_url(mpn) if mpn else '', url] if q))
        if not queries or re.search(r'\bnot\s+set\b', mpn, re.I):
            return [], 'missing or unassigned part number or URL'
        for query in queries:
            parts, err = lookup(query)
            if err:
                log('api error', manufacturer_id=mpn, error=err, source=r['source'])
                continue
            expected = _mpn_key(mpn)
            exact_parts = [p for p in parts if expected and _mpn_key(p.get('ManufacturerPartNumber') or '') == expected]
            if exact_parts:
                return exact_parts, None
            # A URL can specify a more concrete ordering suffix or sanitized slash.
            # Require one unambiguous result matching the URL or explicit URL reference.
            if query == url and url:
                uid = _mpn_key(_url_id(url))
                def slug(s):
                    return re.sub(r'[^A-Z0-9]', '', _mpn_key(s))
                matching = [p for p in parts if uid and slug(p.get('ManufacturerPartNumber') or '') == slug(uid)]
                if len(matching) == 1:
                    log('manufacturer id mismatch', requested=mpn, returned=matching[0].get('ManufacturerPartNumber'), source=r['source'])
                    return matching, None
        return [], 'no exact Mouser result'

    # Resolve each input reference at most once, even when testing many merges.
    resolved = {}

    def group_candidates(g):
        required = sum(r['qty'] for r in g['rows'])
        by_mpn = {}
        for r in g['rows']:
            ident = _mpn_key(r['mpn']) or r['url'] or r['source']
            by_mpn.setdefault(ident, []).append(r)
        candidates = []
        for rs in by_mpn.values():
            if not _covers(_group(rs)['key'], g['key']):
                continue
            r = max(rs, key=lambda r: (_score(r['key']), bool(r['url'])))
            if not (r['mpn'] or r['url']):
                continue
            if r['source'] not in resolved:
                resolved[r['source']] = find_parts(r)
                parts, err = resolved[r['source']]
                if err:
                    log('part not found', manufacturer_id=r['mpn'], source=r['source'], reason=err)
            parts, _ = resolved[r['source']]
            for p in parts:
                candidates.append((r, p, _best_order(p, required)))
        return candidates

    def best_candidate(g):
        candidates = group_candidates(g)
        if not candidates:
            return None
        return min(candidates, key=lambda c: (
            c[2] is None or not c[2][4], c[2] is None,
            c[2][2] if c[2] else Decimal('Infinity'),
            c[2][0] if c[2] else 0))

    def available_order(candidate):
        return candidate is not None and candidate[2] is not None and candidate[2][4]

    # Work from the most restrictive specifications towards the least restrictive.
    # Never decide by specificity alone: compare the real price of the combined
    # order, subtracting the price of the order already planned for that group.
    groups = []
    for number, g in enumerate(sorted(exact, key=lambda g: -_score(g['key'])), 1):
        report(f'  {progress(number, len(exact))} | Matching '
               f'{g["rows"][0]["mpn"] or g["rows"][0]["spec"]}')
        if g['key']['kind'] not in PASSIVES:
            groups.append(g)
            continue
        standalone = best_candidate(g)
        options = []
        for h in groups:
            if not _can_substitute(h['key'], g['key']):
                continue
            combined = _group(h['rows'] + g['rows'])
            candidate = best_candidate(combined)
            if not available_order(candidate):
                continue
            previous = best_candidate(h)
            previous_cost = previous[2][2] if available_order(previous) else Decimal(0)
            incremental = candidate[2][2] - previous_cost
            options.append((incremental, candidate[2][2], candidate[2][1],
                            str(candidate[1].get('MouserPartNumber') or ''), h, combined))
        if options:
            incremental, _, _, _, h, combined = min(options, key=lambda x: x[:4])
            # If the standalone option is available and cheaper, do not force a merge.
            if not available_order(standalone) or incremental <= standalone[2][2]:
                log('substitution review', sources=[r['source'] for r in g['rows']],
                    original=[r['mpn'] for r in g['rows']],
                    candidate=[r['mpn'] for r in h['rows']],
                    incremental_cost=str(incremental))
                h.update(combined)
                continue
        groups.append(g)

    report(f'      {len(groups)} groups to process ({len(rows) - len(groups)} rows consolidated).')
    report('[4/4] Finalizing orders and purchase quantities...')

    # Choose the final SKU with the same pricing rules used for matching.
    output = []
    source_to_row = {}
    report(progress(0, len(groups)))
    for group_number, g in enumerate(groups, start=1):
        active_row = len(output)
        issues_before = sum(map(len, errorDict.values()))
        for source_row in g['rows']:
            source_to_row[source_row['source']] = active_row
        required = sum(r['qty'] for r in g['rows'])
        label = next((r['mpn'] for r in g['rows'] if r['mpn']),
                     g['rows'][0]['spec'] or 'Unassigned component')
        report(f'  [{group_number}/{len(groups)}] Processing {label} | Required: {required}')
        fallback = max(g['rows'], key=lambda r: (_score(r['key']), bool(r['mpn'] or r['url'])))
        candidate = best_candidate(g)
        if candidate:
            r, part, order = candidate
        else:
            r, part, order = fallback, {}, None
            log('no verified supplier', manufacturer_id=r['mpn'], sources=[s['source'] for s in g['rows']])
        qty, unit, total = required, None, None
        if order:
            qty, unit, total, _, available = order
        elif part:
            minimum_order = _minimum_order(part, required)
            if minimum_order > _order_limit(required):
                log('excessive minimum order', manufacturer_id=part.get('ManufacturerPartNumber'),
                    required=required, minimum_order=minimum_order,
                    minimum=part.get('Min'), multiple=part.get('Mult'),
                    automatic_limit=_order_limit(required))
            else:
                log('price unavailable', manufacturer_id=part.get('ManufacturerPartNumber'),
                    currency='DKK', required=required, minimum_order=minimum_order)
            # Keep the requested quantity visible; price stays blank until reviewed.
        stock = _int(part.get('AvailabilityInStock'))
        if part and stock is None:
            log('stock unknown', manufacturer_id=part.get('ManufacturerPartNumber'), buy_qty=qty)
        elif part and stock < qty:
            log('out of stock', manufacturer_id=part.get('ManufacturerPartNumber'),
                required=required, buy_qty=qty, stock=stock, lead_time=part.get('LeadTime'))
        if qty > required:
            log('quantity increased', manufacturer_id=part.get('ManufacturerPartNumber') or r['mpn'],
                required=required, buy_qty=qty)
        output.append([part.get('ManufacturerPartNumber') or r['mpn'] or None,
                       part.get('MouserPartNumber'), _specification(g, r), qty,
                       float(unit) if unit is not None else None,
                       float(total) if total is not None else None,
                       part.get('ProductDetailUrl') or r['url'] or (_search_url(r['mpn']) if r['mpn'] else None)])
        if verbose:
            new_issues = sum(map(len, errorDict.values())) - issues_before
            cost = f'{total:.2f} DKK' if total is not None else 'unpriced'
            stock_text = str(stock) if stock is not None else 'unknown'
            report(f'      {progress(group_number, len(groups))} | '
                   f'Buy: {qty} | Stock: {stock_text} | Cost: {cost} | '
                   f'New issues: {new_issues} | Elapsed: {elapsed()}')
    mergedBOM = pd.DataFrame(output, columns=outCols)
    # Map grouping errors to the exact merged row(s), even after MPN substitution.
    for entries in errorDict.values():
        for entry in entries:
            if 'merged_rows' not in entry:
                sources = ([entry['source']] if 'source' in entry else [])
                sources += entry.get('sources', []) + entry.get('existing_sources', [])
                entry['merged_rows'] = sorted({source_to_row[s] for s in sources if s in source_to_row})
    if verbose:
        missing_costs = int(mergedBOM['Total Cost'].isna().sum())
        known_cost = mergedBOM['Total Cost'].sum()
        report('\nBOM merge completed.')
        report(f'  Merged rows: {len(mergedBOM)} | API requests: {api_requests} | Cache hits: {cache_hits}')
        report(f'  Elapsed: {elapsed()} | Errors/warnings: {sum(map(len, errorDict.values()))}')
        for category, entries in errorDict.items():
            report(f'    {category}: {len(entries)}')
        suffix = f' (partial: {missing_costs} unpriced rows)' if missing_costs else ''
        report(f'  Total cost: {known_cost:.2f} DKK{suffix}')
    return mergedBOM, errorDict


# Priority: when a row has several issues, its most severe category sets the fill.
ERROR_COLORS = {
    'wrong footprint': 'F4B084',
    'conflicting specifications': 'F4B084',
    'out of stock': 'FFC7CE',
    'excessive minimum order': 'FFC7CE',
    'no verified supplier': 'E4DFEC',
    'part not found': 'E4DFEC',
    'api error': 'E4DFEC',
    'price unavailable': 'E4DFEC',
    'manufacturer id mismatch': 'FCE4D6',
    'ambiguous match': 'FCE4D6',
    'missing or invalid buy qty': 'FCE4D6',
    'stock unknown': 'FCE4D6',
    'substitution review': 'FFF2CC',
    'quantity increased': 'DDEBF7',
}


def export_merged_bom(mergedBOM, errorDict, filename='Merged_BOM.xlsx'):
    """Export the original merged DataFrame and its error dictionary to Excel.

    Keep the index from merge_boms() intact: merged_rows stores those row IDs.
    The original DataFrame is not modified. Costs are in DKK.
    """
    import json
    from openpyxl.styles import PatternFill, Font, Alignment
    from openpyxl.utils import get_column_letter

    if not mergedBOM.index.is_unique:
        raise ValueError('Merged BOM index must be unique')
    df = mergedBOM.copy()
    if 'Total Cost' not in df.columns:
        raise ValueError('Missing Total Cost column')
    priority = {category: i for i, category in enumerate(ERROR_COLORS)}
    row_errors = {idx: set() for idx in df.index}
    details = []
    # Resolve exact row IDs from the updated merger. For older dictionaries,
    # fall back to MPN matching (which may mark several possible rows).
    for category, entries in errorDict.items():
        for entry in entries:
            if 'merged_rows' in entry:
                ids = [i for i in entry['merged_rows'] if i in row_errors]
                mapping = 'Exact' if ids else 'No matching BOM row'
            else:
                mpns = [entry.get(k) for k in ('manufacturer_id', 'requested', 'returned')]
                for k in ('original', 'candidate', 'candidates'):
                    values = entry.get(k) or []
                    if isinstance(values, list):
                        for v in values:
                            mpns.extend(v if isinstance(v, list) else [v])
                keys = {_mpn_key(str(m)) for m in mpns if m and not pd.isna(m)}
                ids = [i for i, m in df['Manufacturer id'].items()
                       if pd.notna(m) and _mpn_key(str(m)) in keys]
                mapping = 'MPN match (not exact)' if ids else 'No matching BOM row'
            for i in ids:
                row_errors[i].add(category)
            details.append((category, ids, mapping, entry))

    def ordered(categories):
        return sorted(categories, key=lambda c: (priority.get(c, len(priority)), c))

    df['Errors'] = ['; '.join(ordered(row_errors[i])) for i in df.index]
    # Excel row numbers, not the DataFrame's zero-based index.
    excel_rows = {idx: n for n, idx in enumerate(df.index, start=2)}
    log_df = pd.DataFrame([
        {'Error type': category,
         'BOM Excel rows': ', '.join(str(excel_rows[i]) for i in ids),
         'Mapping': mapping,
         'Details': json.dumps(entry, ensure_ascii=False, default=str)}
        for category, ids, mapping, entry in details
    ], columns=['Error type', 'BOM Excel rows', 'Mapping', 'Details'])
    legend_df = pd.DataFrame([
        {'Error type': c, 'Colour': '#' + ERROR_COLORS.get(c, 'E7E6E6')}
        for c in ordered(set(ERROR_COLORS) | set(errorDict))
    ])

    def fill(color):
        return PatternFill(fill_type='solid', fgColor=color)

    def style_header(ws):
        for cell in ws[1]:
            cell.fill = fill('243746')
            cell.font = Font(color='FFFFFF', bold=True)
            cell.alignment = Alignment(vertical='center', wrap_text=True)
        ws.row_dimensions[1].height = 30
        ws.freeze_panes = 'A2'
        ws.sheet_view.showGridLines = False

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='BOM', index=False)
        log_df.to_excel(writer, sheet_name='Errors', index=False)
        legend_df.to_excel(writer, sheet_name='Legend', index=False)
        ws = writer.sheets['BOM']
        style_header(ws)
        last_data_row = len(df) + 1
        ws.auto_filter.ref = f'A1:{get_column_letter(len(df.columns))}{last_data_row}'
        widths = {'Manufacturer id': 27, 'Supplier Code': 25, 'Part/Specification': 53,
                  'Buy qty': 12, 'Unit Price': 15, 'Total Cost': 16, 'Shop URL': 45, 'Errors': 48}
        money_format = '#,##0.00" DKK"'
        for col, name in enumerate(df.columns, 1):
            ws.column_dimensions[get_column_letter(col)].width = widths.get(name, 20)
            if name in ('Unit Price', 'Total Cost'):
                for row in range(2, last_data_row + 1):
                    ws.cell(row, col).number_format = money_format
        for idx, row in excel_rows.items():
            categories = ordered(row_errors[idx])
            if categories:
                color = ERROR_COLORS.get(categories[0], 'E7E6E6')
                for cell in ws[row]:
                    cell.fill = fill(color)
            for name in ('Part/Specification', 'Errors'):
                if name in df.columns:
                    ws.cell(row, df.columns.get_loc(name) + 1).alignment = Alignment(wrap_text=True, vertical='center')
            if 'Shop URL' in df.columns:
                cell = ws.cell(row, df.columns.get_loc('Shop URL') + 1)
                if isinstance(cell.value, str) and cell.value.startswith(('https://', 'http://')):
                    cell.hyperlink = cell.value
                    cell.font = Font(color='0563C1', underline='single')
        total_col = df.columns.get_loc('Total Cost') + 1
        total_letter = get_column_letter(total_col)
        total_row = last_data_row + 1
        missing_costs = int(df['Total Cost'].isna().sum())
        label = 'TOTAL COST' if not missing_costs else f'KNOWN COST (partial: {missing_costs} unpriced)'
        ws.cell(total_row, max(1, total_col - 1), label)
        ws.cell(total_row, total_col, f'=SUM({total_letter}2:{total_letter}{last_data_row})' if len(df) else '=0')
        ws.cell(total_row, total_col).number_format = money_format
        for cell in ws[total_row]:
            cell.fill = fill('243746')
            cell.font = Font(color='FFFFFF', bold=True)
            cell.alignment = Alignment(wrap_text=True, vertical='center')
        ws.row_dimensions[total_row].height = 43 if missing_costs else 26

        log_ws = writer.sheets['Errors']
        style_header(log_ws)
        log_ws.auto_filter.ref = log_ws.dimensions
        for col, width in zip('ABCD', (34, 22, 29, 95)):
            log_ws.column_dimensions[col].width = width
        for row, (category, *_rest) in enumerate(details, 2):
            for cell in log_ws[row]:
                cell.fill = fill(ERROR_COLORS.get(category, 'E7E6E6'))
                cell.alignment = Alignment(wrap_text=True, vertical='top')
        legend_ws = writer.sheets['Legend']
        style_header(legend_ws)
        legend_ws.column_dimensions['A'].width = 38
        legend_ws.column_dimensions['B'].width = 18
        for row, category in enumerate(legend_df['Error type'], 2):
            for cell in legend_ws[row]:
                cell.fill = fill(ERROR_COLORS.get(category, 'E7E6E6'))
    return filename
