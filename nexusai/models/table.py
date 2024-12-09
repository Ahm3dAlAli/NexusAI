from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class TableMetadata(BaseModel):
    """Metadata for a table extracted from a PDF."""
    page_number: int
    table_index: int
    row_count: int
    column_count: int
    source_paper: Optional[str] = None
    table_caption: Optional[str] = None
    context_text: Optional[str] = None

class TableData(BaseModel):
    """Representation of table data and metadata."""
    data: Dict[str, List[Any]]  # Column name -> list of values
    metadata: TableMetadata

class TableComparisonResult(BaseModel):
    """Results of comparing multiple tables."""
    structural_differences: List[str]
    content_differences: List[str]
    statistical_summary: Dict[str, Any]
    similarity_score: float

class TableSearchResult(BaseModel):
    """Results of searching for similar tables."""
    query_table: TableData
    similar_tables: List[TableData]
    similarity_scores: List[float]
    match_criteria: Dict[str, float]