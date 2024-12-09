import io
from typing import List, Dict, Any
import pdfplumber
from langchain_core.tools import tool
from pydantic import BaseModel
from tabulate import tabulate
import pandas as pd

from nexusai.utils.logger import logger

class Table:
    """Represents a standardized table structure."""
    def __init__(self, data: pd.DataFrame, metadata: Dict[str, Any]):
        self.data = data
        self.metadata = metadata
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data.to_dict(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        df = pd.DataFrame.from_dict(data["data"])
        return cls(df, data["metadata"])

class TableExtractionInput(BaseModel):
    """Input schema for table extraction."""
    pdf_content: bytes
    page_numbers: List[int] | None = None

class TableComparisonInput(BaseModel):
    """Input schema for table comparison."""
    tables: List[Dict[str, Any]]
    comparison_type: str = "structure"  # Options: structure, content, statistics

class TableAnalyzer:
    """Tool for analyzing and comparing tables from PDFs."""
    
    def __extract_tables_from_pdf(self, pdf_content: bytes, page_numbers: List[int] | None = None) -> List[Table]:
        """Extract tables from PDF content."""
        tables = []
        pdf_file = io.BytesIO(pdf_content)
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                pages_to_process = page_numbers or range(len(pdf.pages))
                
                for page_num in pages_to_process:
                    if page_num >= len(pdf.pages):
                        continue
                        
                    page = pdf.pages[page_num]
                    extracted_tables = page.extract_tables()
                    
                    for table_idx, extracted_table in enumerate(extracted_tables):
                        # Convert to pandas DataFrame
                        df = pd.DataFrame(extracted_table[1:], columns=extracted_table[0])
                        
                        # Clean column names
                        df.columns = df.columns.str.strip()
                        
                        # Create metadata
                        metadata = {
                            "page_number": page_num + 1,
                            "table_index": table_idx + 1,
                            "row_count": len(df),
                            "column_count": len(df.columns)
                        }
                        
                        tables.append(Table(df, metadata))
                        
            return tables
            
        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {str(e)}")
            raise

    def __compare_tables(self, tables: List[Table], comparison_type: str) -> str:
        """Compare tables based on specified comparison type."""
        if not tables:
            return "No tables provided for comparison."
            
        if comparison_type == "structure":
            # Compare table structures (columns, data types)
            comparison = []
            for idx, table in enumerate(tables):
                columns = table.data.columns.tolist()
                dtypes = table.data.dtypes.to_dict()
                metadata = table.metadata
                
                comparison.append(
                    f"Table {idx + 1} (Page {metadata['page_number']}):\n"
                    f"- Columns: {columns}\n"
                    f"- Data types: {dtypes}\n"
                    f"- Dimensions: {metadata['row_count']}x{metadata['column_count']}\n"
                )
            
            return "\n".join(comparison)
            
        elif comparison_type == "content":
            # Compare actual content and highlight differences
            if len(tables) < 2:
                return "Need at least 2 tables for content comparison."
                
            base_table = tables[0].data
            differences = []
            
            for idx, table in enumerate(tables[1:], 1):
                # Find common columns
                common_cols = set(base_table.columns) & set(table.data.columns)
                if not common_cols:
                    differences.append(f"No common columns between Table 1 and Table {idx + 1}")
                    continue
                
                # Compare values in common columns
                for col in common_cols:
                    if not base_table[col].equals(table.data[col]):
                        differences.append(f"Different values in column '{col}' between Table 1 and Table {idx + 1}")
            
            return "\n".join(differences) if differences else "Tables have identical content in common columns."
            
        elif comparison_type == "statistics":
            # Generate statistical comparison
            stats = []
            for idx, table in enumerate(tables):
                numeric_cols = table.data.select_dtypes(include=['int64', 'float64']).columns
                if not len(numeric_cols):
                    stats.append(f"Table {idx + 1}: No numeric columns found.")
                    continue
                    
                table_stats = table.data[numeric_cols].describe()
                stats.append(f"Table {idx + 1} Statistics:\n{table_stats.to_string()}")
            
            return "\n\n".join(stats)
            
        else:
            return f"Unsupported comparison type: {comparison_type}"

    @tool("extract-tables", args_schema=TableExtractionInput)
    def extract_tables(self, pdf_content: bytes, page_numbers: List[int] | None = None) -> str:
        """Extract tables from a PDF document.
        
        Args:
            pdf_content: The binary content of the PDF file
            page_numbers: Optional list of specific pages to extract tables from
            
        Returns:
            A string describing the extracted tables
        """
        try:
            tables = self.__extract_tables_from_pdf(pdf_content, page_numbers)
            
            if not tables:
                return "No tables found in the specified pages."
            
            result = []
            for idx, table in enumerate(tables):
                metadata = table.metadata
                result.append(
                    f"\nTable {idx + 1} (Page {metadata['page_number']}):\n"
                    f"Dimensions: {metadata['row_count']}x{metadata['column_count']}\n"
                    f"Columns: {', '.join(table.data.columns.tolist())}\n"
                    f"Preview:\n{tabulate(table.data.head(), headers='keys', tablefmt='grid')}"
                )
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error extracting tables: {str(e)}"

    @tool("compare-tables", args_schema=TableComparisonInput)
    def compare_tables(self, tables: List[Dict[str, Any]], comparison_type: str = "structure") -> str:
        """Compare multiple tables using specified comparison method.
        
        Args:
            tables: List of table dictionaries (containing data and metadata)
            comparison_type: Type of comparison to perform (structure/content/statistics)
            
        Returns:
            A string containing the comparison results
        """
        try:
            # Convert table dictionaries back to Table objects
            table_objects = [Table.from_dict(table_dict) for table_dict in tables]
            return self.__compare_tables(table_objects, comparison_type)
            
        except Exception as e:
            return f"Error comparing tables: {str(e)}"