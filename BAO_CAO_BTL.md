# BÁO CÁO BÀI TẬP LỚN MÔN XỬ LÝ ẢNH
## ĐỀ TÀI 5: KHẢO SÁT CÁC PHÉP BIẾN ĐỔI ÂM BẢN, LOGARIT VÀ GAMMA; PHÂN TÍCH ẢNH HƯỞNG QUA HISTOGRAM; KẾT HỢP PHÁT HIỆN BIÊN SOBEL ĐỂ SO SÁNH MỨC ĐỘ BẢO TOÀN CHI TIẾT

---

- **Đề tài:** Đề tài 5
- **Nội dung:** Khảo sát các phép biến đổi âm bản, logarit và gamma
- **Yêu cầu:** Cài đặt ba phép biến đổi; phân tích ảnh hưởng của tham số qua histogram; kết hợp phát hiện biên Sobel để so sánh mức độ bảo toàn chi tiết sau biến đổi.

---

## MỤC LỤC
1. [LỜI MỞ ĐẦU](#1-lời-mở-đầu)
2. [CƠ SỞ LÝ THUYẾT](#2-cơ-sở-lý-thuyết)
   - 2.1. Phép biến đổi mức xám trong miền không gian (Point Transformations)
   - 2.2. Phép biến đổi Âm bản (Image Negative)
   - 2.3. Phép biến đổi Logarit (Logarithmic Transformation)
   - 2.4. Phép biến đổi Gamma / Lũy thừa (Power-Law Transformation)
   - 2.5. Phân tích phân bố mức xám qua Histogram
   - 2.6. Toán tử phát hiện biên Sobel và Lý thuyết bảo toàn chi tiết
3. [THIẾT KẾ VÀ CÀI ĐẶT HỆ THỐNG](#3-thiết-kế-và-cài-đặt-hệ-thống)
   - 3.1. Cấu trúc module mã nguồn
   - 3.2. Cài đặt các thuật toán cốt lõi (`transformations.py`)
   - 3.3. Các chỉ số đo lường định lượng bảo toàn chi tiết
   - 3.4. Giao diện người dùng tương tác Desktop GUI (`app.py`)
4. [KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH](#4-kết-quả-thực-nghiệm-và-phân-tích)
   - 4.1. Thử nghiệm trên Ảnh thiếu sáng / Chụp ban đêm (`dark_scene`)
   - 4.2. Thử nghiệm trên Ảnh cháy sáng / Dư sáng (`overexposed`)
   - 4.3. Thử nghiệm trên Ảnh y tế / Mô phỏng X-quang (`xray_simulation`)
   - 4.4. Thử nghiệm trên Thang độ xám và Hình học biên (`gray_ramp_shapes`)
   - 4.5. Phân tích tổng hợp ảnh hưởng của tham số Gamma $\gamma$
5. [ĐÁNH GIÁ VÀ BÀN LUẬN](#5-đánh-giá-và-bàn-luận)
6. [KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN](#6-kết-luận-và-hướng-phát-triển)

---

## 1. LỜI MỞ ĐẦU

Trong kỹ thuật Xử lý ảnh số (Digital Image Processing), tăng cường ảnh trong miền không gian (Spatial Domain Image Enhancement) là một trong những bước tiền xử lý thiết yếu nhằm nâng cao chất lượng thị giác cho người quan sát hoặc làm nổi bật các đặc trưng quan trọng phục vụ các tác vụ phân tích, phân đoạn (segmentation) và nhận dạng tự động.

Trong số các phương pháp biến đổi điểm (Point Operations), ba phép biến đổi kinh điển và nền tảng nhất là:
1. **Phép biến đổi Âm bản (Negative):** Đảo ngược thang độ xám, đặc biệt hiệu quả trong chẩn đoán hình ảnh y tế.
2. **Phép biến đổi Logarit:** Nén dải động cực lớn và làm nổi bật các chi tiết trong vùng tối.
3. **Phép biến đổi Lũy thừa / Gamma (Power-Law):** Phương pháp hiệu chỉnh độ sáng phi tuyến đa năng, cho phép tinh chỉnh linh hoạt bằng tham số $\gamma$.

Báo cáo này nghiên cứu toàn diện ba phép biến đổi trên cả ba khía cạnh: **cơ sở lý thuyết toán học**, **sự biến thiên phân bố mức xám qua biểu đồ Histogram**, và **đánh giá định tính lẫn định lượng mức độ bảo toàn / làm nổi bật chi tiết biên bằng toán tử vi phân Sobel**.

---

## 2. CƠ SỞ LÝ THUYẾT

### 2.1. Phép biến đổi mức xám trong miền không gian
Biến đổi điểm mức xám ánh xạ giá trị cường độ $r$ của pixel tại vị trí $(x, y)$ của ảnh gốc thành giá trị mức xám mới $s$ của ảnh kết quả thông qua hàm truyền đạt:
$$s = T(r)$$
Trong đó với ảnh mức xám chuẩn 8-bit, $r, s \in [0, L - 1]$ với $L = 256$ (dải mức xám từ $0$ đến $255$).

---

### 2.2. Phép biến đổi Âm bản (Image Negative)
Phép biến đổi âm bản đảo ngược các mức xám theo công thức:
$$s = (L - 1) - r = 255 - r$$
- **Đặc điểm toán học:** Đạo hàm bậc nhất $T'(r) = -1$ (hằng số âm). Đây là một ánh xạ tuyến tính nghịch đảo đối xứng qua điểm trung tâm mức xám $127.5$.
- **Ứng dụng:** Làm nổi bật các chi tiết màu sáng nằm trên nền tối lớn, phổ biến trong hiển thị ảnh chụp X-quang, nhũ ảnh (mammograms) và hiển thị ảnh vi mạch hiển vi.

---

### 2.3. Phép biến đổi Logarit (Logarithmic Transformation)
Hàm biến đổi logarit tổng quát có dạng:
$$s = c \cdot \ln(1 + r)$$
Để đưa toàn bộ dải mức xám sau biến đổi vừa vặn vào khoảng $[0, 255]$, hằng số tỉ lệ chuẩn hóa $c$ được xác định theo giá trị mức xám cực đại của ảnh $\max(r)$:
$$c = \frac{255}{\ln(1 + \max(r))}$$
(Ví dụ: với $\max(r) = 255$, $c \approx \frac{255}{\ln(256)} \approx 45.986$).

- **Đặc điểm toán học:**
  Đạo hàm bậc nhất của hàm biến đổi là:
  $$T'(r) = \frac{c}{1 + r}$$
  - Khi $r$ nhỏ (vùng tối): $T'(r)$ rất lớn ($T'(0) \approx 45.986 \gg 1$), độ dốc của hàm biến đổi rất cao, do đó một dải mức xám hẹp ở vùng tối được dãn rộng thành một dải mức xám lớn.
  - Khi $r$ lớn (vùng sáng): $T'(r)$ giảm dần về $0$ ($T'(255) \approx 0.179 < 1$), dải mức xám cao bị nén chặt lại.
- **Ứng dụng:** Hiển thị phổ biến đổi Fourier (Fourier Spectrum), khôi phục chi tiết ảnh chụp đêm, ảnh viễn thám có dải động sáng chênh lệch cực lớn.

---

### 2.4. Phép biến đổi Gamma / Lũy thừa (Power-Law Transformation)
Công thức chuẩn hóa:
$$s = c \cdot \left(\frac{r}{255}\right)^\gamma \cdot 255$$
(với $c$ là hệ số tỉ lệ, thường $c = 1.0$; $\gamma > 0$ là tham số mũ).

- **Đặc điểm toán học:**
  Đạo hàm bậc nhất:
  $$T'(r) = c \cdot \gamma \cdot \left(\frac{r}{255}\right)^{\gamma - 1}$$
  Phân bố đáp ứng phụ thuộc mật thiết vào giá trị $\gamma$:
  1. **Khi $\gamma < 1$ (ví dụ $\gamma = 0.2, 0.4, 0.67$):**
     Đường cong lồi lên trên ($T''(r) < 0$). Tại vùng mức xám thấp $r \to 0$, $T'(r) \to \infty$. Dải mức xám tối bị kéo dãn mạnh, nâng độ sáng toàn bộ vùng tối mà không làm cháy trắng hoàn toàn vùng sáng.
  2. **Khi $\gamma = 1$:**
     Ánh xạ đồng nhất tuyến tính $s = r$ (không thay đổi ảnh).
  3. **Khi $\gamma > 1$ (ví dụ $\gamma = 1.5, 2.5, 4.0$):**
     Đường cong võng xuống dưới ($T''(r) > 0$). Vùng mức xám thấp bị nén lại về gần $0$ (làm tối sâu), trong khi vùng mức xám cao được kéo dãn dải tương phản. Rất hiệu quả để xử lý ảnh bị dư sáng, cháy sáng hoặc sương mù lóa.

---

### 2.5. Phân tích phân bố mức xám qua Histogram
Biểu đồ Histogram của ảnh mức xám là hàm rời rạc:
$$h(r_k) = n_k$$
trong đó $r_k$ là mức xám thứ $k$ ($0 \le k \le 255$), $n_k$ là số lượng pixel có mức xám bằng $r_k$.
- **Ảnh thiếu sáng (Underexposed):** Histogram lệch hẳn về phía bên trái (gần mức 0).
- **Ảnh dư sáng (Overexposed):** Histogram dồn cục về phía bên phải (gần mức 255).
- **Ảnh tương phản thấp (Low contrast):** Histogram tập trung bó hẹp ở một khoảng hẹp ở giữa.
- **Tác động của phép biến đổi:**
  Dựa trên định luật bảo toàn xác suất của biến ngẫu nhiên liên tục:
  $$p_s(s) = p_r(r) \left| \frac{dr}{ds} \right| = \frac{p_r(r)}{|T'(r)|}$$
  - Ở những vùng có $|T'(r)| > 1$ (dãn dải mức xám), mật độ xác suất $p_s(s)$ giảm xuống và các cột Histogram phân tách thưa ra.
  - Ở những vùng có $|T'(r)| < 1$ (nén dải mức xám), các mức xám bị dồn sát vào nhau tạo thành các đỉnh nhọn Histogram.

---

### 2.6. Toán tử phát hiện biên Sobel và Lý thuyết bảo toàn chi tiết

#### 2.6.1. Định nghĩa toán tử Sobel
Toán tử Sobel xấp xỉ đạo hàm riêng không gian bậc một theo hướng ngang ($x$) và dọc ($y$) bằng cách chập ảnh với hai ma trận nhân chập $3 \times 3$:
$$G_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix} * I, \quad G_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix} * I$$
Độ lớn Gradient tại mỗi điểm ảnh $(x, y)$ được tính bằng:
$$G(x, y) = \sqrt{G_x^2(x, y) + G_y^2(x, y)}$$

#### 2.6.2. Mối quan hệ toán học giữa Biến đổi Mức xám và Gradient Biên
Xét hàm biến đổi $s = T(r)$. Theo quy tắc đạo hàm hàm hợp trong giải tích vi phân nhiều chiều:
$$\frac{\partial s}{\partial x} = T'(r) \cdot \frac{\partial r}{\partial x}, \quad \frac{\partial s}{\partial y} = T'(r) \cdot \frac{\partial r}{\partial y}$$
Do đó, độ lớn Gradient sau biến đổi thỏa mãn hệ thức:
$$G_s = \sqrt{\left(\frac{\partial s}{\partial x}\right)^2 + \left(\frac{\partial s}{\partial y}\right)^2} = |T'(r)| \cdot \sqrt{\left(\frac{\partial r}{\partial x}\right)^2 + \left(\frac{\partial r}{\partial y}\right)^2} = |T'(r)| \cdot G_r$$

> **Định lý quan trọng về bảo toàn chi tiết:**
> 1. Với **phép biến đổi Âm bản**: $T'(r) = -1 \implies |T'(r)| = 1$. Độ lớn Gradient $G_s = G_r$. **Phép biến đổi âm bản bảo toàn hoàn hảo 100% biên độ chi tiết Sobel!**
> 2. Với **phép biến đổi Logarit & Gamma ($\gamma < 1$)**: Tại các vùng tối ($r$ nhỏ), $|T'(r)| \gg 1$, do đó $G_s \gg G_r$. Các đường biên chìm, mờ nhạt trong bóng tối được **khuếch đại độ tương phản cực mạnh**, giúp toán tử Sobel phát hiện rõ nét những chi tiết mà trên ảnh gốc mắt người và máy tính đều không thấy được.
> 3. Ngược lại, tại vùng sáng với Gamma $\gamma < 1$, $|T'(r)| < 1$, biên độ chi tiết vùng sáng bị nén nhẹ. Với Gamma $\gamma > 1$, $|T'(r)| > 1$ ở vùng sáng, giúp khôi phục chi tiết cho ảnh bị cháy sáng.

---

## 3. THIẾT KẾ VÀ CÀI ĐẶT HỆ THỐNG

### 3.1. Cấu trúc module mã nguồn
Dự án được tổ chức khoa học thành 4 file chính:
- `transformations.py`: Cài đặt thuần túy các thuật toán xử lý ảnh, biến đổi mức xám, tính toán ma trận vi phân Sobel và bộ đo lường chi tiết định lượng.
- `sample_generator.py`: Tự động tạo 4 ảnh mẫu đại diện cho các kịch bản thực tế (ảnh tối, ảnh cháy sáng, ảnh X-quang, thang độ xám chuẩn).
- `run_experiments.py`: Script tự động hóa toàn bộ quy trình thực nghiệm, xuất biểu đồ đối chiếu và sinh file tổng hợp báo cáo `SUMMARY_RESULTS.md`.
- `app.py`: Ứng dụng Desktop chuyên nghiệp xây dựng bằng thư viện `CustomTkinter` với giao diện Dark Mode hiện đại, hỗ trợ tương tác trượt thanh tham số real-time.

---

### 3.2. Cài đặt các thuật toán cốt lõi (`transformations.py`)

```python
# Trích đoạn cài đặt các hàm toán học cốt lõi
def negative_transform(image: np.ndarray, max_val: int = 255) -> np.ndarray:
    gray = ensure_grayscale(image)
    return (max_val - gray).astype(np.uint8)

def log_transform(image: np.ndarray, c: float = None) -> np.ndarray:
    gray = ensure_grayscale(image).astype(np.float32)
    max_pixel = np.max(gray)
    if c is None:
        c = 255.0 / np.log(1.0 + max_pixel)
    transformed = c * np.log(1.0 + gray)
    return np.clip(transformed, 0, 255).astype(np.uint8)

def gamma_transform(image: np.ndarray, gamma: float = 1.0, c: float = 1.0) -> np.ndarray:
    gray = ensure_grayscale(image).astype(np.float32)
    normalized = gray / 255.0
    transformed = c * (normalized ** gamma) * 255.0
    return np.clip(transformed, 0, 255).astype(np.uint8)
```

---

### 3.3. Các chỉ số đo lường định lượng bảo toàn chi tiết
Để đánh giá một cách khoa học mức độ bảo toàn và nâng cao chi tiết biên sau biến đổi, hệ thống sử dụng 4 chỉ số định lượng:
1. **Mean Gradient Magnitude ($\bar{G}$):** Độ lớn gradient trung bình toàn ảnh.
2. **Tenengrad Focus Measure:** Chỉ số kinh điển đo năng lượng biên và độ sắc nét chi tiết:
   $$\text{Tenengrad} = \frac{1}{M \times N} \sum_{x} \sum_{y} \left( G_x(x, y)^2 + G_y(x, y)^2 \right)$$
3. **Mật độ điểm biên nhị phân Otsu (% Edge Density):**
   $$\text{Edge Density} = \frac{\sum [G_{\text{norm}}(x, y) > T_{\text{Otsu}}]}{M \times N} \times 100\%$$
4. **Độ tương phản toàn cục ($\sigma$ - Standard Deviation):** Độ lệch chuẩn mức xám của toàn bộ pixel ảnh.

---

### 3.4. Giao diện Desktop GUI (`app.py`)
Giao diện ứng dụng cung cấp:
- Mở ảnh bất kỳ từ hệ thống hoặc chọn nhanh 4 kịch bản ảnh mẫu.
- Chọn giữa 3 phép biến đổi: Âm bản, Logarit, Gamma.
- Thanh trượt tùy biến linh hoạt tham số Gamma $\gamma \in [0.05, 4.0]$ và hệ số tỉ lệ $c$.
- **Tab 1:** Hiển thị song song 4 khung: Ảnh gốc | Ảnh biến đổi | Histogram chồng phổ | Bản đồ nhiệt biên Sobel.
- **Tab 2:** So sánh tổng thể đồng thời 4 chế độ trên cùng một màn hình.
- **Tab 3:** Vẽ đồ thị tương quan tham số $\gamma$ với Tenengrad Energy và Mật độ biên.
- Nút xuất file ảnh kết quả độ nét cao.

---

## 4. KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH

Dưới đây là các kết quả định lượng chi tiết được trích xuất tự động từ hệ thống thử nghiệm trên 4 tập dữ liệu đại diện.

### 4.1. Thử nghiệm trên Ảnh thiếu sáng / Chụp ban đêm (`dark_scene`)
Ảnh chụp ban đêm có mức xám tập trung rất thấp trong khoảng $[0, 50]$, mắt thường chỉ thấy một màu đen xì bao phủ.

#### Bảng số liệu định lượng:
| Phép biến đổi | Độ tương phản ($\sigma$) | Mean Gradient | Tỉ lệ Gradient | Tenengrad (Chi tiết) | Pixel biên Otsu | Mật độ biên (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Ảnh gốc (Original)** | 12.70 | 5.13 | 1.00x | 374.8 | 7,853 | 3.93% |
| **Âm bản (Negative)** | 12.70 | 5.13 | 1.00x | 374.8 | 7,853 | 3.93% |
| **Logarit (Log, $c$ auto)** | **64.92** | **23.47** | **4.57x** | **6,823.2** | **7,878** | **3.94%** |
| **Gamma ($\gamma = 0.4$)** | 34.98 | 13.23 | 2.58x | 2,206.0 | 6,467 | 3.23% |
| **Gamma ($\gamma = 2.5$)** | 0.67 | 0.30 | 0.06x | 2.7 | 7,842 | 3.92% |

#### Khảo sát chi tiết dải tham số Gamma ($\gamma$):
| Gamma ($\gamma$) | Đặc tính tác động | Mean Gradient | Tenengrad | Edge Density (%) | Độ tương phản ($\sigma$) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **0.20** | Kéo dãn cực mạnh dải tối | 16.98 | 4,815.8 | 3.34% | 50.17 |
| **0.40** | Làm sáng hài hòa dải tối | 13.23 | 2,206.0 | 3.23% | 34.98 |
| **0.67** | Nâng sáng nhẹ | 8.84 | 1,000.0 | 2.26% | 22.23 |
| **1.00** | Nguyên bản | 5.13 | 374.8 | 3.93% | 12.70 |
| **1.50** | Nén dải tối | 2.17 | 82.1 | 3.96% | 5.14 |
| **2.50** | Làm tối sâu | 0.30 | 2.7 | 3.92% | 0.67 |
| **4.00** | Gần như đen hoàn toàn | 0.004 | 0.007 | 0.24% | 0.02 |

#### Nhận xét chuyên sâu:
1. **Biến đổi Logarit** cho hiệu quả kinh ngạc: Độ tương phản tăng gấp **5.1 lần** (từ 12.7 lên 64.92). Độ sắc nét chi tiết Tenengrad tăng vọt từ $374.8$ lên $6,823.2$ (gấp **18.2 lần**). Bản đồ biên Sobel bộc lộ rõ toàn bộ các viền cửa sổ, đường viền ngôi nhà và các chi tiết vi mô bị chìm trong bóng tối.
2. **Biến đổi Gamma ($\gamma = 0.4$)** cũng cải thiện vượt bậc với Mean Gradient tăng $2.58$ lần và Tenengrad tăng gần $6$ lần.
3. Khi tăng $\gamma > 1$ trên ảnh tối, dải tối bị nén triệt để về $0$, gradient sụt giảm nghiêm trọng và chi tiết hoàn toàn biến mất.

---

### 4.2. Thử nghiệm trên Ảnh cháy sáng / Dư sáng (`overexposed`)
Ảnh chụp cảnh trời nắng gắt hoặc lóa đèn, đa số pixel dồn về dải cực cao $[200, 255]$.

#### Bảng số liệu định lượng:
| Phép biến đổi | Độ tương phản ($\sigma$) | Mean Gradient | Tỉ lệ Gradient | Tenengrad (Chi tiết) | Mật độ biên (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ảnh gốc (Original)** | 11.09 | 3.10 | 1.00x | 187.5 | 2.02% |
| **Logarit (Log)** | 2.39 | 0.65 | 0.21x | 9.6 | 2.02% |
| **Gamma ($\gamma = 0.4$)** | 4.80 | 1.35 | 0.44x | 36.2 | 2.20% |
| **Gamma ($\gamma = 2.5$)** | **22.92** | **6.39** | **2.06x** | **798.0** | **2.05%** |
| **Gamma ($\gamma = 4.0$)** | **30.48** | **8.41** | **2.71x** | **1,396.5** | **2.07%** |

#### Nhận xét chuyên sâu:
1. Đối với ảnh dư sáng, **phép biến đổi Logarit và Gamma ($\gamma < 1$) phản tác dụng**: Chúng dồn mức xám sáng lên kịch trần $255$, khiến toàn bộ ảnh bị lóa trắng, Tenengrad sụt giảm từ $187.5$ xuống còn $9.6$ (mất chi tiết).
2. Ngược lại, **Gamma $\gamma > 1$ ($\gamma = 2.5, 4.0$) phát huy sức mạnh tối đa**: Đường cong kéo dãn dải sáng giúp tách biệt rõ các vân mây và khối hình học chói sáng. Mean Gradient tăng từ $3.10$ lên $8.41$ (tăng **2.71 lần**), Tenengrad tăng từ $187.5$ lên $1,396.5$ (tăng **7.45 lần**).

---

### 4.3. Thử nghiệm trên Ảnh y tế / Mô phỏng X-quang (`xray_simulation`)
Ảnh chụp X-quang đặc trưng bởi diện tích nền đen lớn, các mô xương và khối tổn thương có cường độ sáng trung gian mờ nhạt.

#### Bảng số liệu định lượng:
| Phép biến đổi | Độ tương phản ($\sigma$) | Mean Gradient | Tenengrad | Mật độ biên (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Ảnh gốc** | 48.64 | 29.93 | 11,219.3 | 9.04% |
| **Âm bản (Negative)** | **48.64** | **29.93** | **11,219.3** | **9.04%** |
| **Logarit** | 105.92 | 30.67 | **16,550.3** | 7.80% |
| **Gamma ($\gamma = 0.4$)**| 78.19 | 30.21 | 12,483.0 | 7.88% |
| **Gamma ($\gamma = 2.5$)**| 21.29 | 15.35 | 3,282.8 | 6.20% |

#### Nhận xét chuyên sâu:
1. **Phép biến đổi Âm bản** thể hiện sự bảo toàn chi tiết toán học chính xác 100%: Mọi chỉ số từ Độ tương phản, Mean Gradient, Tenengrad và Mật độ biên đều trùng khớp hoàn toàn với ảnh gốc. Tuy nhiên, về mặt cảm nhận thị giác của mắt người (Human Visual System), nền chuyển sang màu trắng giúp các tổn thương và đường viền xương màu sẫm trở nên nổi bật và dễ nhận biết hơn rất nhiều.
2. **Biến đổi Logarit** tăng chỉ số Tenengrad lên mức cao nhất ($16,550.3$), làm nổi bật rõ các đường cong xương sườn mảnh mai.

---

### 4.4. Thử nghiệm trên Thang độ xám và Hình học biên (`gray_ramp_shapes`)
Thử nghiệm trên thang độ xám tuyến tính kiểm chứng mối quan hệ giữa đường cong truyền đạt và độ dốc Gradient:
- Biểu đồ Histogram của ảnh gốc trải đều trên toàn dải $[0, 255]$.
- Biến đổi Âm bản đảo ngược hoàn toàn trục hoành của Histogram.
- Biến đổi Logarit đẩy dồn khối lượng xác suất về nửa phải (dải sáng), Histogram có đuôi dài về bên trái.
- Biến đổi Gamma $\gamma = 0.4$ làm dãn khoảng cách các bậc xám ở vùng tối, trong khi $\gamma = 2.5$ nén chặt các bậc xám tối vào sát gốc tọa độ $0$.

---

## 5. ĐÁNH GIÁ VÀ BÀN LUẬN

Từ kết quả phân tích lý thuyết và thực nghiệm, nhóm rút ra bảng tổng kết so sánh giữa ba phương pháp:

| Tiêu chí | Biến đổi Âm bản (Negative) | Biến đổi Logarit (Log) | Biến đổi Gamma (Power-Law) |
| :--- | :--- | :--- | :--- |
| **Bản chất hàm** | Tuyến tính nghịch đảo | Phi tuyến (Logarithmic) | Phi tuyến (Lũy thừa) |
| **Tham số điều khiển** | Không cần tham số | Hệ số tỉ lệ $c$ | Tham số mũ $\gamma$ và hệ số $c$ |
| **Bảo toàn biên Sobel** | **Bảo toàn 100% nguyên vẹn** ($|T'|=1$) | Khuếch đại mạnh ở vùng tối, nén ở vùng sáng | Rất linh hoạt: $\gamma < 1$ khuếch đại vùng tối; $\gamma > 1$ khuếch đại vùng sáng |
| **Độ phức tạp tính toán** | $O(N)$ (cực nhanh, phép trừ) | $O(N)$ (cần tính $\ln$) | $O(N)$ (có thể dùng bảng Look-Up Table - LUT) |
| **Phù hợp nhất cho** | Ảnh y tế X-quang, phim âm bản, vi mạch | Ảnh quá tối, phổ Fourier, ảnh ban đêm | Đa mục đích: cân bằng sáng/tối, hiệu chuẩn màn hình hiển thị |

---

## 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 6.1. Kết luận
Đề tài đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra:
1. Cài đặt chính xác, chuẩn xác về mặt toán học 3 phép biến đổi: Âm bản, Logarit và Gamma.
2. Phân tích tường tận cơ chế biến đổi phân bố mức xám qua biểu đồ Histogram và kiểm chứng quy luật bảo toàn xác suất.
3. Thiết lập hệ thống đo lường định lượng bảo toàn chi tiết bằng toán tử vi phân Sobel qua các chỉ số khoa học: Mean Gradient, Tenengrad Energy, Otsu Edge Density.
4. Chứng minh bằng toán học và thực nghiệm lý do tại sao Âm bản bảo toàn biên tuyệt đối, còn Log và Gamma khuếch đại biên phụ thuộc vào đạo hàm $T'(r)$.
5. Xây dựng ứng dụng Desktop GUI hoàn chỉnh, trực quan, hỗ trợ tương tác tức thời.

### 6.2. Hướng phát triển
- Tích hợp thêm kỹ thuật Cân bằng Histogram (Histogram Equalization - HE) và Cân bằng thích ứng cục bộ (CLAHE) để đối chiếu hiệu quả.
- Tối ưu hóa tốc độ xử lý ảnh độ phân giải siêu cao (4K, 8K) bằng Bảng tra trước giá trị (Look-Up Table - LUT 256 phần tử) trên GPU.
- Mở rộng xử lý tự động cho video thời gian thực từ camera.
