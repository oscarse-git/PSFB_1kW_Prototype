import requests
from urllib.parse import urlparse, parse_qs, unquote

with open("api_key.txt", "r") as file:
    API_KEY = file.read().strip()


def get_part_number(url):
    if not isinstance(url, str):
        return None

    parsed = urlparse(url)

    # Mouser search URL
    if parsed.path.rstrip("/") == "/c":
        return parse_qs(parsed.query).get("q", [None])[0]

    # Mouser product URL
    if "/ProductDetail/" in parsed.path:
        return unquote(parsed.path.rstrip("/").split("/")[-1])

    return None

def extraer_Datos(url):
    id = get_part_number(url)

    if not id:
        return None

    api_url = "https://api.mouser.com/api/v1/search/partnumber"

    params = {
        "apiKey": API_KEY
    }

    payload = {
        "SearchByPartRequest": {
            "mouserPartNumber": id,
            "partSearchOptions": "Exact"
        }
    }

    response = requests.post(
        api_url,
        params=params,
        json=payload,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    return data