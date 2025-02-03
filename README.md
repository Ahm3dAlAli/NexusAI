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

NexusAI transforms how researchers interact with scientific literature. It streamlines research by delegating the heavy lifting to an AI agent able to plan its own execution strategy, self-assess the quality of its work, and let the user ask further questions to dive deeper into the results. All with access to the most comprehensive academic search engines (arXiv, Bing, CORE, and Google).

# Features

NexusAI combines advanced AI research capabilities with enterprise-ready platform features to deliver a comprehensive research automation solution. The system is built on two main pillars: a sophisticated AI agent for intelligent research automation and a robust platform infrastructure for enterprise deployment.

### Core Agent Capabilities

The AI agent is designed to handle complex research tasks through a combination of advanced language models, specialized tools, and intelligent workflow management. These capabilities enable the agent to understand, plan, and execute research tasks with human-like comprehension while maintaining machine-like efficiency.

- 🧠 **Dual Processing Modes** - Intelligently routes queries through either a research workflow for complex questions or direct paper processing for document analysis, optimizing response strategies.
- 📋 **Dynamic Research Planning** - Creates adaptive research strategies using a multi-LLM approach (gpt-4o-mini for simple tasks, gpt-4o for complex ones) to optimize cost and performance.
- 🔄 **Multi-Provider Search** - Unified search interface across arXiv, Bing, CORE, and Serp APIs with provider fallback, ensuring comprehensive coverage and resilience.
- 📑 **Smart Document Processing** - RAG-powered content filtering with configurable dimension embeddings, automatically limiting processing to the most relevant sections of papers.
- ⚡ **Asynchronous Tool Execution** - Parallel processing of tool calls through async/await patterns, significantly reducing latency in multi-step research tasks.
- 🔍 **Iterative Quality Control** - Self-assessment system with configurable feedback loops (`MAX_FEEDBACK_REQUESTS`) for continuous refinement of responses.
- 💬 **Stateful Conversations** - Maintains conversation context through `AgentState` management, enabling coherent multi-turn interactions.

### Platform Features

The platform layer provides the infrastructure and interfaces necessary for deploying NexusAI in production environments. These features ensure security, scalability, and a seamless user experience while maintaining enterprise-grade standards.

- 🎨 **Intuitive Research Interface** - Minimalist chat-like interface with curated example research questions to help researchers quickly understand and leverage the platform's capabilities.
- 📚 **Research Management** - PostgreSQL-powered system for storing research history and paper collections, enabling users to access and continue previous research sessions while building their knowledge base.
- 💾 **Caching Layer** - Redis-based caching system for API responses and PDF content with provider-specific cache management, optimizing response times and reducing API costs.
- 🌐 **Real-time Updates** - WebSocket-based streaming of intermediate results with structured message types, providing researchers with live insights into the research process.
- ⚙️ **Customizable Experience** - System-level custom instructions feature allowing researchers to guide the agent's behavior and tailor its research approach to their specific needs.
- 🔐 **Enterprise-grade Security** - Comprehensive authentication system through NextAuth supporting email-password and Microsoft Azure AD, with JWT-secured API endpoints and WebSocket connections.

# Architecture

The backend implements two primary functionalities: Research Workflow and Paper Processing.

### Research Workflow

Orchestrated through a directed graph structure with the following nodes:

1. **Decision Making Node** - The entry point of the workflow that evaluates query complexity using gpt-4o-mini. It analyzes the user's request and produces a `DecisionMakingOutput` to determine whether research is required or if the query can be answered directly. The node supports custom instructions through markdown-formatted directives that influence the decision-making process.

2. **Planning Node** - A strategic component that creates detailed research plans based on the query complexity. It utilizes gpt-4o for complex planning tasks while falling back to gpt-4o-mini for simpler ones to optimize costs. The node creates structured research plans with explicit tool mappings and incorporates previous conversation context to avoid redundant searches.

3. **Tools Node** - The execution engine that handles all external interactions through asynchronous processing. It implements retry mechanisms with exponential backoff for reliability and manages two primary tools: a unified paper search interface across multiple providers and a PDF processing system for content extraction with RAG-based filtering.

4. **Agent Node** - The orchestrator that coordinates tool execution based on the planning output. It maintains the conversation state through `AgentState` and manages the streaming of intermediate results to clients through WebSocket connections, ensuring real-time visibility into the research process.

5. **Judge Node** - The quality control component that evaluates response quality through structured `JudgeOutput`. It implements configurable feedback loops with a default of 2 attempts and provides specific improvement directives when refinement is needed, ensuring high-quality research outputs.

### Paper Processing

This workflow transforms academic papers into structured summaries by accepting a paper URL, retrieving the document with the `PDFDownloader` tool, and using RAG-based filtering with Azure/OpenAI embeddings to process only the most relevant sections, generating a concise summary.

### Project Structure

```
NexusAI/
├── backend/                 # FastAPI backend service
│   ├── Dockerfile
│   ├── requirements.txt     # Python dependencies
│   └── nexusai/             # Core NexusAI folder
│   └── server/              # FastAPI server folder
├── platform/                # Next.js application
│   └── Dockerfile
├── docker-compose.yml       # Docker services configuration
└── .env.sample              # Environment variables template
```

## ⚙️ Getting Started

To immediately start using NexusAI, you can use our online demo [here](https://nexusai-platform.redisland-af07373c.westus2.azurecontainerapps.io). Alternatively, you can run the application locally by following the instructions below.

### Running with Docker

Start the application by running:
```bash
docker-compose up --build
```

If that doesn't work, try running it without the dash:
```bash
docker compose up --build
```

This command starts four services:
- PostgreSQL (database) - Port 5432
- Redis (caching) - Port 6379
- Backend (FastAPI) - Port 8000
- Platform (Next.js) - Port 3000

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

We would like to thank Dimant AI and Langchain for hosting the AgentCraft Hackathon. Special thanks to Microsoft Azure for providing sponsorship credits to deploy the application infrastructure, and to arXiv, Bing, CORE, and Serp for providing APIs to access academic papers.

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
