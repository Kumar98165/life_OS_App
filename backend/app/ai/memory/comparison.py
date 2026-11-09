"""LifeOS - Memory Comparison & Contradiction Engine.

Provides deterministic text normalization, exact duplicate detection,
semantic overlap scoring, and contradiction detection between candidate memories
and existing confirmed memories.
"""
import re
from typing import Optional, List, Dict, Any, Tuple
from app.models.ai import AIMemory


def normalize_memory_text(text: str) -> str:
    """Normalize text by lowercasing, stripping extra whitespaces, and removing punctuation."""
    if not text:
        return ""
    lowered = text.lower().strip()
    # Replace non-alphanumeric with single space
    cleaned = re.sub(r"[^\w\s]", " ", lowered)
    return " ".join(cleaned.split())


def extract_keywords(text: str) -> set[str]:
    """Extract significant keywords (> 2 chars) excluding common stop words."""
    stop_words = {
        "the", "and", "for", "that", "this", "with", "from", "user", "prefers",
        "likes", "wants", "is", "are", "was", "were", "to", "in", "on", "at",
        "by", "an", "a", "of", "it", "my", "your", "his", "her", "their"
    }
    normalized = normalize_memory_text(text)
    tokens = normalized.split()
    return {t for t in tokens if len(t) > 2 and t not in stop_words}


class MemoryComparisonEngine:
    """Detects duplicates, close similarities, and contradictions among memories."""

    # Common antonym / polarity pairs to deterministically flag contradictions
    POLARITY_PAIRS = [
        ("short", "detailed"),
        ("concise", "comprehensive"),
        ("morning", "evening"),
        ("morning", "night"),
        ("early", "late"),
        ("vegetarian", "non-vegetarian"),
        ("vegan", "meat"),
        ("hindi", "english"),
        ("dark", "light"),
        ("enable", "disable"),
        ("active", "inactive"),
    ]

    def check_duplicate_or_contradiction(
        self,
        candidate_key: str,
        candidate_value: str,
        candidate_type: str,
        existing_memories: List[AIMemory]
    ) -> Dict[str, Any]:
        """Compare candidate against existing user memories.

        Returns a dictionary:
        {
            "is_duplicate": bool,
            "duplicate_memory_id": Optional[str],
            "is_contradiction": bool,
            "contradicting_memory_id": Optional[str],
            "contradiction_reason": Optional[str],
            "similarity_score": float
        }
        """
        norm_key = normalize_memory_text(candidate_key)
        norm_val = normalize_memory_text(candidate_value)
        cand_keywords = extract_keywords(f"{candidate_key} {candidate_value}")

        for existing in existing_memories:
            ex_key = normalize_memory_text(existing.memory_key)
            ex_val = normalize_memory_text(existing.memory_value)

            # 1. Exact Duplicate (key or value match)
            if norm_key == ex_key and (norm_val == ex_val or existing.memory_type == candidate_type):
                if norm_val == ex_val:
                    return {
                        "is_duplicate": True,
                        "duplicate_memory_id": existing.id,
                        "is_contradiction": False,
                        "contradicting_memory_id": None,
                        "contradiction_reason": None,
                        "similarity_score": 1.0,
                    }

            # 2. Key Overlap & Polarity / Content Difference (Contradiction Check)
            ex_keywords = extract_keywords(f"{existing.memory_key} {existing.memory_value}")
            common_keywords = cand_keywords.intersection(ex_keywords)

            # If they share core domain concepts (e.g. "response", "style", "workout", "sleep")
            if len(common_keywords) >= 1:
                # Check for explicit polarity antonyms
                for w1, w2 in self.POLARITY_PAIRS:
                    if (w1 in norm_val and w2 in ex_val) or (w2 in norm_val and w1 in ex_val) or \
                       (w1 in norm_key and w2 in ex_key) or (w2 in norm_key and w1 in ex_key):
                        return {
                            "is_duplicate": False,
                            "duplicate_memory_id": None,
                            "is_contradiction": True,
                            "contradicting_memory_id": existing.id,
                            "contradiction_reason": f"Conflict detected between '{candidate_value}' and existing '{existing.memory_value}' ({w1} vs {w2})",
                            "similarity_score": 0.85,
                        }

                # Check if same key concept but distinctly different value (e.g. "prefers dark theme" vs "prefers light theme")
                if norm_key == ex_key and norm_val != ex_val:
                    return {
                        "is_duplicate": False,
                        "duplicate_memory_id": None,
                        "is_contradiction": True,
                        "contradicting_memory_id": existing.id,
                        "contradiction_reason": f"Update/replacement candidate for existing '{existing.memory_key}': '{existing.memory_value}'",
                        "similarity_score": 0.80,
                    }

            # 3. High Jaccard similarity without contradiction (near duplicate)
            union_keywords = cand_keywords.union(ex_keywords)
            if union_keywords:
                jaccard = len(common_keywords) / len(union_keywords)
                if jaccard >= 0.75:
                    return {
                        "is_duplicate": True,
                        "duplicate_memory_id": existing.id,
                        "is_contradiction": False,
                        "contradicting_memory_id": None,
                        "contradiction_reason": None,
                        "similarity_score": jaccard,
                    }

        return {
            "is_duplicate": False,
            "duplicate_memory_id": None,
            "is_contradiction": False,
            "contradicting_memory_id": None,
            "contradiction_reason": None,
            "similarity_score": 0.0,
        }


memory_comparison_engine = MemoryComparisonEngine()

