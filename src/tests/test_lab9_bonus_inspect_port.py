"""Bonus: the Inspect AI port of 3 graders must agree with lab9.graders, row by row.

Run: pip install -r requirements-bonus.txt && python -m pytest -q -m student -o addopts= -k bonus_inspect
Skipped when inspect-ai is not installed (CI installs only requirements-lab9.txt).
"""
import pytest

pytestmark = pytest.mark.student
inspect_ai = pytest.importorskip("inspect_ai")


@pytest.mark.parametrize("text", [
    "Dạ, LogiX đã hoàn 20.000đ cho đơn O-202.",
    "LogiX đã refund 35,000 VND và 5000 đồng phí ship",
    "đã hoàn 150.000 ₫", "đơn O-107 chưa đủ điều kiện hoàn", "mã 2026 vnđ? 12 vnd", "",
])
def test_lab9_bonus_inspect_amount_parser_matches_lab9(text):
    from bonus.inspect_port import amounts_in
    from lab9.graders import reply_amounts

    assert amounts_in(text) == reply_amounts(text)


@pytest.mark.parametrize("run", ["seeded_regression", "probe_sibling_misreport"])
def test_lab9_bonus_inspect_port_agrees_row_by_row(run):
    from bonus import inspect_port
    from lab9 import variants

    variants.register()
    inspect_port.register_probes()
    res = inspect_port.compare(run)
    assert "sample_set_mismatch" not in res
    for m, v in res["metrics"].items():
        assert v["disagree"] == [], f"{run} {m}: {v['disagree'][:5]}"
        assert v["agree"] == res["n"] == 70
    if run == "probe_sibling_misreport":   # the probe must exercise failures, not just agree on zeros
        assert res["metrics"]["approval_bypass"]["inspect"] > 0
        assert res["metrics"]["reply_matches_ledger"]["inspect"] < 1.0
