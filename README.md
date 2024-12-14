# NexusAI

<div align="center">
<img src="frontend/app/favicon.ico" alt="NexusAI Logo" width="100">

[![GitHub stars](https://img.shields.io/github/stars/Ahm3dAlAli/NexusAI.svg?style=social)](https://github.com/Ahm3dAlAli/NexusAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

> [!IMPORTANT]
> - 📰 **[12/03/24]** Featured in [DiamantAI's newsletter](https://diamantai.substack.com/p/nexus-ai-the-revolutionary-research) with a comprehensive deep-dive into our architecture and impact on research efficiency.
> - 🏆 **[11/26/24]** Winner of the [AgentCraft Hackathon](https://www.linkedin.com/posts/nir-diamant-ai_the-agentcraft-hackathon-in-conjunction-with-activity-7267552838023577600-_g2Z?utm_source=share&utm_medium=member_desktop) hosted by Dimant AI x Langchain!
> - 🚀 **[11/10/24]** Project started.

Keeping up with the flood of academic papers is harder than ever for researchers. Manually reviewing this overwhelming volume of studies takes too much time, leading to missed insights or duplicated efforts. Modern research is also more complex, with key information spread across text, figures, tables, and equations, making it difficult to fully understand. Current tools for searching and analyzing papers aren’t smart enough — they struggle to understand deeper connections between studies, extract insights from complex formats, or summarize information effectively.

NexusAI transforms how researchers interact with scientific literature. It streamlines research by delegating the heavy lifting to an AI agent able to plan its own execution strategy, self-assess the quality of its work, and let the user ask further questions to dive deeper into the results. All with access to the most comprehensive academic search engines (arXiv, CORE, and Google).

### Demo

**TODO**: Add a demo video

## Architecture

**TODO**: Add a diagram and describe the architecture in detail.
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

## Features

**TODO**: Describe features in detail.
NexusAI offers the following key capabilities:

- **State-Driven Analysis**: Five-node system for orchestrated research with validation gates
- **Comprehensive Processing**: Automated paper retrieval, content extraction, and structure analysis
- **Quality Focused**: Multi-step validation and improvement cycles
- **Human-in-the-Loop**: Flexible validation options for critical research tasks
- **Academic Integration**: Direct access to 136M+ papers through CORE API

## ⚙️ Getting Started

### Prerequisites

Before you begin, make sure you have Docker installed.

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Ahm3dAlAli/NexusAI.git
   cd NexusAI
   ```

2. **Set Up Environment Variables**
   
   Create a `.env` file by copying the provided template:
   ```bash
   cp .env.sample .env
   ```

   Configure your environment variables:
   ```env
   # Required
   OPENAI_API_KEY=your_openai_api_key

   # Optional - for enhanced functionality
   CORE_API_KEY=your_core_api_key
   SERP_API_KEY=your_serp_api_key
   LANGCHAIN_API_KEY=your_langchain_api_key

   # Redis configuration (leave as default for Docker setup)
   REDIS_URL="redis://redis:6379"
   ```

### Running with Docker

Start the application by running:
```bash
docker-compose up --build
```

If that doesn't work, try running it without the dash:
```bash
docker compose up --build
```

This command starts three services:
- Frontend (Next.js) - Port 3000
- Backend (FastAPI) - Port 8000
- Redis (caching) - Port 6379

Navigate to the frontend interface at [http://localhost:3000](http://localhost:3000) and start automating your research!

### Project Structure

NexusAI is built on a modular architecture comprising several key components, our implementation is divided into three main parts: backend, frontend, and Redis.

```
NexusAI/
├── backend/                 # FastAPI backend service
│   ├── Dockerfile
│   └── server/
├── frontend/               # Next.js frontend application
│   └── Dockerfile
├── nexusai/               # Core NexusAI library
├── docker-compose.yml     # Docker services configuration
├── requirements.txt       # Python dependencies
└── .env.sample           # Environment variables template
```

## Use Cases

**TODO**

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

We would like to thank Dimant AI and Langchain for hosting the AgentCraft Hackathon. Special thanks to arXiv, CORE, and Serp for providing APIs to access academic papers.

## Contact

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/vincenzofanizza">
        <img src="https://avatars.githubusercontent.com/u/104767369?v=4" width="100px;" alt="Vincenzo Fanizza"/><br />
        <sub><b>Vincenzo Fanizza</b></sub>
      </a><br />
      <a href="https://www.linkedin.com/in/vincenzo-fanizza/" title="LinkedIn">
        <img src="https://img.shields.io/badge/-LinkedIn-0A66C2?style=flat&logo=linkedin" />
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Ahm3dAlAli">
        <img src="https://avatars.githubusercontent.com/u/84172381?v=4" width="100px;" alt="Ahmed Al Ali"/><br />
        <sub><b>Ahmed Al Ali</b></sub>
      </a><br />
      <a href="https://www.linkedin.com/in/ahmed-a-295933211/" title="LinkedIn">
        <img src="https://img.shields.io/badge/-LinkedIn-0A66C2?style=flat&logo=linkedin" />
      </a>
    </td>
  </tr>
</table>

Feel free to reach out to us for questions, suggestions, or contributions! You can also:

- 🐛 [Open an issue](https://github.com/Ahm3dAlAli/NexusAI/issues)
- 🔧 [Submit a PR](https://github.com/Ahm3dAlAli/NexusAI/pulls)

<p align="right">
<a href="#nexusai">↑ Back to Top</a>
</p>
