
from typing import Annotated, Sequence, TypedDict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The state of the agent during the paper research process.
    
    Attributes:
        requires_research (bool): Indicates if the query needs research
        num_feedback_requests (int): Number of times feedback was requested
        is_good_answer (bool): Whether the current answer meets quality standards
        messages (Sequence[BaseMessage]): History of messages in the conversation
        current_papers (List[str]): IDs of papers currently being processed
        search_depth (int): Current depth of the search process
        error_count (int): Number of errors encountered
    """
    requires_research: bool
    num_feedback_requests: int
    is_good_answer: bool
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_papers: List[str]
    search_depth: int
    error_count: int

class PaperMetadata(BaseModel):
    """
    Metadata for a scientific paper.
    
    Attributes:
        paper_id: Unique identifier for the paper
        title: Paper title
        authors: List of authors
        published_date: Publication date
        abstract: Paper abstract
        urls: URLs where the paper can be accessed
        citation_count: Number of citations
        download_url: Direct download URL if available
    """
    paper_id: str = Field(..., description="Unique identifier for the paper")
    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of paper authors")
    published_date: Optional[str] = Field(None, description="Publication date of the paper")
    abstract: Optional[str] = Field(None, description="Paper abstract")
    urls: List[str] = Field(default_factory=list, description="URLs to access the paper")
    citation_count: Optional[int] = Field(None, description="Number of citations")
    download_url: Optional[str] = Field(None, description="Direct download URL")

class SearchResult(BaseModel):
    """
    Result of a paper search operation.
    
    Attributes:
        query: The search query used
        papers: List of paper metadata
        total_results: Total number of results found
        processed_results: Number of results processed
        error: Error message if search failed
    """
    query: str = Field(..., description="Search query used")
    papers: List[PaperMetadata] = Field(
        default_factory=list,
        description="List of papers found"
    )
    total_results: int = Field(0, description="Total number of results found")
    processed_results: int = Field(0, description="Number of results processed")
    error: Optional[str] = Field(None, description="Error message if search failed")

class ProcessingError(BaseModel):
    """
    Error that occurred during paper processing.
    
    Attributes:
        error_type: Type of error
        message: Error message
        paper_id: ID of paper being processed when error occurred
        step: Processing step where error occurred
        recoverable: Whether the error is recoverable
    """
    error_type: str = Field(..., description="Type of error encountered")
    message: str = Field(..., description="Error message")
    paper_id: Optional[str] = Field(None, description="ID of paper being processed")
    step: str = Field(..., description="Step where error occurred")
    recoverable: bool = Field(True, description="Whether error is recoverable")

def create_initial_state() -> AgentState:
    """
    Create the initial state for the agent.
    
    Returns:
        AgentState: Initial state with default values
    """
    return AgentState(
        requires_research=False,
        num_feedback_requests=0,
        is_good_answer=False,
        messages=[],
        current_papers=[],
        search_depth=0,
        error_count=0
    )

def update_state_on_error(state: AgentState, error: ProcessingError) -> AgentState:
    """
    Update state when an error occurs.
    
    Args:
        state: Current agent state
        error: Error that occurred
        
    Returns:
        AgentState: Updated state
    """
    state["error_count"] += 1
    
    if error.paper_id and error.paper_id in state["current_papers"]:
        state["current_papers"].remove(error.paper_id)
    
    if not error.recoverable:
        state["requires_research"] = False
        state["is_good_answer"] = True  # Force end of processing
        
    return state