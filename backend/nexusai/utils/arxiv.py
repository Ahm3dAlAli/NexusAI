def url_to_pdf_url(url: str) -> str:
    return url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
