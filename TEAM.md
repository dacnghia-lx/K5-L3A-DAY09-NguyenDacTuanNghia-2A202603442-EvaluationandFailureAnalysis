# Team

## Thông tin nhóm

- Tên nhóm: MHT
- Lớp: L3A
- Repo nhóm: `K5-L3A-Day8-MHT-FromWorkflowsToAgents`
- URL repo: https://github.com/VOX304/K5-L3A-Day8-MHT-FromWorkflowsToAgents
- Lab 9 (cá nhân): https://github.com/dacnghia-lx/K5-L3A-DAY09-NguyenDacTuanNghia-2A202603442-EvaluationandFailureAnalysis · nhánh nộp `starter/d09` → PR vào `main` · commit chốt: commit cuối trên PR trước hạn

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Nguyễn Đắc Tuấn Nghĩa | 2A202603442 | orange25k5@gmail.com | https://github.com/dacnghia-lx | Orchestrator + handoff |
| 2 | Vũ Mạnh Hoạch | 2A202603500 | 26ai.hoachvm@vinuni.edu.vn | https://github.com/vumanhhoach2003 | Workflow + integration |
| 3 | Nguyễn Văn Tùng | 2A202603471 | nguyenvantung011204@gmail.com | https://github.com/Nguyenvantung04 | Single |
| 4 | Võ Công Minh | 2A202503520 | congminhvox@gmail.com | https://github.com/vox304 | Ledger + evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Đắc Tuấn Nghĩa | Orchestrator + handoff | d33bd49 | src/tests/test_orchestrator_shape.py (20 ca) |
| Vũ Mạnh Hoạch | Workflow + integration | 07dba1e | src/tests/test_workflow_shape.py |
| Nguyễn Văn Tùng | Single agent | ddb1169 | src/tests/test_single_agent.py |
| Võ Công Minh | Ledger + evaluation (có trợ lý AI hỗ trợ thực thi; không nhận tác giả code shape của thành viên khác) | e27e680 | src/tests/test_evaluation_safety.py (33 ca), src/tests/test_evaluation_ablation.py (9 ca) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603442_NguyenDacTuanNghia

### Phần việc phụ trách

- Orchestrator (Shape C) tại `src/lab8/shapes/orchestrator.py` và ranh giới handoff giữa orchestrator với investigator.

### Đóng góp cụ thể

- Orchestrator đọc claim, dựng handoff bằng `make_handoff` (8 field allowlist, `facts` rỗng, 3 tool chỉ đọc: `lookup_order`, `lookup_refund_history`, `compute_compensation`), là bên duy nhất gọi `durability.issue_refund` với quote đầy đủ.
- Investigator không nhận `parent_secret`, `raw_headers`, ticket, `approval_id` hay claim row; gọi tool ghi thì bị `ToolRejected`. Trace chỉ ghi handoff đã sanitize.
- Tiền do code tính từ order row, không tin số ngày trễ trong ticket (C-002 `denied` ở cả 5 seed, khác swarm ở seed 55).
- Truyền `crash_at` vào host, không nuốt `InjectedCrash`; lỗi bất ngờ khác trả `failed` để `run_claim` không ném exception.
- Viết bộ kiểm thử `src/tests/test_orchestrator_shape.py` (20 ca).
- Gộp bốn nhánh vào `main`, xử lý conflict `TEAM.md` và `orchestrator.py`; điền `decision_adr.md` và viết `group_report.md`.

### Bằng chứng

- Commit `d33bd49` (orchestrator + test), `9e19a19` (báo cáo cá nhân), `8591ea1` (ADR + báo cáo nhóm).
- Báo cáo chi tiết: `report/team/2A202603442_NguyenDacTuanNghia.md`.
- Test passed: 62/62 test case `orchestrator` trong `test_public_matrix.py` và 20/20 trong `src/tests/test_orchestrator_shape.py`. Benchmark: pass rate 1.000, pass^5 1.000, cost/success 47.85 VND mô phỏng (`src/reports/benchmark.json`). Run id mẫu: `R-orchestrator-C-001-s11`.

## 2A202603500_VuManhHoach

### Phần việc phụ trách

