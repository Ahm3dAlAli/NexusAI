
import asyncio
import argparse
from typing import Optional
import json
from pydantic import BaseModel, Field
from langchain_core.tools import Tool

from .tools.core_api import CoreAPIWrapper
from .tools.pdf_tools import download_paper
from .workflow.nodes import WorkflowNodes
from .workflow.graph import ResearchWorkflow

class SearchPapersInput(BaseModel):
    """Input schema for paper search."""
    query: str = Field(description="The query to search for on the selected archive.")
    max_papers: int = Field(
        description="Maximum number of papers to return (1-10).",
        default=1,
        ge=1,
        le=10
    )

def setup_tools() -> list[Tool]:
    """Setup the tools available to the agent."""
    return [
        Tool(
            name="search-papers",
            description="Search for scientific papers using the CORE API.",
            func=lambda x: CoreAPIWrapper().search(**json.loads(x)),
            args_schema=SearchPapersInput
        ),
        Tool(
            name="download-paper",
            description="Download a specific scientific paper from a given URL.",
            func=download_paper
        ),
        Tool(
            name="ask-human-feedback",
            description="Ask for human feedback when encountering unexpected errors.",
            func=lambda x: input(x)
        )
    ]

async def process_query(query: str, workflow: ResearchWorkflow) -> Optional[str]:
    """Process a single research query."""
    try:
        result = await workflow.process_query(query)
        
        # Check for errors
        if isinstance(result, dict) and "error" in result:
            print(f"Error: {result['error']}")
            return None
            
        if not result or "messages" not in result:
            print("No results found")
            return None
        
        # Get the last message content
        messages = result["messages"]
        if not messages:
            return None
        
        return messages[-1].content
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return None

def display_banner():
    """Display the application banner."""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║      Scientific Paper Research Agent      ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)

def display_help():
    """Display help information."""
    help_text = """
    Available Commands:
    ------------------
    - Type your research query to process it
    - 'help' to display this help message
    - 'exit' to quit the application
    
    Query Examples:
    --------------
    - "Find recent papers about quantum computing"
    - "Download and summarize: [paper_url]"
    - "Find papers about machine learning from 2023-2024"
    """
    print(help_text)

def main() -> None:
    """Main entry point for the scientific paper agent."""
    parser = argparse.ArgumentParser(
        description="Scientific Paper Research Agent"
    )
    parser.add_argument(
        "query",
        nargs="?",
        type=str,
        help="Research query to process"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()

    # Setup workflow
    tools = setup_tools()
    nodes = WorkflowNodes(tools)
    workflow = ResearchWorkflow(nodes)

    if args.interactive:
        display_banner()
        display_help()
        print("\nEntering interactive mode. Type 'exit' to quit.\n")
        
        while True:
            try:
                query = input("\nEnter your research query: ").strip()
                
                if query.lower() == 'exit':
                    print("\nGoodbye!")
                    break
                    
                if query.lower() == 'help':
                    display_help()
                    continue
                    
                if not query:
                    continue
                
                print("\nProcessing your query...\n")
                result = asyncio.run(process_query(query, workflow))
                
                if result:
                    print("\nResults:")
                    print("=" * 80)
                    print(result)
                    print("=" * 80)
                else:
                    print("\nNo results found.")
                    
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                
    else:
        # Process single query
        if not args.query:
            parser.error("Query is required when not in interactive mode")
            
        print("Processing your query...\n")
        result = asyncio.run(process_query(args.query, workflow))
        
        if result:
            print("\nResults:")
            print("=" * 80)
            print(result)
            print("=" * 80)
        else:
            print("No results found.")

if __name__ == "__main__":
    main()