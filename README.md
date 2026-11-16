# BÀI TẬP LỚN MÔN XỬ LÝ ẢNH (DIGITAL IMAGE PROCESSING)
## ĐỀ TÀI 5: KHẢO SÁT CÁC PHÉP BIẾN ĐỔI ÂM BẢN, LOGARIT VÀ GAMMA

**Yêu cầu đề tài:** Cài đặt ba phép biến đổi; phân tích ảnh hưởng của tham số qua histogram; kết hợp phát hiện biên Sobel để so sánh mức độ bảo toàn chi tiết sau biến đổi.

---

## 📌 1. Giới thiệu Đề tài
Dự án tập trung nghiên cứu, cài đặt và đánh giá toàn diện:
1. **Ba phép biến đổi không gian mức xám kinh điển**:
   - Biến đổi Âm bản (Image Negative): $s = 255 - r$
   - Biến đổi Logarit (Logarithmic Transformation): $s = c \cdot \ln(1 + r)$
   - Biến đổi Gamma / Lũy thừa (Power-Law / Gamma Transformation): $s = c \cdot (r/255)^\gamma \cdot 255$
2. **Phân tích biến thiên qua Histogram**:
   - Khảo sát sự dịch chuyển, co dãn và phân bố mật độ mức xám khi thay đổi các hệ số $c$ và đặc biệt là dải tham số $\gamma \in [0.05, 5.0]$.
3. **Đánh giá mức độ bảo toàn chi tiết bằng toán tử Sobel**:
   - Tính toán ma trận Gradient $G_x, G_y$, độ lớn Gradient $G = \sqrt{G_x^2 + G_y^2}$.
   - Đo lường định lượng qua các chỉ số:
     - **Mean Gradient Magnitude**: Cường độ biên trung bình.
     - **Tenengrad Focus Measure** ($\sum G_x^2 + G_y^2$): Năng lượng chi tiết biên.
     - **Mật độ điểm biên nhị phân Otsu (%)**: Tỉ lệ phần trăm chi tiết biên phân tách được.
     - **Độ tương phản toàn cục (Standard Deviation $\sigma$)**.

---

## 📂 2. Cấu trúc thư mục dự án
```text
C:\BTL_XLA\
├── sample_images/              # Bộ ảnh mẫu kiểm thử chuẩn
│   ├── dark_scene.png          # Ảnh thiếu sáng / chụp ban đêm (kiểm chứng Gamma < 1 và Log)
│   ├── overexposed.png         # Ảnh cháy sáng / lóa (kiểm chứng Gamma > 1)
│   ├── xray_simulation.png     # Mô phỏng ảnh X-quang y tế (kiểm chứng Âm bản)
│   └── gray_ramp_shapes.png    # Thang độ xám và các chi tiết hình học chuẩn
├── experiments_output/         # Thư mục lưu trữ biểu đồ và số liệu thực nghiệm
│   ├── *_comparison_overview.png
│   ├── *_gamma_sweep.png
│   ├── *_gamma_metrics_graph.png
│   ├── *_metrics.csv
│   └── SUMMARY_RESULTS.md      # Bảng tổng kết số liệu định lượng tự động
├── transformations.py          # Thư viện thuật toán cốt lõi & đo lường chi tiết
├── sample_generator.py         # Script sinh bộ ảnh kiểm nghiệm chuẩn
├── run_experiments.py          # Script chạy toàn bộ quy trình thực nghiệm tự động
├── app.py                      # Ứng dụng Desktop GUI chuyên nghiệp (CustomTkinter)
├── BAO_CAO_BTL.md              # Báo cáo BTL đầy đủ chi tiết (lý thuyết, thực nghiệm, kết luận)
└── README.md                   # Hướng dẫn cài đặt và sử dụng
```

---

## 🚀 3. Hướng dẫn cài đặt & Chạy chương trình

### Yêu cầu môi trường
- Python >= 3.9 (Đã kiểm nghiệm hoàn hảo trên Python 3.14)
- Các thư viện cần thiết:
```bash
pip install opencv-python numpy matplotlib customtkinter pillow pandas tabulate
```

### 3.1. Chạy Ứng dụng Giao diện Đồ họa (GUI)
Để khởi động giao diện trực quan hiện đại:
```bash
python app.py
```
**Các tính năng nổi bật của ứng dụng GUI:**
- **Tab 1 - Khảo sát tương tác real-time:** Kéo thanh trượt tham số $\gamma$ và $c$ để xem ngay lập tức ảnh biến đổi, biểu đồ Histogram đối chiếu và bản đồ biên Sobel.
- **Tab 2 - So sánh đồng thời 4 phương pháp:** Hiển thị trực quan cùng lúc Ảnh gốc, Âm bản, Logarit và Gamma với biểu đồ Histogram và Biên Sobel tương ứng.
- **Tab 3 - Phân tích tham số Gamma:** Tự động vẽ đồ thị tương quan giữa $\gamma$ và chỉ số nét chi tiết Tenengrad & Mật độ biên Otsu.
- **Nút "Mở ảnh từ máy..."**: Cho phép chọn bất kỳ ảnh nào của người dùng để khảo sát.
- **Nút "Lưu ảnh kết quả"**: Xuất ảnh chất lượng cao sau khi đã tinh chỉnh tham số ưng ý.

### 3.2. Chạy Thực nghiệm Tự động & Xuất Toàn Bộ Báo Cáo
Để tái tạo lại toàn bộ kết quả phân tích trên 4 bộ ảnh mẫu:
```bash
python run_experiments.py
```
Toàn bộ biểu đồ sắc nét và file bảng số liệu định lượng sẽ được lưu tự động trong thư mục `experiments_output/`.