- Workflow (Shape A) tại `src/lab8/shapes/workflow.py` và integration: chạy kiểm thử tích hợp sau khi ghép các shape.

### Đóng góp cụ thể

- Triển khai luồng Python cố định, không gọi model: `get_claim_view` → `lookup_order` → `compute_compensation` từ order row → `lookup_refund_history` (chỉ ghi trace) → `durability.issue_refund` với quote đầy đủ.
- Ghi trace xuống đĩa trước khi gọi host để trace vẫn hợp lệ khi crash; không ghi claim row, ticket hay order row thô.
- Chạy kiểm thử tích hợp: host test, toàn bộ student test, retry C-001 trên cùng database, crash suite và benchmark 4 shape.
- Đề xuất chọn workflow vì cùng độ đúng với single/orchestrator nhưng chi phí thấp nhất và ít tự chủ nhất.
- Bộ kiểm thử `src/tests/test_workflow_shape.py` (37 ca, có trợ lý AI hỗ trợ viết): workflow không gọi model, kết quả không đổi theo seed, crash ở 3 điểm vẫn một refund, truyền quote đầy đủ ở T14, không tin số ngày trễ trong ticket, trace không lộ secret/PII.

### Bằng chứng

- Commit `07dba1e` (`feat: workflow + integration`).
- Báo cáo chi tiết: `report/team/2A202603500_VuManhHoach.md`.
- Test passed: 62/62 test case `workflow` trong `test_public_matrix.py` và 37/37 trong `src/tests/test_workflow_shape.py`. Benchmark: pass rate 1.000, pass^5 1.000, variance 0, cost/success 34.29 VND mô phỏng, 0 model call. Run id mẫu: `R-workflow-C-001-s11`.

## 2A202603471_NguyenVanTung

### Phần việc phụ trách

- Single agent (Shape B - ReAct loop) tại `src/lab8/shapes/single.py`.

### Đóng góp cụ thể

- Triển khai ReAct loop với max 8 steps, sandbox `worker=True` chỉ cho phép công cụ đọc.
- Cơ chế không tin dữ liệu ticket của khách, luôn tra cứu DB đơn hàng để tính bồi thường thực tế.
- Tách quyền ghi duy nhất cho Host và xử lý an toàn crash injection.
- Viết bộ kiểm thử `src/tests/test_single_agent.py`.

### Bằng chứng

- Commit `ddb1169`.
- Báo cáo chi tiết: `report/team/2A202603471_NguyenVanTung.md`.
- Test passed: `src/tests/test_single_agent.py` và 62/62 test case `single` trong `test_public_matrix.py`.

## 2A202503520_VoCongMinh

### Phần việc phụ trách

- Ledger + evaluation (CP4–CP5): kiểm chứng an toàn ghi hoàn tiền, tạo bằng chứng crash và benchmark, thực hiện ablation một biến. Phần host ledger/policy/durability là code có sẵn của lab.

### Đóng góp cụ thể

- Viết `src/tests/test_evaluation_safety.py` (33 ca end-to-end): approval không hợp lệ, ba cửa sổ crash × ba shape, hai claim cùng một đơn, xung đột hạn mức khi retry, không lộ thông tin qua stdout/artifact.
- Viết `src/tests/test_evaluation_ablation.py` (9 ca) và biến thể `src/bonus/orchestrator_no_history.py` cho ablation bỏ bước đọc history ở investigator.
- Sinh bằng chứng máy: crash 20/20, benchmark 280 trial, ablation 140 trial, JUnit 364 test; không sửa tay JSON.
- Hoàn thiện research card R1 và `docs/cp4-cp5-evaluation.md`.

### Bằng chứng

- Commit `e27e680` (tích hợp shape, test evaluation, ablation), `b6177ca` (bằng chứng CP4–CP5 và báo cáo cá nhân).
- Báo cáo chi tiết: `report/team/2A202503520_VoCongMinh.md`.
- Report: `src/reports/crash.json` (20/20), `src/reports/benchmark.json`, `src/reports/ablation_history.json`, `src/reports/evaluation_tests.xml` (364 passed). Ablation: cost/success orchestrator giảm từ 47.85 xuống 38.57 VND mô phỏng, pass rate giữ 1.000.
