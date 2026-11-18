# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5` (judge replay, n = 100 mỗi tiêu chí, FAIL = lớp dương).

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | **PASS** | dùng (chỉ cho tone, không cho tiền) |
| helpful | 100 | 0.375 | 1.000 | 0.300 | **FAIL** (κ, R) | loại |

Ma trận nhầm lẫn:
- tone_ok: `{tp: 24, fp: 4, fn: 6, tn: 66}`. Tỉ lệ FAIL quan sát 0.28, sau Rogan-Gladen (sens 0.8, spec 66/70) là 0.30.
- helpful: `{tp: 9, fp: 0, fn: 21, tn: 70}`. Tỉ lệ FAIL quan sát 0.09, sau Rogan-Gladen là 0.30: judge đếm thiếu lỗi tới hơn 3 lần.

## ≥5 case audit thủ công

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | tone H-008 "Em đã hoàn tiền cho anh rồi nha…" | PASS | FAIL | Người | Xưng "em/anh" + "nha" quá suồng sã. Rubric thêm: *xưng hô phải là "LogiX" / "anh/chị"; không dùng "em", "bạn", tiểu từ "nha/nhé"*. |
| 2 | tone H-029 "Dạ, vui lòng chờ… không cần nhắn thêm." | PASS | FAIL | Người | Judge bị đánh lừa bởi "Dạ, vui lòng". Rubric thêm: *câu mệnh lệnh / chặn khách liên hệ là FAIL dù có kính ngữ*. |
| 3 | tone H-051 "LogiX đã refund 90.000đ…" | FAIL | PASS | Người | CS LogiX cho phép từ "refund". Rubric thêm danh sách từ tiếng Anh được phép (refund, ship, voucher) để judge không phạt. |
| 4 | tone H-081 "đơn O-107 chưa đủ điều kiện hoàn…" | FAIL | PASS | **Judge** | Người đọc nhầm ticket. Hành động: sửa nhãn người trong tập calibration (ghi người sửa vào cột `note`), chạy lại calibration. |
| 5 | tone H-063 "đã hoàn 20.000đ và sẽ hoàn thêm…" | PASS | FAIL | Người | Hứa hẹn ngoài kết quả hệ thống. Đây không phải lỗi tone mà là lỗi nội dung → chuyển sang grader code `ReplyMatchesLedger` (FM-08) / rubric "không hứa ngoài ledger". |
| 6 | tone H-070 "…ạ 😂😂" | PASS | FAIL | Người | Rubric thêm: *emoji cười trong phản hồi khiếu nại = FAIL*. |
| 7 | tone H-094 "Da, LogiX da hoan…" (mất dấu) | PASS | FAIL | Người | Rubric thêm: *thiếu dấu tiếng Việt / dịch máy = FAIL*. |
| 8 | helpful HL-015 "đã hoàn 55.000đ" (ledger 40.000đ) | PASS | FAIL | Người | Judge không thấy ledger nên không thể biết số sai. Số tiền phải chấm bằng code (`ReplyMatchesLedger`), không bằng judge. |
| 9 | helpful HL-047 "Ok bạn, đơn O-515 xử lý rồi nhé." | PASS | FAIL | Người | Không nói kết quả, không nói số tiền. Rubric helpful cần tiêu chí cụ thể: *phải nêu trạng thái + số tiền (nếu resolved) + bước tiếp theo*. |
| 10 | helpful HL-016 (xin lỗi dài, số sai) | PASS | FAIL | Người | Judge thưởng cho lời xin lỗi dài (verbosity bias) trong khi số tiền sai. |

## Kết luận
- **tone_ok dùng được**: κ 0.757 / P 0.857 / R 0.800 đều qua sàn. 6 FN là lỗi xưng hô / emoji / mất dấu, sửa được bằng rubric ở trên. Chỉ dùng để theo dõi tone, không làm gate tiền.
- **helpful bị loại**: R = 0.30 (21 FN / 30 FAIL thật), κ = 0.375 < 0.6. Precision 1.0 chỉ chứng minh judge "hiếm khi nói FAIL". Nó bỏ lọt 70% reply sai, phần lớn là **sai số tiền so với ledger** (HL-015, 020, 043, 053…) và reply rỗng nội dung. Một gate dựa trên judge này sẽ cho qua đúng loại lỗi đắt nhất. Thay bằng grader code `reply_matches_ledger` (FM-08).
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật. Sau khi sửa rubric phải calibrate lại trên tập mới, không dùng lại 100 dòng này (đã bị "nhìn thấy").
