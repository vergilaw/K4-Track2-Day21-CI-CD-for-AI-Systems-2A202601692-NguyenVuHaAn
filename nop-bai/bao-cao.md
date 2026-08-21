# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Nguyễn Vũ Hà An |
| MSSV | 2A202601692 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/vergilaw/K4-Track2-Day21-CI-CD-for-AI-Systems-2A202601692-NguyenVuHaAn |
| Ngày nộp | 21/08/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.672 | 0.865 |
| 2 | 50 | 0.05 | 2 | 0.590 | 0.840 |
| 3 | 200 | 0.1 | 5 | 0.691 | 0.871 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Bộ siêu tham số này đạt điểm f1_score cao nhất (0.691) so với các bộ còn lại. Mặc dù lần chạy này cũng có accuracy cao nhất, nhưng sự chênh lệch f1_score giữa lần chạy 2 và 3 là rất lớn (0.590 vs 0.691) trong khi accuracy gần như không đổi (0.840 vs 0.871). Điều này cho thấy f1_score nhạy cảm và phản ánh đúng chất lượng học của mô hình hơn. Tôi cũng nhận thấy sự đánh đổi: tăng n_estimators và max_depth giúp mô hình học các mẫu phức tạp hơn, nhưng đánh đổi bằng thời gian huấn luyện lâu hơn và nguy cơ overfit nếu learning_rate quá cao.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Adult Income có sự mất cân bằng lớp đáng kể, với tỷ lệ lớp "thu nhập <= 50K" chiếm đến 75% và lớp "thu nhập > 50K" chỉ chiếm 25%. Do đó, nếu một mô hình cực kỳ tệ chỉ luôn đoán bừa là "thu nhập thấp" cho mọi mẫu, nó vẫn sẽ đạt độ chính xác (accuracy) là 75%. Con số này gây hiểu lầm nghiêm trọng về chất lượng thực sự của mô hình. 

Thay vào đó, f1_score (cho lớp dương) đo lường sự cân bằng giữa độ chuẩn xác (Precision) và độ bao phủ (Recall), bắt buộc mô hình phải thực sự dự đoán đúng người có thu nhập cao thì điểm mới tăng. Việc KHÔNG dùng `average="weighted"` là để ngăn lớp đa số (thu nhập thấp) kéo điểm số lên, giúp hệ thống CI/CD đánh giá khắt khe và chính xác năng lực phát hiện thu nhập cao của mô hình.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Lệnh curl kiểm tra API trên máy ảo EC2 bị treo mãi không trả kết quả | AWS mặc định chặn tất cả các cổng từ bên ngoài, chỉ mở port 22 | Vào AWS Console, thiết lập Security Group Inbound Rule mở port 8080 cho `0.0.0.0/0` |
| Quá trình CI/CD báo lỗi parse biến STORAGE_CREDENTIALS | Định dạng file credentials của AWS xuất ra đôi khi chứa ký tự rác (BOM) hoặc thiếu khoảng trắng hợp lệ | Nâng cấp script Python dùng `json.loads` an toàn và `csv.DictReader` loại bỏ BOM-UTF8 |
| Lệnh `dvc push` bị AccessDenied trên GitHub Actions | Chưa cấp quyền ghi (PutObject) cho IAM User hoặc chưa có quyền ListBucket | Thêm quyền `s3:ListBucket` vào chính sách IAM để DVC kiểm tra file tồn tại |

---

## 4. So Sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.691 | 0.871 |
| Bước 3 (thêm `train_batch2`) | 0.687 | 0.869 |

**Nhận xét:** f1_score giảm nhẹ đi khoảng 0.004 khi thêm batch 2 vào tập huấn luyện. Điều này hợp lý và phản ánh đúng bản chất vì dữ liệu batch 2 được cắt từ cùng một tập gốc (cùng phân phối) so với batch 1, nên việc thêm dữ liệu chỉ đơn thuần tăng số lượng mẫu chứ không mang lại thông tin hay dạng phân phối mới, đôi khi còn thêm nhiễu khiến điểm số giảm nhẹ. Thêm dữ liệu không phải lúc nào cũng làm mô hình tốt lên.

---

## 5. Phần Bonus Đã Thực Hiện

- [x] Bonus 1 - Tracking MLflow từ xa với DagsHub: Đã khai báo 3 biến môi trường để gửi lịch sử huấn luyện từ Actions sang DagsHub (ảnh 06).
- [x] Bonus 3 - Báo cáo precision / recall tự động: Ghi thêm classification_report và confusion_matrix ra file detail.txt để CI lưu artifact.
- [x] Bonus 5 - Cảnh báo lệch lạc dữ liệu: Đã thêm logic kiểm tra độ lệch phân phối trung bình đặc trưng Age (tuổi) giữa tập Train và Eval.
- [x] Thêm: Đã tạo nhánh phụ cố tình dùng tham số kém để chứng minh Quality Gate chặn Release thành công (ảnh 07).
