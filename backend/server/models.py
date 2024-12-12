from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request schema for a query."""

    query: str
