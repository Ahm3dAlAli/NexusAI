from typing import Optional
from pydantic import BaseModel

class FigureMetadata(BaseModel):
    """Metadata for a figure extracted from a PDF."""
    page_number: int
    figure_index: int
    width: int
    height: int
    content_type: str
    nearby_text: Optional[str] = None
    caption: Optional[str] = None
    source_paper: Optional[str] = None

class FigureAnalysis(BaseModel):
    """Analysis results from Claude for a scientific figure."""
    figure_type: str  # e.g., "line graph", "bar chart", "scatter plot"
    components: str   # Main elements and components identified
    findings: str     # Key insights and findings
    methodology: str  # Methods or approaches used
    quality_assessment: str  # Assessment of data representation
    limitations: str  # Identified limitations or potential improvements
    raw_analysis: str # Complete raw analysis from Claude

class FigureComparison(BaseModel):
    """Results of comparing multiple figures."""
    visual_similarities: list[str]
    visual_differences: list[str]
    methodological_comparison: str
    content_alignment: str
    complementary_insights: list[str]
    recommendation: str
    raw_comparison: str

class FigureSearchResult(BaseModel):
    """Results of searching for similar figures."""
    query_figure: dict
    similar_figures: list[dict]
    similarity_scores: list[float]
    match_criteria: dict[str, float]