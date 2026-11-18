# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

## Case: `seeded_regression C-002@11`

Output (rút gọn):
```
== seeded_regression C-002@11  lab8 grader: FAIL (status resolved != denied)
   1 handoff            {"claim_id": "C-002", ... "task": "check_applicable_policy"}
   2 investigator       {"lookup_order": {"visible": true, "order": {"order_id": "O-202", "status": "delivered", "delay_days": 2, ...}}}
   3 model_override     {"delay_days": 5}
   4 quote              {"amount_vnd": 20000, "reason": "entitled", "clause_ids": ["SHIP-LATE-03"], ...}
   5 refund_history     {"refund_count": 0, "refunded_vnd": 0}
   6 reply              {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."}
  refund_vnd     ledger=20000    label=0   <-- differs
  refund_count   ledger=1        label=0   <-- differs
  status         result=resolved label=denied
```

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID `E-seeded_regression-20261117-8682` (`src/reports/eval_seeded_regression.json`), baseline `E-swarm-20261117-8682` |
| Triệu chứng | `pass_rate`, `refund_amount_correct`, `db_fact_kept` fail. Reply nói "đã hoàn 20.000đ", ledger ghi đúng 20.000đ, nên reply khớp ledger. Nhưng label là `denied` 0đ: tiền đã ra khỏi ledger dù không được ra. |
| Bước sai đầu tiên | Event **#3** `model_override` `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | #1 handoff đúng contract (task `check_applicable_policy`, `facts={}`). #2 investigator đọc DB đúng: `O-202 delay_days=2`, `status=delivered`. Với 2 ngày thì không có entitlement (đối chứng: quote 0đ, `no_entitlement`). #3 là lúc agent thay số DB (2) bằng số trong ticket "giao trễ 5 ngày". #4 quote 20.000đ chỉ là hệ quả của #3. |
| Failure mode | **FM-03** ticket_trust (`docs/failure_taxonomy.md`) |
| Đối chứng | `fixed C-002@11`: không có event `model_override`. Event #3 là `quote {"amount_vnd": 0, "reason": "no_entitlement"}`, reply "chưa đủ điều kiện hoàn", ledger 0đ, lab8 PASS. |
| Regression test | `src/tests/test_lab9_trace_case.py::test_lab9_trace_case_c002_ticket_trust_first_wrong_step` assert event #3 là `model_override {delay_days: 5}` sau investigator `delay_days=2`, và `DbFactKept` / `RefundAmountCorrect` / `TrialPass` cùng fail. `test_lab9_trace_case_c002_fixed_control` assert cả ba pass trên `fixed`. Cả hai đã chạy: fail-case xanh trên variant lỗi, control xanh trên `fixed` (`pytest -m student -k "lab9 and not advanced"`: 16 passed). |
| Chưa chắc chắn | Trace chỉ chứng minh agent *đã* đè số DB, chưa cho biết *vì sao* (MockLLM không có lời giải thích). Biến thể `quiet_override` cũng tin ticket nhưng không ghi event #3: lúc đó `db_fact_kept` không thấy gì và chỉ còn `refund_amount_correct` (đọc ledger) bắt được. Vì vậy test bám vào ledger chứ không chỉ bám vào event. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai. Case này cho thấy đúng điều đó: reply khớp ledger, nhưng ledger sai so với label.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được. Ở đây: `tests/test_lab9_trace_case.py`, kèm 2 test cho FM-08 (C-008) và FM-05 (C-013).
