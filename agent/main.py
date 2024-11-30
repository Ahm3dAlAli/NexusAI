import asyncio
import argparse
from langchain_core.tools import BaseTool

from .tools.functions import download_paper, search_papers, ask_human_feedback
from .workflow.nodes import WorkflowNodes
from .workflow.graph import ResearchWorkflow

def setup_tools() -> list[BaseTool]:
    """Setup the tools available to the agent."""
    return [download_paper, search_papers, ask_human_feedback]

async def process_query(query: str, workflow: ResearchWorkflow) -> str:
    """Process a single research query."""
    result = await workflow.process_query(query)

    # Check for errors
    if "error" in result:
        print(f"Error: {result['error']}")
        return result["error"]

    return result["answer"]

def display_banner():
    """Display the application banner."""
    banner = """
    ╔═════════════════════════════╗
    ║          NexusAI            ║
    ╚═════════════════════════════╝
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

def main():
    parser = argparse.ArgumentParser(
        description="NexusAI"
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
                print(f"{'=' * 35} Results {'=' * 35}\n\n{result}\n{'=' * 80}")
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
        print(f"{'=' * 36} Result {'=' * 36}\n\n{result}\n{'=' * 80}")

if __name__ == "__main__":
    main()