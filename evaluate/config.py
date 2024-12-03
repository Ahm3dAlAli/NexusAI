
import os
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from dataclasses import dataclass, field
from enum import Enum

load_dotenv()

class ServiceType(Enum):
    """Types of services that can be evaluated."""
    OUR_AGENT = "our_agent"
    PERPLEXITY = "perplexity"


@dataclass
class ServiceConfig:
    """Configuration for individual services."""
    enabled: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    batch_size: Optional[int] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None

@dataclass
class EvalConfig:
    """Evaluation configuration."""
    # API Keys
    PERPLEXITY_API_KEY: str = field(default_factory=lambda: os.getenv("PERPLEXITY_API_KEY", ""))
    OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    CORE_API_KEY: str = field(default_factory=lambda: os.getenv("CORE_API_KEY", ""))
    
    # Test queries with expected results
    DEFAULT_QUERIES: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "query": "Find 8 papers on quantum machine learning",
            "expected_papers": 8,
            "min_year": None,
            "max_year": None,
            "required_elements": ["title", "authors", "abstract"]
        },
        {
            "query": "Find papers on CRISPR applications in genetic disorders from 2024",
            "expected_papers": None,
            "min_year": 2024,
            "max_year": 2024,
            "required_elements": ["title", "year", "abstract"]
        },
    ])
    
    # Evaluation parameters
    NUM_RUNS: int = 3  # Number of evaluation runs
    TIMEOUT: int = 300  # Maximum time per query in seconds
    PARALLEL_QUERIES: bool = True
    MAX_CONCURRENT_QUERIES: int = 3
    
    # Service configurations
    SERVICES: Dict[ServiceType, ServiceConfig] = field(default_factory=lambda: {
        ServiceType.OUR_AGENT: ServiceConfig(
            model_name="gpt-4o-mini"
        ),
        ServiceType.PERPLEXITY: ServiceConfig(
            model_name="gpt-4.0-mini",  # Updated model name
            api_key=os.getenv("PERPLEXITY_API_KEY")
        )
    })
    
    # Metrics configuration
    METRIC_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        "response_time": 0.2,
        "paper_coverage": 0.3,
        "citation_quality": 0.2,
        "answer_relevance": 0.15,
        "scientific_accuracy": 0.15
    })
    
    # Validation thresholds
    THRESHOLDS: Dict[str, float] = field(default_factory=lambda: {
        "min_success_rate": 0.8,
        "max_latency_p95": 120.0,  # Increased to account for CORE API latency
        "min_paper_coverage": 0.7,
        "min_citation_quality": 0.6,
        "min_scientific_accuracy": 0.7
    })
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of validation errors."""
        errors = []
        
        # Validate required API keys
        required_keys = {
            "PERPLEXITY_API_KEY": self.PERPLEXITY_API_KEY,
            "OPENAI_API_KEY": self.OPENAI_API_KEY,
            "CORE_API_KEY": self.CORE_API_KEY
        }
        
        for key_name, key_value in required_keys.items():
            if not key_value:
                errors.append(f"Missing {key_name}")
            
        # Validate metric weights
        weight_sum = sum(self.METRIC_WEIGHTS.values())
        if abs(weight_sum - 1.0) > 0.001:  # Allow for small floating-point differences
            errors.append(f"Metric weights must sum to 1.0 (current sum: {weight_sum})")
            
        return errors

    def get_enabled_services(self) -> List[ServiceType]:
        """Get list of enabled services."""
        return [svc for svc, cfg in self.SERVICES.items() if cfg.enabled]