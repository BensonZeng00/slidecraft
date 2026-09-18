"""Synthetic state tests, not provider or human-approval integration tests."""

import copy
import json
from pathlib import Path
import unittest
from validate_state import generation_errors, production_errors, validate
from outline_state import outline_fingerprint


class StateTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads((Path(__file__).parents[1] / "assets" /
                                 "project-state.example.json").read_text(encoding="utf-8"))
        self.sid = self.state["slides"][0]["id"]

    def ready(self, status="awaiting-review"):
        slide = self.state["slides"][0]
        slide.update(status=status, artifacts={"pptx": "out/page.pptx", "preview": "out/page.png"},
                     checks={"native": True, "render": True})
        return slide

    def deck(self):
        second = copy.deepcopy(self.state["slides"][0])
        second["id"] = "page-two"
        self.state.update(mode="multi", total_slides=2)
        self.state["slides"].append(second)
        self.state["outline"] = {"revision":1, "status":"awaiting-review", "approval":None,
                                 "pages":[{"id":s["id"], "title":s["title"], "key_points":["SYNTHETIC content"]}
                                          for s in self.state["slides"]]}
        self.approve_outline()

    def approve_outline(self):
        outline = self.state["outline"]
        outline["status"] = "approved"
        outline["approval"] = {"revision":outline["revision"], "evidence":"SYNTHETIC",
                               "user_text":"SYNTHETIC outline approval",
                               "content_sha256":outline_fingerprint(outline)}

    def attempt(self, outcome="failed", usable=False):
        records = self.state["generation"]["attempts"]
        records.append({"id": f"request-{len(records)}", "slide_id": self.sid,
                        "outcome": outcome, "usable": usable})

    def test_template(self):
        self.assertEqual(validate(self.state), [])
        self.assertEqual(generation_errors(self.state, self.sid), [])

    def test_next_page_rejected(self):
        self.deck()
        self.ready()
        self.assertTrue(generation_errors(self.state, "page-two"))

    def test_current_review_no_generation(self):
        self.ready()
        self.assertTrue(generation_errors(self.state, self.sid))

    def test_revision_requires_new_approval(self):
        slide = self.ready("approved")
        slide["approval"] = {"revision": 1, "evidence": "SYNTHETIC", "user_text": "SYNTHETIC approval"}
        self.assertEqual(validate(self.state), [])
        slide["revision"] = 2
        self.assertTrue(validate(self.state))

    def test_approved_page_unlocks_next(self):
        self.deck()
        slide = self.ready("approved")
        slide["approval"] = {"revision": 1, "evidence": "SYNTHETIC", "user_text": "SYNTHETIC approval"}
        self.assertEqual(generation_errors(self.state, "page-two"), [])

    def test_resume_does_not_approve(self):
        self.deck()
        self.ready()
        restored = json.loads(json.dumps(self.state))
        self.assertTrue(generation_errors(restored, "page-two"))

    def test_revision_clears_approval(self):
        slide = self.ready("needs-revision")
        slide["approval"] = {"revision": 1}
        self.assertTrue(validate(self.state))
        slide["approval"] = None
        self.assertEqual(validate(self.state), [])

    def test_budget_exhausted(self):
        for _ in range(3):
            self.attempt()
        self.assertTrue(generation_errors(self.state, self.sid))
        self.attempt()
        self.assertTrue(validate(self.state))

    def test_project_cap(self):
        self.state["generation"]["max_calls_total"] = 1
        self.attempt()
        self.assertTrue(generation_errors(self.state, self.sid))

    def test_pending_job(self):
        self.attempt("unknown")
        self.assertTrue(generation_errors(self.state, self.sid))

    def test_usable_result_stops_retry(self):
        self.attempt("succeeded", True)
        self.assertTrue(generation_errors(self.state, self.sid))

    def test_paths(self):
        for value in ("../secret", "C:/secret", "https://secret", "/secret", "\\\\server\\file"):
            self.state["slides"][0]["artifacts"] = {"pptx": value}
            self.assertTrue(validate(self.state))

    def test_count_and_duplicate_ids(self):
        self.deck()
        self.state["slides"][1]["id"] = self.sid
        self.assertTrue(validate(self.state))
        self.state["total_slides"] = 3
        self.assertTrue(validate(self.state))

    def test_unverified_cannot_be_review_ready(self):
        self.ready()["checks"]["render"] = False
        self.assertTrue(validate(self.state))

    def test_early_later_production(self):
        self.deck()
        self.state["slides"][1]["status"] = "reference-ready"
        self.assertTrue(validate(self.state))

    def test_malformed(self):
        for value in (None, {}, {"slides": [None]}, {"slides": "wrong"}):
            self.assertTrue(validate(value))

    def test_future_attempt_rejected_even_when_status_planned(self):
        self.deck()
        self.state["generation"]["attempts"] = [{"id":"request-future", "slide_id":"page-two", "outcome":"failed"}]
        self.assertTrue(validate(self.state))

    def test_zero_budget(self):
        self.state["generation"].update(max_calls_total=0, max_calls_per_slide=0, planned_images=0)
        self.assertEqual(validate(self.state), [])
        self.assertTrue(generation_errors(self.state,self.sid))

    def test_typed_invalid_status(self):
        self.state["slides"][0]["status"] = []
        self.assertTrue(validate(self.state))

    def test_outline_gate_before_first_page(self):
        self.deck()
        self.state["outline"].update(status="awaiting-review", approval=None)
        self.assertEqual(validate(self.state), [])
        self.assertTrue(generation_errors(self.state,self.sid))
        self.assertTrue(production_errors(self.state,self.sid))

    def test_outline_approval_unlocks_only_first_page(self):
        self.deck()
        self.assertEqual(generation_errors(self.state,self.sid), [])
        self.assertTrue(generation_errors(self.state,"page-two"))

    def test_outline_content_change_invalidates_approval(self):
        self.deck()
        self.state["outline"]["pages"][0]["key_points"] = ["Changed content"]
        self.assertTrue(production_errors(self.state,self.sid))

    def test_outline_revision_invalidates_approval(self):
        self.deck()
        self.state["outline"]["revision"] = 2
        self.assertTrue(production_errors(self.state,self.sid))

    def test_outline_requires_per_page_content(self):
        self.deck()
        self.state["outline"]["pages"][0]["key_points"] = []
        self.approve_outline()
        self.assertTrue(validate(self.state))

    def test_outline_order_must_match(self):
        self.deck()
        self.state["outline"]["pages"].reverse()
        self.approve_outline()
        self.assertTrue(validate(self.state))

    def test_legacy_deck_not_auto_approved(self):
        self.deck()
        del self.state["outline"]
        self.assertTrue(production_errors(self.state,self.sid))

    def test_resume_keeps_outline_waiting(self):
        self.deck()
        self.state["outline"].update(status="awaiting-review",approval=None)
        restored = json.loads(json.dumps(self.state))
        self.assertTrue(production_errors(restored,self.sid))


if __name__ == "__main__":
    unittest.main()
