from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from mem0 import MemoryClient

from nexusai.config import MEM0_API_KEY, MEM0_ORG_ID, MEM0_PROJECT_ID
from nexusai.utils.logger import logger

class Message(BaseModel):
    role: str = Field(description="Role of the message sender (user or assistant)")
    content: str = Field(description="Content of the message")

class AddMemoryInput(BaseModel):
    messages: List[Message] = Field(description="List of messages to add to memory")
    user_id: str = Field(description="ID of the user associated with these messages")
    output_format: str = Field(description="Version format for the output", default="v1.1")
    metadata: Optional[Dict[str, Any]] = Field(description="Additional metadata", default=None)

class SearchMemoryInput(BaseModel):
    query: str = Field(description="The search query string")
    user_id: str = Field(description="ID of the user to search memories for")
    filters: Dict[str, Any] = Field(
        description="Filters to apply to the search",
        default_factory=lambda: {"version": "v2"}
    )

class GetAllMemoryInput(BaseModel):
    user_id: str = Field(description="ID of the user to get memories for")
    version: str = Field(description="Version of the memory to retrieve", default="v2")
    filters: Dict[str, Any] = Field(
        description="Filters to apply to the retrieval",
        default_factory=dict
    )
    page: int = Field(description="Page number for pagination", default=1)
    page_size: int = Field(description="Number of items per page", default=50)

class MemoryTools:
    """Memory tools implementation using Mem0."""
    
    def __init__(self):
        self.client = MemoryClient(
            api_key=MEM0_API_KEY,
            org_id=MEM0_ORG_ID,
            project_id=MEM0_PROJECT_ID
        ) if MEM0_API_KEY else None

    def add_memory(self, messages: List[Message], user_id: str, 
                  output_format: str = "v1.1", 
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add messages to memory."""
        if not self.client:
            return "Memory service not configured"
        
        try:
            message_dicts = [msg.dict() for msg in messages]
            result = self.client.add(
                message_dicts, 
                user_id=user_id,
                output_format=output_format,
                metadata=metadata
            )
            return "Successfully stored memory"
        except Exception as e:
            logger.error(f"Error adding memory: {str(e)}")
            return f"Error adding memory: {str(e)}"

    def search_memory(self, query: str, user_id: str, 
                     filters: Optional[Dict[str, Any]] = None) -> str:
        """Search through memories."""
        if not self.client:
            return "Memory service not configured"
        
        try:
            results = self.client.search(
                query=query,
                user_id=user_id,
                filters=filters or {}
            )
            return str(results)
        except Exception as e:
            logger.error(f"Error searching memory: {str(e)}")
            return f"Error searching memory: {str(e)}"

    def get_all_memory(self, user_id: str, version: str = "v2",
                      filters: Optional[Dict[str, Any]] = None,
                      page: int = 1, page_size: int = 50) -> str:
        """Retrieve all memories matching criteria."""
        if not self.client:
            return "Memory service not configured"
        
        try:
            results = self.client.get_all(
                version=version,
                filters=filters or {"user_id": user_id},
                page=page,
                page_size=page_size
            )
            return str(results)
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            return f"Error retrieving memories: {str(e)}"

    def get_tools(self) -> List[StructuredTool]:
        """Get the memory tools."""
        return [
            StructuredTool(
                name="add_memory",
                description="Add new messages to memory with associated metadata",
                func=self.add_memory,
                args_schema=AddMemoryInput
            ),
            StructuredTool(
                name="search_memory",
                description="Search through memories with a query and filters",
                func=self.search_memory,
                args_schema=SearchMemoryInput
            ),
            StructuredTool(
                name="get_all_memory",
                description="Retrieve all memories matching specified filters",
                func=self.get_all_memory,
                args_schema=GetAllMemoryInput
            )
        ]