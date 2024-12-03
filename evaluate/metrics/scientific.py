from typing import Dict, Any, List
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ScientificMetrics:
    """Evaluates academic rigor by comparing against CVPR-style meta-reviews."""
    
    def __init__(self):
        # Initialize TF-IDF vectorizer for text comparison
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # CVPR-style reference texts
        self.reference_texts = [
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
        self.reference_embeddings = self.vectorizer.fit_transform(self.reference_texts)

    def evaluate(self, result: Dict[str, Any], query_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyzes scientific quality through multiple dimensions.
        
        Args:
            result: Response containing answer text and metadata
            query_data: Original query parameters
            
        Returns:
            Dictionary of scientific metrics:
                - citation_quality (0-1): Quality of citations
                - scientific_structure (0-1): Academic structure compliance
                - academic_rigor (0-1): Similarity to CVPR-style writing
                - technical_depth (0-1): Depth of technical discussion
        """
        text = str(result.get("answer", ""))
        
        # Base citation metrics
        citation_metrics = self._evaluate_citations(text)
        
        # Structure and content metrics
        structure_metrics = self._evaluate_structure(text)
        
        # Academic writing style metrics
        style_metrics = self._evaluate_academic_style(text)
        
        # Combine all metrics
        return {
            "citation_quality": citation_metrics,
            "scientific_structure": structure_metrics,
            "academic_rigor": style_metrics["style_similarity"],
            "technical_depth": style_metrics["technical_content"]
        }

    def _evaluate_citations(self, text: str) -> float:
        """Evaluate citation quality and consistency."""
        # Standard citations
        citations = len(re.findall(r"\[\d+\]|\(\d{4}\)", text))
        dois = len(re.findall(r"doi\.org|DOI:", text))
        urls = len(re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text))
        
        # Citation consistency
        consistent_format = len(set(re.findall(r"\[\d+\]", text))) > 0  # Check if consistent citation format is used
        
        # Normalize and combine scores
        citation_score = (citations + dois + urls) / (3 * max(1, citations + dois + urls))
        return citation_score * (1.2 if consistent_format else 1.0)  # Bonus for consistent formatting

    def _evaluate_structure(self, text: str) -> float:
        """Evaluate academic structure compliance."""
        structure_elements = {
            'methodology': ["method", "approach", "technique", "algorithm", "framework"],
            'results': ["result", "finding", "performance", "accuracy", "evaluation"],
            'analysis': ["analysis", "comparison", "study", "investigation"],
            'background': ["previous", "prior", "existing", "literature"],
            'conclusion': ["conclusion", "future work", "directions"]
        }
        
        scores = []
        for category, terms in structure_elements.items():
            has_element = any(term in text.lower() for term in terms)
            scores.append(float(has_element))
            
        return sum(scores) / len(structure_elements)

    def _evaluate_academic_style(self, text: str) -> Dict[str, float]:
        """Evaluate academic writing style and technical depth."""
        # Convert text to TF-IDF vector
        text_vector = self.vectorizer.transform([text])
        
        # Calculate similarity with reference texts
        similarities = cosine_similarity(text_vector, self.reference_embeddings)
        max_similarity = float(np.max(similarities))
        
        # Evaluate technical content
        technical_terms = [
            "algorithm", "methodology", "framework", "architecture",
            "empirical", "theoretical", "quantitative", "statistical",
            "benchmark", "baseline", "ablation", "analysis"
        ]
        
        technical_score = sum(term in text.lower() for term in technical_terms) / len(technical_terms)
        
        return {
            "style_similarity": max_similarity,
            "technical_content": technical_score
        }