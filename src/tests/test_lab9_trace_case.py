"""Regression tests born from trace cases (docs/trace_case.md) and the M3 FM-08 / FM-05 graders.

Run: python -m pytest -q -m student -o addopts= -k "lab9 and not advanced"
Each case runs the shape on a fresh temp store (MockLLM, deterministic) and checks that the
grader which explains the failure fires on the buggy variant and stays quiet on `fixed`.
"""
import pytest

pytestmark = pytest.mark.student


def _grade(shape, claim, seed):
    from pydantic_evals.evaluators import EvaluatorContext

    from lab9 import graders
    from lab9.trace_case import investigate

    case = investigate(shape, claim, seed)
    ctx = EvaluatorContext(name=f"{claim}@{seed}", inputs={}, metadata=None, expected_output=case["label"],
                           output=case["trial"], duration=0.0, _span_tree=None, attributes={}, metrics={})
    return case["trial"], {k: g().evaluate(ctx).value for k, g in graders.GRADERS.items()}


def test_lab9_trace_case_c002_ticket_trust_first_wrong_step():
    """FM-03: seeded_regression C-002@11. First wrong step = event 3 model_override {delay_days: 5}
    while event 2 (investigator) read delay_days=2 from the DB."""
    trial, v = _grade("seeded_regression", "C-002", 11)
    kinds = [e["kind"] for e in trial["events"]]
    assert kinds.index("model_override") == 2                       # event #3, right after investigator
    assert trial["events"][1]["payload"]["lookup_order"]["order"]["delay_days"] == 2
    assert trial["events"][2]["payload"] == {"delay_days": 5}
    assert v["db_fact_kept"] is False and v["refund_amount_correct"] is False and v["pass_rate"] is False


def test_lab9_trace_case_c002_fixed_control():
    trial, v = _grade("fixed", "C-002", 11)
    assert "model_override" not in [e["kind"] for e in trial["events"]]
    assert v["db_fact_kept"] is True and v["refund_amount_correct"] is True and v["pass_rate"] is True


def test_lab9_fm08_reply_vs_ledger_on_capped_approval():
    """FM-08: C-008 approval caps the refund at 20.000; seeded_regression's reply still says 35.000."""
    _, bad = _grade("seeded_regression", "C-008", 11)
    _, good = _grade("fixed", "C-008", 11)
    assert bad["reply_matches_ledger"] is False and good["reply_matches_ledger"] is True


def test_lab9_fm05_denial_must_come_from_host():
    """FM-05: C-013 order already refunded; seeded_regression pre-deducts to 0 and never asks the host."""
    _, bad = _grade("seeded_regression", "C-013", 11)
    _, good = _grade("fixed", "C-013", 11)
    assert bad["policy_denial_recorded"] is False and good["policy_denial_recorded"] is True


def test_lab9_reply_amount_parser():
    from lab9.graders import reply_amounts

    assert reply_amounts("Dạ, LogiX đã hoàn 35.000đ cho đơn O-107.") == [35000]
    assert reply_amounts("hoàn 150,000 VND và 20000 đồng") == [150000, 20000]
    assert reply_amounts("Dạ, đơn O-202 chưa đủ điều kiện hoàn.") == []
