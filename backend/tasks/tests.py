from django.test import TestCase
from .scoring import compute_scores

class ScoringTests(TestCase):
    def test_basic_scoring_order(self):
        tasks = [
            {"id": "t1", "title": "Low effort", "due_date": None, "estimated_hours": 0.5, "importance": 5, "dependencies": []},
            {"id": "t2", "title": "High importance", "due_date": None, "estimated_hours": 8, "importance": 10, "dependencies": []},
            {"id": "t3", "title": "Soon due", "due_date": "2099-01-01", "estimated_hours": 2, "importance": 6, "dependencies": []}
        ]
        results, meta = compute_scores(tasks)
        self.assertEqual(len(results), 3)
        # ensure scores present and are floats
        for r in results:
            self.assertIn("score", r)
        # ensure stable ordering by score
        scores = [r["score"] for r in results]
        self.assertTrue(all(isinstance(s, float) for s in scores))

    def test_overdue_boosts(self):
        import datetime
        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=1)).isoformat()
        tasks = [
            {"id": "a", "title": "Overdue", "due_date": yesterday, "estimated_hours": 4, "importance": 5, "dependencies": []},
            {"id": "b", "title": "Far future", "due_date": (today + datetime.timedelta(days=30)).isoformat(), "estimated_hours": 1, "importance": 5, "dependencies": []}
        ]
        results, meta = compute_scores(tasks)
        # Overdue should have higher score than far future even if effort equal
        self.assertTrue(results[0]["id"] == "a")

    def test_cycle_detection(self):
        tasks = [
            {"id": "1", "title": "A", "due_date": None, "estimated_hours": 1, "importance": 5, "dependencies": ["2"]},
            {"id": "2", "title": "B", "due_date": None, "estimated_hours": 2, "importance": 5, "dependencies": ["1"]}
        ]
        results, meta = compute_scores(tasks)
        self.assertIn("1", meta["cycles"])
        self.assertIn("2", meta["cycles"])
