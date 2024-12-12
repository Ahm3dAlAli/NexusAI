from typing import Dict, Any, List, Optional
import re
import numpy as np
import torch
from transformers import AutoTokenizer
from adapters import AutoAdapterModel
from dataclasses import dataclass
from scipy.spatial.distance import cosine

@dataclass
class StyleMetrics:
    style_similarity: float
    technical_content: float

class ScientificMetrics:
    """Evaluates academic rigor by comparing against CVPR-style meta-reviews using SPECTER2."""
    
    def __init__(self, reference_texts: Optional[List[str]] = None):
        """
        Initialize the metrics evaluator with optional custom reference texts.
        
        Args:
            reference_texts: Optional list of reference academic texts. If None, uses defaults.
        """
        # Initialize SPECTER2 model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
        self.model = AutoAdapterModel.from_pretrained('allenai/specter2_base')
        self.model.load_adapter("allenai/specter2", source="hf", 
                              load_as="proximity", set_active=True)
        
        self.reference_texts = reference_texts or [
            """
            Recent advances in computer vision have been driven by deep learning approaches.
            This survey provides a comprehensive analysis of current methods and their theoretical foundations.
            We systematically categorize existing methods based on architectural choices and learning paradigms.
            Our analysis reveals several key trends: (1) increasing adoption of attention mechanisms,
            (2) emergence of efficient training strategies, and (3) focus on scalable architectures.
            Through extensive experimentation on standard benchmarks [1,2,3], we demonstrate the effectiveness
            of these approaches. Results indicate significant improvements over previous methods (p < 0.01).
            Future research directions include addressing computational efficiency and model interpretability.
            """,
            """
            This meta-analysis examines recent developments in transformer architectures for vision tasks.
            We review 50 papers from top conferences (CVPR, ICCV, ECCV) published between 2020-2024.
            The methodology follows standard systematic review protocols, evaluating each paper on:
            technical novelty, experimental rigor, and practical impact.
            Our findings demonstrate a clear trend towards self-supervised learning approaches,
            with 75% of recent papers incorporating some form of unsupervised pre-training.
            Quantitative analysis shows average performance improvements of 8.5% (±1.2) on standard benchmarks.
            We identify three primary research directions that warrant further investigation.
            """
        ]
        
        # Precompute reference embeddings
        self.reference_embeddings = self._get_embeddings(self.reference_texts)

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get SPECTER2 embeddings for a list of texts."""
        inputs = self.tokenizer(texts, padding=True, truncation=True,
                              return_tensors="pt", return_token_type_ids=False, 
                              max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Take the first token ([CLS]) embeddings
        return outputs.last_hidden_state[:, 0, :].numpy()

    def evaluate(self, result: Dict[str, Any], query_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyzes scientific quality through multiple dimensions.
        
        Args:
            result: Response containing answer text and metadata
            query_data: Original query parameters
            
        Returns:
            Dictionary of scientific metrics:
                - scientific_structure (0-1): Academic structure compliance
                - academic_rigor (0-1): Similarity to CVPR-style writing
                - technical_depth (0-1): Depth of technical discussion
        """
        text = str(result.get("answer", result.get("content", "")))
        
        if not text.strip():
            return {
                "scientific_structure": 0.0,
                "academic_rigor": 0.0,
                "technical_depth": 0.0
            }
        
        structure_metrics = self._evaluate_structure(text)
        style_metrics = self._evaluate_academic_style(text)
        
        metrics = {
            "scientific_structure": structure_metrics,
            "academic_rigor": style_metrics.style_similarity,
            "technical_depth": style_metrics.technical_content
        }
        
        if len(text.split()) < 50:
            penalty = max(0.5, len(text.split()) / 50)
            metrics = {k: v * penalty for k, v in metrics.items()}
            
        return metrics

    def _evaluate_academic_style(self, text: str) -> StyleMetrics:
        """Evaluate academic writing style and technical depth using SPECTER2."""
        try:
            # Get embedding for input text
            text_embedding = self._get_embeddings([text])[0]
            
            # Calculate cosine similarities with reference texts
            similarities = [
                1 - cosine(text_embedding, ref_embedding)
                for ref_embedding in self.reference_embeddings
            ]
            max_similarity = float(np.max(similarities))
        except Exception as e:
            print(f"Error in style evaluation: {e}")
            max_similarity = 0.0
        
        # Technical terms evaluation
        technical_terms = {
            'methodology': [
                "algorithm", "methodology", "framework", "architecture",
                "implementation", "procedure", "protocol"
            ],
            'analysis': [
                "empirical", "theoretical", "quantitative", "statistical",
                "analytical", "comparative", "systematic"
            ],
            'evaluation': [
                "benchmark", "baseline", "ablation", "analysis",
                "performance", "metric", "evaluation"
            ],
            'scientific': [
                "hypothesis", "experiment", "observation", "evidence",
                "validation", "verification", "replication"
            ]
        }
        
        # Calculate weighted technical score
        category_scores = []
        text_lower = text.lower()
        for category, terms in technical_terms.items():
            category_hits = sum(term in text_lower for term in terms)
            category_scores.append(min(1.0, category_hits / len(terms)))
        
        technical_score = sum(category_scores) / len(technical_terms)
        
        return StyleMetrics(
            style_similarity=max_similarity,
            technical_content=technical_score
        )

    def _evaluate_content_relevance(self, text: str, query_data: Dict[str, Any]) -> float:
        """Evaluate how well the content addresses the query topic using SPECTER2."""
        query = query_data.get("query", "")
        if not query:
            return 1.0
        
        try:
            # Get embeddings
            embeddings = self._get_embeddings([query, text])
            query_embedding, text_embedding = embeddings[0], embeddings[1]
            
            # Calculate semantic similarity
            similarity = 1 - cosine(query_embedding, text_embedding)
            return float(similarity)
        except Exception as e:
            print(f"Error in content relevance evaluation: {e}")
            # Fallback to term-based matching
            query_terms = re.findall(r'\w+', query.lower())
            query_terms = [term for term in query_terms if len(term) > 3]
            
            if not query_terms:
                return 1.0
                
            text_lower = text.lower()
            term_matches = sum(term in text_lower for term in query_terms)
            
            return min(1.0, term_matches / len(query_terms))
            

    def _evaluate_structure(self, text: str) -> float:
        """Evaluate academic structure compliance."""
        structure_elements = {
            'methodology': [
                "method", "approach", "technique", "algorithm", "framework",
                "procedure", "protocol", "implementation", "process"
            ],
            'results': [
                "result", "finding", "performance", "accuracy", "evaluation",
                "outcome", "achievement", "measurement", "metric", "score"
            ],
            'analysis': [
                "analysis", "comparison", "study", "investigation",
                "examination", "assessment", "evaluation", "interpretation"
            ],
            'background': [
                "previous", "prior", "existing", "literature", "background",
                "context", "foundation", "basis", "motivation"
            ],
            'conclusion': [
                "conclusion", "future work", "directions", "summary",
                "recommendation", "implication", "contribution", "impact"
            ]
        }
        
        # Calculate weighted scores based on section ordering
        scores = []
        last_found_index = -1
        
        for category, terms in structure_elements.items():
            # Find the earliest occurrence of any term in this category
            positions = [text.lower().find(term) for term in terms]
            positions = [pos for pos in positions if pos != -1]
            
            if positions:
                current_pos = min(positions)
                # Check if sections are in expected order
                if current_pos > last_found_index:
                    scores.append(1.0)
                else:
                    scores.append(0.5)  # Penalty for out of order sections
                last_found_index = current_pos
            else:
                scores.append(0.0)
        
        return sum(scores) / len(structure_elements)

    