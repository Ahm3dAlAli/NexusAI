# NexusAI

<div align="center">
<img src="frontend/app/favicon.ico" alt="NexusAI Logo" width="100">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

> [!IMPORTANT]
> - 📰 **[12/03/24]** Featured in [DiamantAI's newsletter](https://diamantai.substack.com/p/nexus-ai-the-revolutionary-research) with a comprehensive deep-dive into our architecture and impact on research efficiency.
> - 🏆 **[11/26/24]** Winner of the [AgentCraft Hackathon](https://www.linkedin.com/posts/nir-diamant-ai_the-agentcraft-hackathon-in-conjunction-with-activity-7267552838023577600-_g2Z?utm_source=share&utm_medium=member_desktop) hosted by Dimant AI x Langchain!
> - 🚀 **[11/10/24]** Project started.

Keeping up with the flood of academic papers is harder than ever for researchers. Manually reviewing this overwhelming volume of studies takes too much time, leading to missed insights or duplicated efforts. Modern research is also more complex, with key information spread across text, figures, tables, and equations, making it difficult to fully understand. Current tools for searching and analyzing papers aren’t smart enough — they struggle to understand deeper connections between studies, extract insights from complex formats, or summarize information effectively.

NexusAI transforms how researchers interact with scientific literature. It streamlines research by delegating the heavy lifting to an AI agent able to plan its own execution strategy, self-assess the quality of its work, and let the user ask further questions to dive deeper into the results. All with access to the most comprehensive academic search engines (arXiv, CORE, and Google).

## Features

- 🧠 **Intelligent Query Processing** - Automatically determines if a query needs extensive research or can be answered directly, optimizing response time and computational resources.
- 📋 **Structured Planning** - Breaks down complex research queries into manageable subtasks with explicit tool mapping for systematic information gathering.
- 🔄 **Multi-API Paper Search** - Comprehensive research coverage through integration with arXiv, CORE, and Google Scholar APIs, with unified search syntax for consistent results across platforms.
- 📑 **Smart PDF Processing** - Efficient document handling with on-the-fly RAG and FAISS-powered vector search to extract only the most relevant content from papers.
- ⚡ **Parallel Processing** - Executes multiple tool calls simultaneously to minimize latency and improve response times.
- 🔍 **Self-Assessment & Refinement** - Implements quality control through automated self-review and iterative refinement of responses based on internal feedback.
- 💬 **Follow-up Questions** - Maintains conversation context to allow natural follow-up questions and deeper exploration of research topics without repeating context.
- 💾 **Redis Caching System** - Optimizes performance and reduces API costs by caching search results and tool outputs for faster subsequent queries.

## Architecture

NexusAI implements a modular architecture powered by a Python/LangChain backend, Next.js frontend, and Redis caching layer. The core agent workflow is orchestrated through a directed graph structure as shown below:

![Agent Workflow](https://i.ibb.co/0BBzkcb/mermaid-diagram-2024-11-17-195744.png)

The system maintains state through the `AgentState` class, tracking research requirements, planning status, feedback iterations, and message history.

Key components of the workflow include:

1. **Decision Making Node**: Determines if a query needs research or can be answered directly, producing a `DecisionMakingOutput`.

2. **Planning Node**: For research queries, breaks down complex tasks into subtasks mapped to specific tools.

3. **Agent Node**: Executes the research plan using a ReAct pattern, coordinating tool usage and synthesizing results.

4. **Tools Node**: Provides two main tools:
   - **Paper Search**: Unified search across multiple APIs (ArXiv, CORE, SERP) using `SearchPapersInput` schema
   - **PDF Processing**: Implemented in `PDFDownloader` with RAG-based content filtering

5. **Judge Node**: Quality control through `JudgeOutput`, providing feedback for iterative improvement.

The system employs Redis caching for API responses and parallel processing for tool execution to optimize performance. All communication between nodes uses standardized message types defined in `AgentMessageType`.

### Project Structure

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

   # Deployment
   FRONTEND_URL="http://localhost:3000"
   NEXT_PUBLIC_API_URL="ws://localhost:8000/ws"
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
