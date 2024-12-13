# UC Berkeley hackathon

## Todos

### Tech
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

### Documentation
- README:
    - Describe the agent (use markdown blocks from original notebook)
    - We should probably go more in depth with the agent description. We should document the code and write what each part does in the README.
    - Describe the evaluation procedure
- there will be some overlap between the README and the user guide
    - **ask judges where to write detailed doc (readme or user guide???)**

## Submission
- **Video Presentation**: Demonstrate your application in action and explain how it addresses a real-world problem.
- **Presentation Slides**: Outline the problem, your solution, technical implementation, and potential impact.
- **Project Code**: Provide source code with instructions for running the application, including any dependencies.
- **User Guide**: Include a brief document explaining how users can interact with your application. MAXIMUM 7-8 pages.

## Notes
We should explain all our design choices in the user guide.

We want to provide researchers with a responsive and long-context agent that can answer complex questions.
For this, we implemented cache and context window management.

Cache:
- store pdfs and query results in cache (redis to maximize throughput)
- query results expire after 7 days (reasonable time period for a paper to be relevant)
- the goal is to minimize latency, reduce API usage, and make the agent more robust

Agent context: we implemented a sophisticated context management system to make the agent more responsive to the current planning.
- remove all messages between the last human message and the last planning message
- add the current planning message at the end

Make the agent robust:
- use RAG
- multiple APIs

Why 4o mini?
- best compromise between latency, cost, and performance
- lambda labs doesn't support debit cards
- gemini models cannot be used as agents because they strictly require user-ai message sequence

Search APIs:
- the user can run the agent locally, but they need to provide their own API keys.
- using the online demo is recommended because we'll have all the keys there, especially semantic scholar which is the best API.

## Priorities 

### Latex Overleaf report and Unit testing
- Documentation and Testing
- Create comprehensive API documentation
- Develop test suites for each component
- Implement integration tests
- Create usage examples and tutorials
- Add Evlauation Metrics and Benchamrking in the report

