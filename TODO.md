# UC Berkeley hackathon

## Todos

### Tech
- use models promoted for the hackathon
    - gemini flash 8b
    - llama 3.1 70b berkeley
- expand search engine (use other APIs)
- add more params to config
- handle large documents
    - limit time with unstructured and opt for a faster strategy (based on number of pages?)
    - use RAG or some other strategy to handle issues with context window OR gemini (1M tokens)
- use cache for downloaded data:
    - paper URL/filename as key
    - extracted data from unstructured (compress?)
    - bytes as backup (compress?) or the original file so that also the user can open it
- memory:
    - store previous outputs in local db for persisted memory
    - allow the user to select previous outputs to start from or start a new task
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
- build full platform and deploy?

### Eval
- should we drop latency as a metric? we can just reference it at the end

### Documentation
- add docstrings to all functions
- README:
    - Describe the agent (use markdown blocks from original notebook)
    - We should probably go more in depth with the agent description. We should document the code and write what each part does in the README.
    - Describe the evaluation procedure
- there will be some overlap between the README and the user guide

## Submission
- **Video Presentation**: Demonstrate your application in action and explain how it addresses a real-world problem.
- **Presentation Slides**: Outline the problem, your solution, technical implementation, and potential impact.
- **Project Code**: Provide source code with instructions for running the application, including any dependencies.
- **User Guide**: Include a brief document explaining how users can interact with your application. MAXIMUM 7-8 pages.
