# UC Berkeley hackathon

## Todos

### Tech
- expand search engine (use other APIs)
    - Google Scholar
    - CORE
    - semantic scholar
    - arxiv
    - PubMed
    - Web of Science
    We need to be able to find ANY paper we can think of. Maybe we don't need all of them maybe we need more.
- handle large documents
    - limit time with unstructured and opt for a faster strategy (based on number of pages?)
    - use RAG or some other strategy to handle issues with context window
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

## Notes
- lambda labs doesn't support debit cards
- gemini models cannot be used as agents because they strictly require user-ai message sequence

### Priorities 

#### Priority 1: Core API Wrapper Development
API Integration Layer

Implement unified interface for multiple academic APIs:

PubMed
Core API
Semantic Scholar
arXiv
Google Scholar API


Develop standardized response format
Implement caching system for paper storage
Create parallel processing pipeline for multi-API queries

Search Engine Core

Design unified search interface
Implement query router
Create response aggregator
Build cache management system
Develop API rate limiting handlers

#### Priority 2: Unstructured Data Processing
Table Analysis

Implement table extraction from PDFs
Create comparison framework for tables across papers
Design standardized table representation format
Build table data validator

Paper Analysis Pipeline

Create full-text extraction system
Implement section-wise analysis
Design citation network analyzer
Build figure/diagram extractor
Develop metadata processor

#### Priority 3: User Agent System
Agent Implementation

Design agent architecture for complex queries
Implement consecutive NP-hard question handling
Create context maintenance system
Develop agent cooperation framework

Documentation and Testing

Create comprehensive API documentation
Develop test suites for each component
Implement integration tests
Create usage examples and tutorials