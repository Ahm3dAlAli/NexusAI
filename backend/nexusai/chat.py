import asyncio

from langchain_core.messages import SystemMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langsmith import traceable
from nexusai.config import LLM_PROVIDER
from nexusai.models.llm import ModelProviderType
from nexusai.models.outputs import PaperOutput
from nexusai.prompts.chat_prompts import create_paper_prompt
from nexusai.tools.paper_downloader import PaperDownloader
from nexusai.utils.logger import logger


@traceable()
async def process_paper(url: str) -> PaperOutput | None:
    """Process a paper URL and generate a structured response using GPT-4."""
    logger.info(f"Creating paper for URL: {url}")

    # Initialize the LLM
    if LLM_PROVIDER == ModelProviderType.openai:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, max_tokens=16384)
    elif LLM_PROVIDER == ModelProviderType.azureopenai:
        llm = AzureChatOpenAI(
            azure_deployment="gpt-4o-mini", temperature=0.0, max_tokens=16384
        )
    else:
        raise ValueError(f"Invalid LLM provider: {LLM_PROVIDER}")

    # Download paper handling failed requests
    try:
        downloader = PaperDownloader(query=None)
        content = await asyncio.get_event_loop().run_in_executor(
            None, downloader.download, url
        )
        if not content:
            return
    except Exception as e:
        logger.error(f"Error downloading paper: {e}")
        return

    system_prompt = SystemMessage(
        content=create_paper_prompt.format(url=url, content=content)
    )

    # Invoke the LLM
    structured_llm = llm.with_structured_output(PaperOutput)
    return await structured_llm.ainvoke([system_prompt])
