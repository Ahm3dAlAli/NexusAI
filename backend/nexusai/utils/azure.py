import re

def extract_details_from_target_uri(target_uri: str) -> dict:
    endpoint = re.search(r'https://[^/]+', target_uri).group(0)
    deployment_name = re.search(r'/deployments/(.*)/chat/completions', target_uri).group(1)
    api_version = re.search(r'api-version=(.*)', target_uri).group(1)
    if not all([endpoint, deployment_name, api_version]):
        raise ValueError("The provided Azure OpenAI endpoint is not valid.")
    return {
        "endpoint": endpoint,
        "deployment_name": deployment_name,
        "api_version": api_version
    }
