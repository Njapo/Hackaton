"""
progress_analyzer.py - Progress Analysis and Healing Score Computation

This module provides functions for:
- Computing cosine similarity between embeddings
- Calculating healing scores
- Generating progress trends
- Creating doctor-style assessments
"""

from typing import List, Optional, Tuple, Dict
import numpy as np
from . import models, schemas


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Compute cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Similarity score between -1 and 1 (typically 0 to 1 for normalized vectors)
    """
    if not embedding1 or not embedding2:
        return 0.0
    
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Compute cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return float(similarity)


def compute_healing_score(
    current_embedding: List[float],
    previous_embedding: List[float],
    higher_similarity_means_better: bool = False
) -> float:
    """
    Compute healing score based on embedding similarity.
    
    Args:
        current_embedding: Current image embedding
        previous_embedding: Previous/baseline image embedding
        higher_similarity_means_better: If True, high similarity = healing
                                         If False, low similarity = healing (condition improving/clearing)
        
    Returns:
        Healing score from 0 to 100
    """
    similarity = cosine_similarity(current_embedding, previous_embedding)
    
    # Normalize similarity from [-1, 1] to [0, 1]
    normalized_similarity = (similarity + 1) / 2
    
    if higher_similarity_means_better:
        # Higher similarity means healing (e.g., returning to normal skin)
        score = normalized_similarity * 100
    else:
        # Lower similarity means healing (condition is improving/changing from diseased state)
        score = (1 - normalized_similarity) * 100
    
    return max(0.0, min(100.0, score))


def analyze_trend(healing_scores: List[float]) -> str:
    """
    Analyze trend from a sequence of healing scores.
    
    Args:
        healing_scores: List of healing scores over time
        
    Returns:
        'improving', 'stable', or 'worsening'
    """
    if len(healing_scores) < 2:
        return 'stable'
    
    # Calculate average change
    changes = [healing_scores[i] - healing_scores[i-1] for i in range(1, len(healing_scores))]
    avg_change = np.mean(changes)
    
    # Thresholds
    if avg_change > 5:
        return 'improving'
    elif avg_change < -5:
        return 'worsening'
    else:
        return 'stable'


def generate_progress_prompt(
    current_entry: models.History,
    previous_entries: List[models.History],
    comparisons: List[Dict],
    average_healing_score: float,
    trend: str,
    section_name: str
) -> str:
    """
    Generate a comprehensive prompt for Gemini to create doctor-style assessment.
    
    Args:
        current_entry: Current history entry
        previous_entries: List of previous history entries for context
        comparisons: List of comparison data with healing scores
        average_healing_score: Overall healing score
        trend: 'improving', 'stable', or 'worsening'
        section_name: Name of the lesion section
        
    Returns:
        Formatted prompt for Gemini AI
    """
    # Format current predictions
    current_predictions = "\n".join([
        f"  - {pred['disease']}: {pred['confidence']:.1%} confidence"
        for pred in current_entry.disease_predictions
    ])
    
    # Format previous entries
    previous_context = ""
    for i, entry in enumerate(previous_entries, 1):
        top_pred = entry.disease_predictions[0] if entry.disease_predictions else {}
        previous_context += (
            f"\n{i}. {entry.timestamp.strftime('%Y-%m-%d %H:%M')}: "
            f"{top_pred.get('disease', 'Unknown')} "
            f"({top_pred.get('confidence', 0):.1%})"
        )
        if entry.user_notes:
            previous_context += f" - User notes: {entry.user_notes}"
    
    # Format comparisons
    comparison_text = ""
    for comp in comparisons:
        comparison_text += (
            f"\n  - Compared to {comp['previous_timestamp'].strftime('%Y-%m-%d')}: "
            f"Healing score: {comp['healing_percentage']:.1f}%, "
            f"Similarity: {comp['current_similarity']:.2f}"
        )
    
    prompt = f"""
