# NexusAI

<div align="center">
<img src="path-to-your-logo.svg" alt="NexusAI Logo" width="100">

[![GitHub stars](https://img.shields.io/github/stars/yourusername/nexusai.svg?style=social)](https://github.com/Ahm3dAlAli/NexusAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Discussions](https://img.shields.io/badge/Discussions-Q%26A-green?logo=github)](https://github.com/yourusername/nexusai/discussions)

</div>

> [!IMPORTANT]
> - 🏆 (11/26/24) Winner of the Agent Craft Hackathon hosted by Dimant AI x Langchain!
> - 📚 Built using LangGraph and advanced LLMs for state-driven scientific paper analysis
> - 🔍 Integrated with CORE API for access to 136M+ academic papers
> - 🤝 Join our growing community of researchers and contributors

NexusAI is an intelligent research assistant that transforms how researchers interact with scientific literature. It streamlines the paper analysis process through state-driven workflows, advanced language models, and sophisticated validation mechanisms.

- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quickstart](#quickstart)
- [Use Cases](#use-cases)
- [Contributing](#contributing)

## Key Features

NexusAI offers the following key capabilities:

- **State-Driven Analysis**: Five-node system for orchestrated research with validation gates
- **Comprehensive Processing**: Automated paper retrieval, content extraction, and structure analysis
- **Quality Focused**: Multi-step validation and improvement cycles
- **Human-in-the-Loop**: Flexible validation options for critical research tasks
- **Academic Integration**: Direct access to 136M+ papers through CORE API

## Architecture

NexusAI is built upon a layered architecture with three main components:

### 1. Workflow Engine
- StateGraph Architecture for orchestrated research
- Decision Making Node for query intent analysis
- Planning Node for research strategy formulation
- Tool Execution Node for paper processing
- Judge Node for quality validation

### 2. Paper Processing
- CORE API integration
- PDF content extraction
- Text structure preservation
- Metadata validation

### 3. Analysis Pipeline
- State-aware processing
- Multi-step validation
- Quality improvement cycles
- Human validation options

## Quickstart

First install the required packages:

```bash
pip install requirements.txt
```

Set up your environment variables:

```python

```

Basic usage example:

```python
from nexusai import ResearchAssistant

# Initialize the research assistant
assistant = ResearchAssistant()

# Analyze a research paper
results = assistant.analyze_paper("paper_url_or_query")

# Run a literature review
review = assistant.literature_review("quantum computing", year_range=(2023, 2024))
```

Evaluation using MacOS zsh

```python
python path/run_evaluation.py --services our_agent perplexity --interactive
```

## Use Cases

### 1. Academic Research
- Literature review and synthesis
- Paper analysis and summary
- Citation tracking
- Research validation

### 2. Industry R&D
- Technical documentation review
- Patent analysis
- Competitive research
- State-of-the-art tracking

### 3. Education
- Student research assistance
- Learning resource identification
- Research methodology training


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to Dimant AI and Langchain for hosting the Agent Craft Hackathon
- Special thanks to CORE API for enabling academic paper access
- Thanks to our amazing community of contributors

## Contact

- GitHub Issues: For bug reports and feature requests
- GitHub Discussions: For general questions and discussions


<p align="right">
<a href="#nexusai">↑ Back to Top</a>
</p>
