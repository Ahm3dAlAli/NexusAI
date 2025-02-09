import re

def arxiv_abs_to_pdf_url(url: str) -> str:
    return url.replace("arxiv.org/abs/", "arxiv.org/pdf/")

def extract_urls(text: str) -> list[str]:
    links: list[str] = re.findall(r"\[.*?\]\((.*?)\)", text)
    links = list(dict.fromkeys(links))
    return links
