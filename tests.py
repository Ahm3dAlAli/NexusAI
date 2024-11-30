import json
import os
import urllib3
import unstructured_client
from dotenv import load_dotenv
from unstructured_client.models import operations, shared

load_dotenv()

if __name__ == "__main__":
    # Test unstructured for PDF extraction
    client = unstructured_client.UnstructuredClient(
        api_key_auth=os.getenv("UNSTRUCTURED_API_KEY"),
        server_url=os.getenv("UNSTRUCTURED_API_URL"),
    )

    url = "https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf"
    http = urllib3.PoolManager(
        cert_reqs='CERT_NONE',
    )

    # Mock browser headers to avoid 403 error
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    response = http.request('GET', url, headers=headers)

    req = operations.PartitionRequest(
        partition_parameters=shared.PartitionParameters(
            files=shared.Files(
                content=response.data,
                file_name=url,
            ),
            strategy=shared.Strategy.AUTO,
            languages=['eng'],
            split_pdf_page=True,  # This way we send parallel requests for each page, reducing latency.
            split_pdf_allow_failed=True,
            split_pdf_concurrency_level=15  # Set to max value to reduce latency.
        ),
    )

    try:
        res = client.general.partition(request=req)
        element_dicts = [element for element in res.elements]
        
        # Print the processed data's first element only.
        print(element_dicts[0])

        # Write the processed data to a local file.
        json_elements = json.dumps(element_dicts, indent=2)

        with open("data/test.json", "w") as file:
            file.write(json_elements)
    except Exception as e:
        print(e)
