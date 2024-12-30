# Prompt to create a paper that needs to be added to the user collection
create_paper_prompt = """You are a research paper analyzer. Given the following paper URL: {url}

Please analyze the paper and provide the following information in a structured format:
- Title: Extract the exact title of the paper
- Authors: List all authors, separated by commas
- Summary: Provide a 2-3 paragraph summary of the key findings and contributions

Please ensure your response is factual and based on the paper's content.

Here's the paper content:

{content}
"""
