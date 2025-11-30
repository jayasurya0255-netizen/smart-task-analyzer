from datetime import date, datetime
from typing import List, Dict, Any, Tuple

DEFAULT_WEIGHTS = {
    "urgency": 0.35,
    "importance": 0.35,
    "effort": 0.15,
    "dependencies": 0.15
}


# --------------------------
# HELPERS
# --------------------------

def days_until_due(due_date_str):
    """
    Convert ISO date string -> days until due.
    Returns negative if overdue.
    Returns None if invalid date or no date.
    """
    if not due_date_str:
        return None

    try:
        if isinstance(due_date_str, date):
            d = due_date_str
        else:
            d = date.fromisoformat(due_date_str)
    except Exception:
        return None

    today = date.today()
    return (d - today).days


def normalize(value, minv, maxv):
    """Normalizes a value to 0..1."""
    if value is None:
        return 0.0
    if minv == maxv:
        return 0.5  # avoid divide-by-zero, return neutral
    return max(0.0, min(1.0, (value - minv) / (maxv - minv)))


def detect_cycles(tasks):
    """
    Detects circular dependencies via DFS.
    Returns a set of IDs involved in cycles.
    """
    visited = {}
    cycle_nodes = set()

    def dfs(node, stack):
        if node in stack:
            cycle_nodes.update(stack[stack.index(node):])
            return

        if node in visited:
            return

        visited[node] = True
        stack.append(node)

        for dep in tasks.get(node, {}).get("dependencies", []):
            if dep in tasks:
                dfs(dep, stack)

        stack.pop()

    for tid in tasks.keys():
        if tid not in visited:
            dfs(tid, [])

    return cycle_nodes


# --------------------------
# MAIN SCORING FUNCTION
# --------------------------

def compute_scores(task_list: List[Dict[str, Any]], weights: Dict[str, float] = None, strategy: str = None) -> Tuple[List[Dict[str, Any]], Dict]:
    """
    Calculate priority scores for tasks.
    Higher score = higher priority.
    """

    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    # Strategy override (from dropdown)
    if strategy == "fastest":
        weights = {"urgency": 0.2, "importance": 0.2, "effort": 0.5, "dependencies": 0.1}
    elif strategy == "impact":
        weights = {"urgency": 0.1, "importance": 0.7, "effort": 0.1, "dependencies": 0.1}
    elif strategy == "deadline":
        weights = {"urgency": 0.7, "importance": 0.15, "effort": 0.1, "dependencies": 0.05}

    # Build ID map for circular detection
    tasks_by_id = {}
    for t in task_list:
        tid = t.get("id") or t.get("title")
        tasks_by_id[str(tid)] = t

    cycles = detect_cycles(tasks_by_id)

    # Precompute min/max values for normalization
    all_importance = []
    all_effort = []
    all_du = []
    block_counts = {str(k): 0 for k in tasks_by_id.keys()}

    # Count how many tasks depend on each task
    for tid, t in tasks_by_id.items():
        for dep in t.get("dependencies", []):
            if dep in block_counts:
                block_counts[dep] += 1

    # Collect values for normalization
    for t in task_list:
        # importance
        try:
            imp = int(t.get("importance", 5))
        except:
            imp = 5
        all_importance.append(imp)

        # estimated hours
        try:
            est = float(t.get("estimated_hours", 4.0))
            if est <= 0:
                est = 0.5
        except:
            est = 4.0
        all_effort.append(est)

        # due date
        du = days_until_due(t.get("due_date"))
        if du is None:
            du = 365  # far future
        all_du.append(du)

    min_imp, max_imp = min(all_importance), max(all_importance)
    min_est, max_est = min(all_effort), max(all_effort)
    min_du, max_du = min(all_du), max(all_du)
    max_block = max(1, max(block_counts.values()))

    results = []

    # --------------------------
    # SCORING EACH TASK
    # --------------------------
    for t in task_list:
        tid = str(t.get("id") or t.get("title"))
        title = t.get("title", "Untitled")

        # importance
        try:
            importance = int(t.get("importance", 5))
        except:
            importance = 5
        importance_norm = normalize(importance, min_imp, max_imp)

        # urgency
        du = days_until_due(t.get("due_date"))
        if du is None:
            du = max_du

        if du < 0:
            urgency = 1.0  # overdue → max urgency
        else:
            urgency = 1.0 - normalize(du, min_du, max_du)

        # effort (low effort → higher score)
        try:
            est = float(t.get("estimated_hours", 4.0))
            if est <= 0:
                est = 0.5
        except:
            est = 4.0

        effort_norm = 1.0 - normalize(est, min_est, max_est)

        # dependencies score
        block_count = block_counts.get(tid, 0)
        dependencies_score = block_count / max_block

        # total weighted score
        score = (
            weights["urgency"] * urgency +
            weights["importance"] * importance_norm +
            weights["effort"] * effort_norm +
            weights["dependencies"] * dependencies_score
        )

        explanation_parts = [
            f"Urgency: {urgency:.2f}",
            f"Importance: {importance_norm:.2f}",
            f"Effort (quick-win): {effort_norm:.2f}",
            f"Blocks other tasks: {dependencies_score:.2f}",
        ]

        if tid in cycles:
            explanation_parts.append("⚠ Circular dependency detected")

        results.append({
            "id": tid,
            "title": title,
            "raw": t,
            "score": round(score, 4),
            "urgency": round(urgency, 4),
            "importance_norm": round(importance_norm, 4),
            "effort_norm": round(effort_norm, 4),
            "explanation": "; ".join(explanation_parts),
            "in_cycle": tid in cycles,
            "errors": []
        })

    # Sort by score DESC
    results.sort(
        key=lambda x: (-x["score"], -(x["raw"].get("importance") or 0), x["raw"].get("estimated_hours") or 999)
    )

    meta = {"weights": weights, "cycles": list(cycles)}

    return results, meta
