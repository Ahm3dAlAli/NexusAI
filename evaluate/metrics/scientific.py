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
            
            # Calculate cosine similarities with reference texts for style
            style_similarities = [
                1 - cosine(text_embedding, ref_embedding)
                for ref_embedding in self.reference_embeddings
            ]
            style_similarity = float(np.max(style_similarities))
            
            # Calculate technical depth using semantic components
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if not sentences:
                return StyleMetrics(style_similarity=style_similarity, technical_content=0.0)
            
            # Get embeddings for each sentence
            sentence_embeddings = self._get_embeddings(sentences)
            
            # Compare each sentence against reference texts and calculate technical scores
            sentence_scores = []
            for sent_embedding in sentence_embeddings:
                similarities = [
                    1 - cosine(sent_embedding, ref_embedding)
                    for ref_embedding in self.reference_embeddings
                ]
                sentence_scores.append(np.max(similarities))
            
            # Calculate final technical score
            technical_score = float(np.mean(sentence_scores))
            
            return StyleMetrics(
                style_similarity=style_similarity,
                technical_content=technical_score
            )
            
        except Exception as e:
            print(f"Error in style evaluation: {e}")
            return StyleMetrics(style_similarity=0.0, technical_content=0.0)


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
        """
        Evaluate academic structure compliance using semantic sentence embeddings.
        Returns a float score between 0 and 1.
        """
        # Split text into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return 0.0

        # Get embeddings for all sentences
        sentence_embeddings = self._get_embeddings(sentences)
        
        # Define semantic section prototypes
        section_prototypes = {
            'introduction': [
                "This paper presents", "We introduce", "This work explores",
                "We propose", "This study investigates"
            ],
            'background': [
                "Prior work has shown", "Previous research indicates",
                "Existing methods include", "Recent studies have demonstrated"
            ],
            'methodology': [
                "We implement", "Our approach consists of", "The method involves",
                "We develop", "The system architecture"
            ],
            'results': [
                "Our experiments show", "The results demonstrate",
                "Performance evaluation indicates", "Analysis reveals"
            ],
            'discussion': [
                "These findings suggest", "The implications of",
                "Our analysis indicates", "We observe that"
            ],
            'conclusion': [
                "In conclusion", "We conclude", "Future work",
                "This work demonstrates", "Our contributions include"
            ]
        }
        
        # Get embeddings for section prototypes
        prototype_embeddings = {}
        for section, examples in section_prototypes.items():
            prototype_embeddings[section] = self._get_embeddings(examples)
        
        # Identify sections in the text
        identified_sections = []
        current_section = None
        section_scores = []
        
        for sent_idx, sent_embedding in enumerate(sentence_embeddings):
            # Calculate similarity with each section prototype
            section_similarities = {}
            for section, proto_embeddings in prototype_embeddings.items():
                # Calculate average similarity with all examples for this section
                similarities = [
                    1 - cosine(sent_embedding, proto_emb)
                    for proto_emb in proto_embeddings
                ]
                section_similarities[section] = np.mean(similarities)
            
            # Get most similar section if similarity is above threshold
            max_section = max(section_similarities.items(), key=lambda x: x[1])
            if max_section[1] > 0.6:  # Similarity threshold
                if max_section[0] != current_section:
                    identified_sections.append(max_section[0])
                    current_section = max_section[0]
        
        # Score based on section coverage and ordering
        expected_order = ['introduction', 'background', 'methodology', 
                        'results', 'discussion', 'conclusion']
        
        # Calculate coverage score
        unique_sections = set(identified_sections)
        coverage_score = len(unique_sections) / len(expected_order)
        
        # Calculate ordering score
        ordering_score = 0.0
        if identified_sections:
            # Create a mapping of section to its position in expected order
            expected_positions = {section: i for i, section in enumerate(expected_order)}
            
            # Check if sections appear in relatively correct order
            correct_order_count = 0
            for i in range(len(identified_sections) - 1):
                current_pos = expected_positions.get(identified_sections[i], -1)
                next_pos = expected_positions.get(identified_sections[i + 1], -1)
                if current_pos <= next_pos:
                    correct_order_count += 1
            
            # Calculate ordering score based on correct transitions
            if len(identified_sections) > 1:
                ordering_score = correct_order_count / (len(identified_sections) - 1)
            else:
                ordering_score = 1.0  # Single section is considered correctly ordered
        
        # Calculate overall score with weights
        coverage_weight = 0.6
        ordering_weight = 0.4
        final_score = (coverage_weight * coverage_score + 
                    ordering_weight * ordering_score)
        
        return float(final_score)
    
def _evaluate_section_coherence(self, sentences: List[str], 
                              section_embeddings: np.ndarray) -> float:
    """
    Evaluate the coherence within identified sections.
    Returns a float score between 0 and 1.
    """
    if len(sentences) < 2:
        return 1.0
    
    # Calculate cosine similarity between consecutive sentences
    coherence_scores = []
    for i in range(len(section_embeddings) - 1):
        similarity = 1 - cosine(section_embeddings[i], 
                              section_embeddings[i + 1])
        coherence_scores.append(similarity)
    
    return float(np.mean(coherence_scores))