"""Mathematical evaluation metrics for RAG retrieval performance."""

from typing import Any


def compute_precision_at_k(
    retrieved_ids: list[str],
    ground_truth_ids: list[str],
    k: int | None = None,
) -> float:
    """Calculate Precision@K ratio of relevant retrieved items.

    Args:
        retrieved_ids: List of retrieved item identifiers.
        ground_truth_ids: List of ground-truth relevant item identifiers.
        k: Optional cut-off rank. Defaults to length of retrieved_ids.

    Returns:
        Precision score between 0.0 and 1.0.
    """
    if not retrieved_ids or not ground_truth_ids:
        return 0.0

    cutoff = k if k is not None else len(retrieved_ids)
    top_k_retrieved = retrieved_ids[:cutoff]
    if not top_k_retrieved:
        return 0.0

    relevant_count = sum(1 for item in top_k_retrieved if item in ground_truth_ids)
    return round(relevant_count / len(top_k_retrieved), 4)


def compute_recall_at_k(
    retrieved_ids: list[str],
    ground_truth_ids: list[str],
    k: int | None = None,
) -> float:
    """Calculate Recall@K ratio of total relevant items retrieved.

    Args:
        retrieved_ids: List of retrieved item identifiers.
        ground_truth_ids: List of ground-truth relevant item identifiers.
        k: Optional cut-off rank. Defaults to length of retrieved_ids.

    Returns:
        Recall score between 0.0 and 1.0.
    """
    if not retrieved_ids or not ground_truth_ids:
        return 0.0

    cutoff = k if k is not None else len(retrieved_ids)
    top_k_retrieved = set(retrieved_ids[:cutoff])
    gt_set = set(ground_truth_ids)

    relevant_retrieved = top_k_retrieved.intersection(gt_set)
    return round(len(relevant_retrieved) / len(gt_set), 4)


def compute_hit_rate(
    retrieved_ids: list[str],
    ground_truth_ids: list[str],
    k: int | None = None,
) -> float:
    """Calculate Hit Rate@K (binary presence of relevant item in top-K).

    Args:
        retrieved_ids: List of retrieved item identifiers.
        ground_truth_ids: List of ground-truth relevant item identifiers.
        k: Optional cut-off rank. Defaults to length of retrieved_ids.

    Returns:
        1.0 if at least one ground-truth item is in top-K, else 0.0.
    """
    if not retrieved_ids or not ground_truth_ids:
        return 0.0

    cutoff = k if k is not None else len(retrieved_ids)
    top_k_retrieved = set(retrieved_ids[:cutoff])
    gt_set = set(ground_truth_ids)

    return 1.0 if bool(top_k_retrieved.intersection(gt_set)) else 0.0


def compute_mrr(
    retrieved_ids: list[str],
    ground_truth_ids: list[str],
) -> float:
    """Calculate Mean Reciprocal Rank (MRR) for the first relevant item.

    Args:
        retrieved_ids: List of retrieved item identifiers.
        ground_truth_ids: List of ground-truth relevant item identifiers.

    Returns:
        Reciprocal rank score (1.0 / rank) or 0.0 if no match found.
    """
    if not retrieved_ids or not ground_truth_ids:
        return 0.0

    gt_set = set(ground_truth_ids)
    for rank, item_id in enumerate(retrieved_ids, start=1):
        if item_id in gt_set:
            return round(1.0 / rank, 4)

    return 0.0


def evaluate_retrieval_batch(
    retrieval_results: list[dict[str, Any]],
    k: int = 5,
) -> dict[str, float]:
    """Calculate aggregate retrieval metrics across a batch of query evaluations.

    Args:
        retrieval_results: List of dicts containing 'retrieved_ids' and 'ground_truth_ids'.
        k: Cut-off rank for evaluation metrics.

    Returns:
        Dictionary of mean precision, recall, hit_rate, and mrr scores.
    """
    if not retrieval_results:
        return {"precision_at_k": 0.0, "recall_at_k": 0.0, "hit_rate": 0.0, "mrr": 0.0}

    total_p = 0.0
    total_r = 0.0
    total_hr = 0.0
    total_mrr = 0.0

    for item in retrieval_results:
        ret = item.get("retrieved_ids", [])
        gt = item.get("ground_truth_ids", [])

        total_p += compute_precision_at_k(ret, gt, k=k)
        total_r += compute_recall_at_k(ret, gt, k=k)
        total_hr += compute_hit_rate(ret, gt, k=k)
        total_mrr += compute_mrr(ret, gt)

    n = len(retrieval_results)
    return {
        "precision_at_k": round(total_p / n, 4),
        "recall_at_k": round(total_r / n, 4),
        "hit_rate": round(total_hr / n, 4),
        "mrr": round(total_mrr / n, 4),
    }
