from urllib.parse import urlparse


def extract_base_url(url: str) -> str:
    parse_result = urlparse(url)
    return f"{parse_result.scheme}://{parse_result.netloc}"
