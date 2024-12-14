# UC Berkeley hackathon

## Todos

### Tech
- deploy on azure
- better data extraction from PDF. Use unstructured: https://docs.unstructured.io/api-reference/api-services/sdk-python
    - llamaparse? might be a good option to parse data correctly
    - [V] tables: use the html text to help the llm
    - [V] citations: they are detected throughout the text, meaning every chunk contains metadata about the citations it makes
        - NOTE: we need a way to reference the citations from the metadata to the actual citations in the 'References' section or whatever it's called
        - if url starts with 'cite.' then it's a citation
    - [V] images: only parses the text. that should be enough since the image is explained in the text, so we don't need to pass it to the llm
    - [-] equations: no latex but they're detected as equations + most math symbols are detected with unicode. The llm might not be 100% accurate when referencing the equation.
    - other type of links:
        - other sections of the paper (e.g. subsection.3.2)
        - external links (e.g. https://arxiv.org/abs/1706.03762)
- keywords/hybrid search for page filtering

### Documentation
- README:
    - Describe the agent (use markdown blocks from original notebook)
    - We should probably go more in depth with the agent description. We should document the code and write what each part does in the README.
    - Describe the evaluation procedure

## Submission
- **Video Presentation**: Demonstrate your application in action and explain how it addresses a real-world problem.
- **Presentation Slides**: Outline the problem, your solution, technical implementation, and potential impact.
- **Project Code**: Provide source code with instructions for running the application, including any dependencies.
- **User Guide**: Include a brief document explaining how users can interact with your application. MAXIMUM 7-8 pages.

## Priorities 

### Latex Overleaf report and Unit testing
- Documentation and Testing
- Create comprehensive API documentation
- Develop test suites for each component
- Implement integration tests
- Create usage examples and tutorials
- Add Evlauation Metrics and Benchamrking in the report

