# Repo
- set a more restrictive license
- move markdown blocks from notebook to readme
- 'Quickstart' section is made up
- ahmed pls reference me somewhere :)

# Build with AI hackathon

## Ideas
- reduce latency by changing models (using gpt-4o-mini already helps a lot):
    - other areas of improvement: try other models (Qwen2 72B, cerebrus, groq)
    - we can also use different models for different parts of the workflow
- more rigorous analysis with perplexity and copilot or other tools. I think we can find examples where our agent is even better.
    - **we should double down on this since the judges really liked it in the previous hackathon**
    - better explain the metrics and find examples where our agent is even better
- handle large documents
    - limit time to download
    - limit time with unstructured and opt for a faster strategy (based on number of pages?)
    - use RAG or some other strategy to handle issues with context window
- save downloaded data to local cache:
    - paper URL/filename as key
    - extracted data from unstructured (compress?)
    - bytes as backup (compress?) or the original file so that also the user can open it
- better data extraction from PDF. Use unstructured: https://docs.unstructured.io/api-reference/api-services/sdk-python
    - [V] tables: use the html text to help the llm
    - [V] citations: they are detected throughout the text, meaning every chunk contains metadata about the citations it makes
        - NOTE: we need a way to reference the citations from the metadata to the actual citations in the 'References' section or whatever it's called
        - if url starts with 'cite.' then it's a citation
    - [V] images: only parses the text. that should be enough since the image is explained in the text, so we don't need to pass it to the llm
    - [-] equations: no latex but they're detected as equations + most math symbols are detected with unicode. The llm might not be 100% accurate when referencing the equation.
    - other type of links:
        - other sections of the paper (e.g. subsection.3.2)
        - external links (e.g. https://arxiv.org/abs/1706.03762)

## Nice to haves
- build a simple UI?
- memory:
    - store previous outputs in local db for persisted memory
    - allow the user to select previous outputs to start from or start a new task

## Submission
- find a mentor?
- share github repo
- documentation
- demo video (let's take more time to make it better than last time)