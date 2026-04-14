"""
Fuzzy Match Module
==================
Provides fuzzy string matching utilities using the rapidfuzz library.
Used by product_matcher.py to find approximate matches for ingredient names.
"""

from rapidfuzz import fuzz, process


def find_best_match(query, candidates, threshold=65, limit=3):
    """
    Find the best fuzzy matches for a query string against a list of candidates.
    
    Args:
        query: The search string (e.g. "onoin" — a typo for "onion").
        candidates: List of strings to match against (e.g. product names).
        threshold: Minimum similarity score (0-100) to include a result.
        limit: Maximum number of results to return.
    
    Returns:
        List of dicts: [{ "match": str, "score": float, "index": int }]
        Sorted by score descending.
    """
    if not query or not candidates:
        return []

    # Use token_sort_ratio for better matching of reordered words
    # e.g. "red bell pepper" should match "bell pepper red"
    results = process.extract(
        query,
        candidates,
        scorer=fuzz.token_sort_ratio,
        limit=limit,
        score_cutoff=threshold,
    )

    matches = []
    for match_text, score, index in results:
        matches.append({
            "match": match_text,
            "score": round(score, 1),
            "index": index,
        })

    return matches


def is_close_match(string1, string2, threshold=80):
    """
    Check if two strings are a close match.
    
    Args:
        string1: First string.
        string2: Second string.
        threshold: Minimum similarity score to consider a match.
    
    Returns:
        bool: True if the strings are similar enough.
    """
    score = fuzz.token_sort_ratio(string1.lower(), string2.lower())
    return score >= threshold


def find_best_partial_match(query, candidates, threshold=70, limit=3):
    """
    Find matches using partial ratio — useful when the query is a substring
    of the candidate (e.g. "chicken" should match "boneless chicken breast").
    
    Args:
        query: The search string.
        candidates: List of strings to match against.
        threshold: Minimum similarity score.
        limit: Maximum number of results.
    
    Returns:
        List of dicts: [{ "match": str, "score": float, "index": int }]
    """
    if not query or not candidates:
        return []

    results = process.extract(
        query,
        candidates,
        scorer=fuzz.partial_ratio,
        limit=limit,
        score_cutoff=threshold,
    )

    matches = []
    for match_text, score, index in results:
        matches.append({
            "match": match_text,
            "score": round(score, 1),
            "index": index,
        })

    return matches


def combined_fuzzy_search(query, candidates, threshold=60, limit=3):
    """
    Combined search using multiple fuzzy matching strategies.
    Uses a weighted combination of token_sort_ratio and partial_ratio
    for the most accurate results.
    
    Args:
        query: The search string.
        candidates: List of strings to match against.
        threshold: Minimum combined score.
        limit: Maximum number of results.
    
    Returns:
        List of dicts: [{ "match": str, "score": float, "index": int }]
    """
    if not query or not candidates:
        return []

    # Score each candidate with multiple strategies
    scored = []
    for i, candidate in enumerate(candidates):
        token_score = fuzz.token_sort_ratio(query.lower(), candidate.lower())
        partial_score = fuzz.partial_ratio(query.lower(), candidate.lower())
        # Weighted average: 60% token_sort + 40% partial
        combined = (token_score * 0.6) + (partial_score * 0.4)

        if combined >= threshold:
            scored.append({
                "match": candidate,
                "score": round(combined, 1),
                "index": i,
            })

    # Sort by score descending and limit results
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]
