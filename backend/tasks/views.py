from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AnalyzeRequestSerializer
from .scoring import compute_scores
import json

class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/
    """
    def post(self, request):
        data = request.data
        # Accept tasks directly (list) or { tasks: [...] }
        if isinstance(data, list):
            tasks = data
            weights = None
            strategy = None
        else:
            tasks = data.get("tasks") or []
            weights = data.get("weights")
            strategy = data.get("strategy")

        # Basic validation
        serializer = AnalyzeRequestSerializer(data={"tasks": tasks, "weights": weights or {}, "strategy": strategy or "smart"})
        if not serializer.is_valid():
            return Response({"error": "Invalid input", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        tasks = serializer.validated_data["tasks"]
        weights = serializer.validated_data.get("weights") or None
        strategy = serializer.validated_data.get("strategy") or None
        # convert 'smart' to None so compute_scores uses default
        if strategy == "smart":
            strategy = None

        results, meta = compute_scores(tasks, weights=weights, strategy=strategy)
        return Response({"tasks": results, "meta": meta})

class SuggestTasksView(APIView):
    """
    GET /api/tasks/suggest/  (or POST)
    Return top 3 suggestions with brief reasons.
    """
    def get(self, request):
        # user can pass tasks as a query param JSON encoded, or provide none
        tasks_param = request.query_params.get("tasks")
        weights_param = request.query_params.get("weights")
        strategy = request.query_params.get("strategy") or "smart"
        tasks = []
        weights = None
        if tasks_param:
            try:
                tasks = json.loads(tasks_param)
            except Exception:
                return Response({"error": "Invalid tasks param (not JSON)"}, status=400)
        else:
            # Also allow passing tasks via body (if frontend uses GET with body—rare)
            try:
                if request.data and isinstance(request.data, list):
                    tasks = request.data
            except Exception:
                tasks = []

        if weights_param:
            try:
                weights = json.loads(weights_param)
            except Exception:
                weights = None

        if not tasks:
            return Response({"error": "No tasks provided (send tasks in 'tasks' JSON param or POST body)"}, status=400)

        results, meta = compute_scores(tasks, weights=weights, strategy=(None if strategy == "smart" else strategy))
        top3 = results[:3]
        suggestions = []
        for r in top3:
            reason = []
            if r["in_cycle"]:
                reason.append("Resolve dependency cycle")
            if r["raw"].get("due_date"):
                reason.append(f"Due in {r['raw'].get('due_date')}")
            reason.append(f"Importance {r['raw'].get('importance')}")
            if r["raw"].get("estimated_hours"):
                reason.append(f"Est {r['raw'].get('estimated_hours')}h")
            suggestions.append({
                "id": r["id"],
                "title": r["title"],
                "score": r["score"],
                "why": "; ".join(reason),
            })

        return Response({"suggestions": suggestions, "meta": meta})