SYSTEM INSTRUCTION:
You are SkinAI, a specialized dermatology AI assistant. You are reviewing a patient's progress for their skin condition.
Generate a comprehensive, doctor-style progress assessment that is professional, empathetic, and informative.

PATIENT CONTEXT:
Lesion/Section: {section_name}
Current Analysis Date: {current_entry.timestamp.strftime('%Y-%m-%d %H:%M')}

CURRENT FINDINGS:
Disease Predictions:
{current_predictions}

Patient Notes: {current_entry.user_notes or 'None provided'}

HISTORICAL CONTEXT:
Previous Entries:{previous_context}

PROGRESS ANALYSIS:
Overall Trend: {trend.upper()}
Average Healing Score: {average_healing_score:.1f}%

Detailed Comparisons:{comparison_text}

INSTRUCTIONS:
Generate a doctor-style progress report following this structure:

---
**PROGRESS ASSESSMENT - {section_name.upper()}**

**Current Condition:**
[Describe the current state based on the AI predictions and user notes]

**Comparison with Previous Entries:**
[Compare current findings with previous entries, highlighting changes]

**Healing Progress:**
- Overall Score: {average_healing_score:.1f}%
- Trend: {trend.capitalize()}
[Explain what the healing score indicates and whether the condition is improving, stable, or worsening]

**Clinical Observations:**
[Provide 2-3 key observations about the progression]

**Recommendations:**
1. [First recommendation]
2. [Second recommendation]
3. [Third recommendation]

**Next Steps:**
[Suggest when to take next follow-up photo and what to monitor]

**Note:** This is an AI-based educational analysis. Please consult a certified dermatologist for a precise diagnosis and treatment plan.
---

Be specific, use the data provided, and write in a professional yet patient-friendly tone.
"""
    
    return prompt


def compute_comparisons(
    current_entry: models.History,
    previous_entries: List[models.History]
) -> Tuple[List[Dict], float]:
    """
    Compute healing scores by comparing current entry with previous entries.
    
    Args:
        current_entry: Current history entry with embedding
        previous_entries: List of previous entries to compare against
        
    Returns:
        Tuple of (comparisons list, average healing score)
    """
    # Check if current entry has embedding
    current_embedding = current_entry.dino_embedding
    if current_embedding is None or (isinstance(current_embedding, list) and len(current_embedding) == 0):
        return [], 0.0
    
    # Ensure current_embedding is a list
    if not isinstance(current_embedding, list):
        current_embedding = list(current_embedding)
    
    comparisons = []
    healing_scores = []
    
    for prev_entry in previous_entries:
        # Check if previous entry has embedding
        prev_embedding = prev_entry.dino_embedding
        if prev_embedding is None or (isinstance(prev_embedding, list) and len(prev_embedding) == 0):
            continue
        
        # Ensure prev_embedding is a list
        if not isinstance(prev_embedding, list):
            prev_embedding = list(prev_embedding)
        
        try:
            similarity = cosine_similarity(current_embedding, prev_embedding)
            
            # Lower similarity typically means improvement (lesion changing/healing)
            healing_score = compute_healing_score(
                current_embedding,
                prev_embedding,
                higher_similarity_means_better=False
            )
            
            healing_scores.append(healing_score)
            
            prev_top_disease = prev_entry.disease_predictions[0]['disease'] if prev_entry.disease_predictions else 'Unknown'
            
            comparisons.append({
                'previous_entry_id': prev_entry.id,
                'previous_timestamp': prev_entry.timestamp,
                'previous_top_disease': prev_top_disease,
                'current_similarity': float(similarity),
                'healing_percentage': float(healing_score)
            })
        except Exception as e:
            # Skip this comparison if there's an error
            print(f"Warning: Failed to compare with entry {prev_entry.id}: {e}")
            continue
    
    average_healing_score = float(np.mean(healing_scores)) if healing_scores else 0.0
    
    return comparisons, average_healing_score
