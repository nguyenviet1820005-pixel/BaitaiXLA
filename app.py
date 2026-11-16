"""
Ứng dụng Giao diện Đồ họa (GUI) Đề tài 5:
Khảo sát các phép biến đổi âm bản, logarit và gamma;
Phân tích ảnh hưởng của tham số qua histogram;
Kết hợp phát hiện biên Sobel để so sánh mức độ bảo toàn chi tiết sau biến đổi.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from transformations import (
    ensure_grayscale,
    negative_transform,
    log_transform,
    gamma_transform,
    sobel_edges,
    compute_metrics,
    calc_histogram
)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ImageProcessingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Xử Lý Ảnh - Khảo sát Biến đổi Âm bản, Logarit, Gamma & Biên Sobel")
        self.geometry("1400x900")
        self.minsize(1100, 750)

        # Trạng thái dữ liệu
        self.current_image_path = None
        self.original_gray = None
        self.processed_gray = None

        # Thiết lập giao diện
        self._setup_layout()

        # Nạp ảnh mẫu mặc định nếu có
        sample_default = os.path.join("sample_images", "dark_scene.png")
        if os.path.exists(sample_default):
            self.load_image(sample_default)

    def _setup_layout(self):
        # Grid layout (1 hàng, 2 cột: Sidebar và Main Panel)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==============================================================
        # 1. SIDEBAR (Bảng điều khiển bên trái)
        # ==============================================================
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)

        # Tiêu đề & Thông tin sinh viên
        lbl_title = ctk.CTkLabel(
            self.sidebar, 
            text="BIẾN ĐỔI MỨC XÁM\n& BẢO TOÀN BIÊN SOBEL", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#38bdf8"
        )
        lbl_title.pack(padx=15, pady=(15, 5))

        lbl_subtitle = ctk.CTkLabel(
            self.sidebar, 
            text="Phân tích Histogram &\nĐánh giá bảo toàn chi tiết Sobel",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
            justify="center"
        )
        lbl_subtitle.pack(padx=15, pady=(0, 15))

        # Phân cách
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#334155").pack(fill="x", padx=15, pady=5)

        # Chọn nguồn ảnh
        lbl_source = ctk.CTkLabel(self.sidebar, text="1. Nguồn Ảnh Đầu Vào", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_source.pack(anchor="w", padx=15, pady=(10, 5))

        self.btn_open = ctk.CTkButton(
            self.sidebar, 
            text="📁 Mở ảnh từ máy...", 
            command=self._on_choose_file,
            fg_color="#0284c7",
            hover_color="#0369a1"
        )
        self.btn_open.pack(fill="x", padx=15, pady=5)

        # Danh sách ảnh mẫu có sẵn
        self.sample_combobox = ctk.CTkComboBox(
            self.sidebar,
            values=[
                "Ảnh tối (dark_scene.png)",
                "Ảnh cháy sáng (overexposed.png)",
                "Ảnh X-quang (xray_simulation.png)",
                "Ảnh thang độ xám (gray_ramp_shapes.png)"
            ],
            command=self._on_select_sample
        )
        self.sample_combobox.pack(fill="x", padx=15, pady=5)

        # Phân cách
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#334155").pack(fill="x", padx=15, pady=10)

        # Chọn phép biến đổi
        lbl_trans = ctk.CTkLabel(self.sidebar, text="2. Phép Biến Đổi Mức Xám", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_trans.pack(anchor="w", padx=15, pady=(5, 5))

        self.trans_mode = ctk.StringVar(value="gamma")
        
        self.rb_gamma = ctk.CTkRadioButton(
            self.sidebar, text="Biến đổi Gamma (Power-Law)", 
            variable=self.trans_mode, value="gamma", command=self.update_processing
        )
        self.rb_gamma.pack(anchor="w", padx=20, pady=4)

        self.rb_log = ctk.CTkRadioButton(
            self.sidebar, text="Biến đổi Logarit (Log)", 
            variable=self.trans_mode, value="log", command=self.update_processing
        )
        self.rb_log.pack(anchor="w", padx=20, pady=4)

        self.rb_neg = ctk.CTkRadioButton(
            self.sidebar, text="Biến đổi Âm bản (Negative)", 
            variable=self.trans_mode, value="negative", command=self.update_processing
        )
        self.rb_neg.pack(anchor="w", padx=20, pady=4)

        # Thanh trượt tham số Gamma
        self.lbl_gamma_val = ctk.CTkLabel(self.sidebar, text="Tham số Gamma (γ = 0.40):", font=ctk.CTkFont(size=12))
        self.lbl_gamma_val.pack(anchor="w", padx=15, pady=(10, 2))
        
        self.slider_gamma = ctk.CTkSlider(
            self.sidebar, from_=0.05, to=4.0, number_of_steps=79,
            command=self._on_gamma_change
        )
        self.slider_gamma.set(0.40)
        self.slider_gamma.pack(fill="x", padx=15, pady=2)

        # Tùy chọn hằng số c cho Log và Gamma
        self.lbl_c_val = ctk.CTkLabel(self.sidebar, text="Hằng số tỉ lệ c (c = 1.0):", font=ctk.CTkFont(size=12))
        self.lbl_c_val.pack(anchor="w", padx=15, pady=(10, 2))

        self.slider_c = ctk.CTkSlider(
            self.sidebar, from_=0.2, to=3.0, number_of_steps=28,
            command=self._on_c_change
        )
        self.slider_c.set(1.0)
        self.slider_c.pack(fill="x", padx=15, pady=2)

        # Phân cách
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#334155").pack(fill="x", padx=15, pady=10)

        # Tùy chọn hiển thị Sobel
        lbl_sobel_opt = ctk.CTkLabel(self.sidebar, text="3. Tùy Chọn Biên Sobel", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_sobel_opt.pack(anchor="w", padx=15, pady=(5, 5))

        self.sobel_colormap = ctk.StringVar(value="inferno")
        self.cb_colormap = ctk.CTkComboBox(
            self.sidebar,
            values=["inferno", "magma", "gray", "plasma"],
            command=lambda _: self.update_processing()
        )
        self.cb_colormap.set("inferno")
        self.cb_colormap.pack(fill="x", padx=15, pady=5)

        self.var_binary_sobel = ctk.BooleanVar(value=False)
        self.chk_binary_sobel = ctk.CTkCheckBox(
            self.sidebar, text="Biên nhị phân (Ngưỡng Otsu)",
            variable=self.var_binary_sobel,
            command=self.update_processing
        )
        self.chk_binary_sobel.pack(anchor="w", padx=15, pady=5)

        # Nút xuất ảnh
        self.btn_save = ctk.CTkButton(
            self.sidebar, 
            text="💾 Lưu ảnh kết quả", 
            command=self._on_save_result,
            fg_color="#10b981",
            hover_color="#059669"
        )
        self.btn_save.pack(fill="x", padx=15, pady=(20, 10))

        # ==============================================================
        # 2. MAIN PANEL (Các Tab làm việc)
        # ==============================================================
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Tab 1: Khảo sát tương tác (Interactive Studio)
        self.tab1 = self.tabview.add("📊 Khảo Sát Tương Tác & Biên Sobel")
        # Tab 2: So sánh đồng thời 4 chế độ
        self.tab2 = self.tabview.add("🔄 So Sánh Đồng Thời 4 Phương Pháp")
        # Tab 3: Khảo sát dải Gamma
        self.tab3 = self.tabview.add("📈 Phân Tích Dải Tham Số Gamma")

        self._setup_tab1()
        self._setup_tab2()
        self._setup_tab3()

    # ------------------------------------------------------------------
    # TAB 1: KHẢO SÁT TƯƠNG TÁC
    # ------------------------------------------------------------------
    def _setup_tab1(self):
        self.tab1.grid_rowconfigure(0, weight=1)
        self.tab1.grid_columnconfigure(0, weight=1)

        # Frame chứa biểu đồ Matplotlib
        self.fig1 = Figure(figsize=(10, 7.5), dpi=100, facecolor="#1e293b")
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Thanh trạng thái thông số định lượng dưới đáy Tab 1
        self.status_bar1 = ctk.CTkLabel(
            self.tab1,
            text="Đang tải dữ liệu...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8",
            fg_color="#0f172a",
            corner_radius=6,
            height=32
        )
        self.status_bar1.pack(fill="x", padx=5, pady=(0, 5))

    # ------------------------------------------------------------------
    # TAB 2: SO SÁNH ĐỒNG THỜI 4 PHƯƠNG PHÁP
    # ------------------------------------------------------------------
    def _setup_tab2(self):
        self.tab2.grid_rowconfigure(0, weight=1)
        self.tab2.grid_columnconfigure(0, weight=1)

        self.fig2 = Figure(figsize=(11, 7.5), dpi=100, facecolor="#1e293b")
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tab2)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    # ------------------------------------------------------------------
    # TAB 3: PHÂN TÍCH DẢI THAM SỐ GAMMA
    # ------------------------------------------------------------------
    def _setup_tab3(self):
        self.tab3.grid_rowconfigure(0, weight=1)
        self.tab3.grid_columnconfigure(0, weight=1)

        self.fig3 = Figure(figsize=(11, 7.5), dpi=100, facecolor="#1e293b")
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.tab3)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    # ------------------------------------------------------------------
    # XỬ LÝ SỰ KIỆN & VẼ BIỂU ĐỒ
    # ------------------------------------------------------------------
    def _on_choose_file(self):
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"), ("All files", "*.*")]
        path = filedialog.askopenfilename(title="Chọn ảnh xử lý", filetypes=filetypes)
        if path:
            self.load_image(path)

    def _on_select_sample(self, choice):
        filename_map = {
            "Ảnh tối (dark_scene.png)": "dark_scene.png",
            "Ảnh cháy sáng (overexposed.png)": "overexposed.png",
            "Ảnh X-quang (xray_simulation.png)": "xray_simulation.png",
            "Ảnh thang độ xám (gray_ramp_shapes.png)": "gray_ramp_shapes.png"
        }
        fname = filename_map.get(choice, "dark_scene.png")
        path = os.path.join("sample_images", fname)
        if os.path.exists(path):
            self.load_image(path)

    def _on_gamma_change(self, val):
        self.lbl_gamma_val.configure(text=f"Tham số Gamma (γ = {val:.2f}):")
        if self.trans_mode.get() == "gamma":
            self.update_processing()

    def _on_c_change(self, val):
        self.lbl_c_val.configure(text=f"Hằng số tỉ lệ c (c = {val:.2f}):")
        if self.trans_mode.get() in ["gamma", "log"]:
            self.update_processing()

    def load_image(self, path):
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Lỗi", f"Không thể mở file ảnh: {path}")
            return
        self.current_image_path = path
        self.original_gray = ensure_grayscale(img)
        self.update_processing()
        self.update_tab2_and_tab3()

    def update_processing(self):
        if self.original_gray is None:
            return

        mode = self.trans_mode.get()
        c_val = self.slider_c.get()

        if mode == "negative":
            self.processed_gray = negative_transform(self.original_gray)
            title_text = "Phép biến đổi Âm bản (Negative: s = 255 - r)"
        elif mode == "log":
            # Nếu c_val = 1.0 thì dùng c tự động chuẩn hóa, ngược lại scale theo c
            base_c = 255.0 / np.log(1.0 + np.max(self.original_gray) + 1e-5)
            self.processed_gray = log_transform(self.original_gray, c=base_c * c_val)
            title_text = f"Phép biến đổi Logarit (Log: c = {c_val:.2f} * c_std)"
        else: # gamma
            gamma_val = self.slider_gamma.get()
            self.processed_gray = gamma_transform(self.original_gray, gamma=gamma_val, c=c_val)
            title_text = f"Phép biến đổi Gamma (s = {c_val:.2f} * r^{gamma_val:.2f})"

        # Tính toán biên Sobel và định lượng
        sb_orig = sobel_edges(self.original_gray)
        sb_trans = sobel_edges(self.processed_gray)
        metrics = compute_metrics(self.original_gray, self.processed_gray)

        # Cập nhật thanh trạng thái
        status_str = (
            f"Mean Grad: {metrics['orig_mean_grad']:.1f} → {metrics['trans_mean_grad']:.1f} "
            f"({metrics['grad_ratio']:.2f}x) | "
            f"Tenengrad: {metrics['orig_tenengrad']:.0f} → {metrics['trans_tenengrad']:.0f} | "
            f"Mật độ biên: {metrics['orig_edge_density']:.1f}% → {metrics['trans_edge_density']:.1f}% | "
            f"Độ tương phản (Std): {metrics['orig_contrast']:.1f} → {metrics['trans_contrast']:.1f}"
        )
        self.status_bar1.configure(text=status_str)

        # Vẽ Tab 1: 4 ô con (2x2)
        self.fig1.clear()
        cmap_name = self.sobel_colormap.get()
        use_binary = self.var_binary_sobel.get()

        # Ô 1: Ảnh gốc
        ax1 = self.fig1.add_subplot(2, 2, 1)
        ax1.imshow(self.original_gray, cmap='gray', vmin=0, vmax=255)
        ax1.set_title("Ảnh Gốc (Original Grayscale)", color="white", fontsize=11, fontweight="bold")
        ax1.axis('off')

        # Ô 2: Ảnh sau biến đổi
        ax2 = self.fig1.add_subplot(2, 2, 2)
        ax2.imshow(self.processed_gray, cmap='gray', vmin=0, vmax=255)
        ax2.set_title(title_text, color="#38bdf8", fontsize=11, fontweight="bold")
        ax2.axis('off')

        # Ô 3: Đối chiếu Histogram
        ax3 = self.fig1.add_subplot(2, 2, 3)
        h_orig = calc_histogram(self.original_gray)
        h_trans = calc_histogram(self.processed_gray)
        
        ax3.set_facecolor("#0f172a")
        ax3.plot(h_orig, color='#94a3b8', lw=1.5, label='Gốc (Original)')
        ax3.plot(h_trans, color='#38bdf8', lw=2.0, label='Sau Biến Đổi')
        ax3.fill_between(range(256), h_trans, color='#38bdf8', alpha=0.25)
        ax3.set_xlim([0, 256])
        ax3.set_title("So sánh Histogram Mức Xám", color="white", fontsize=11)
        ax3.tick_params(colors="white")
        ax3.legend(facecolor="#1e293b", edgecolor="#475569", labelcolor="white", fontsize=9)
        ax3.grid(True, linestyle="--", alpha=0.3, color="#64748b")

        # Ô 4: Biên Sobel sau biến đổi
        ax4 = self.fig1.add_subplot(2, 2, 4)
        edge_to_show = sb_trans["edge_binary"] if use_binary else sb_trans["magnitude_norm"]
        ax4.imshow(edge_to_show, cmap=cmap_name)
        mode_label = "Biên Nhị Phân Otsu" if use_binary else f"Gradient Sobel ({cmap_name})"
        ax4.set_title(f"{mode_label} | Tenengrad: {metrics['trans_tenengrad']:.0f}", color="white", fontsize=11)
        ax4.axis('off')

        self.fig1.tight_layout()
        self.canvas1.draw()

    def update_tab2_and_tab3(self):
        """Vẽ nội dung cho Tab 2 (So sánh 4 phương pháp) và Tab 3 (Khảo sát Gamma)."""
        if self.original_gray is None:
            return

        gray = self.original_gray
        neg = negative_transform(gray)
        log_img = log_transform(gray)
        gamma_bright = gamma_transform(gray, gamma=0.4)

        # Tab 2: Lưới 4 cột (Ảnh | Histogram | Sobel) cho 4 phương pháp
        self.fig2.clear()
        methods = [
            ("Ảnh Gốc", gray),
            ("Âm Bản", neg),
            ("Logarit", log_img),
            ("Gamma (γ=0.4)", gamma_bright)
        ]

        for i, (name, img) in enumerate(methods):
            sb = sobel_edges(img)
            h = calc_histogram(img)
            m = compute_metrics(gray, img)

            # Cột 1: Ảnh
            ax_img = self.fig2.add_subplot(4, 3, i * 3 + 1)
            ax_img.imshow(img, cmap='gray', vmin=0, vmax=255)
            ax_img.set_title(f"{name}", color="white", fontsize=10, fontweight="bold")
            ax_img.axis('off')

            # Cột 2: Histogram
            ax_h = self.fig2.add_subplot(4, 3, i * 3 + 2)
            ax_h.set_facecolor("#0f172a")
            ax_h.plot(h, color='#38bdf8', lw=1.2)
            ax_h.fill_between(range(256), h, color='#38bdf8', alpha=0.3)
            ax_h.set_xlim([0, 256])
            ax_h.tick_params(colors="white", labelsize=8)
            ax_h.grid(True, linestyle=":", alpha=0.3, color="#64748b")
            ax_h.set_title(f"Histogram", color="#cbd5e1", fontsize=9)

            # Cột 3: Sobel
            ax_s = self.fig2.add_subplot(4, 3, i * 3 + 3)
            ax_s.imshow(sb["magnitude_norm"], cmap='inferno')
            ax_s.set_title(f"Sobel (MeanGrad: {m['trans_mean_grad']:.1f})", color="white", fontsize=9)
            ax_s.axis('off')

        self.fig2.tight_layout()
        self.canvas2.draw()

        # Tab 3: Khảo sát Gamma
        self.fig3.clear()
        gamma_vals = [0.2, 0.4, 0.67, 1.0, 1.5, 2.5, 4.0]
        tenengrad_list = []
        edge_density_list = []

        for g in gamma_vals:
            g_img = gamma_transform(gray, gamma=g)
            m_g = compute_metrics(gray, g_img)
            tenengrad_list.append(m_g['trans_tenengrad'])
            edge_density_list.append(m_g['trans_edge_density'])

        # Biểu đồ đường Tenengrad và Mật độ biên
        ax_metric1 = self.fig3.add_subplot(1, 2, 1)
        ax_metric1.set_facecolor("#0f172a")
        ax_metric1.plot(gamma_vals, tenengrad_list, marker='o', lw=2.5, color='#38bdf8', label='Tenengrad Energy')
        ax_metric1.set_xlabel("Tham số Gamma (γ)", color="white", fontsize=11, fontweight="bold")
        ax_metric1.set_ylabel("Độ nét chi tiết (Tenengrad)", color="#38bdf8", fontsize=11, fontweight="bold")
        ax_metric1.set_title("Năng lượng Chi tiết Sobel theo Gamma", color="white", fontsize=12)
        ax_metric1.tick_params(colors="white")
        ax_metric1.grid(True, linestyle="--", alpha=0.4, color="#64748b")

        ax_metric2 = self.fig3.add_subplot(1, 2, 2)
        ax_metric2.set_facecolor("#0f172a")
        ax_metric2.plot(gamma_vals, edge_density_list, marker='s', lw=2.5, color='#f97316', label='Mật độ biên (%)')
        ax_metric2.set_xlabel("Tham số Gamma (γ)", color="white", fontsize=11, fontweight="bold")
        ax_metric2.set_ylabel("Mật độ điểm biên (%)", color="#f97316", fontsize=11, fontweight="bold")
        ax_metric2.set_title("Tỉ lệ % Điểm Biên Otsu theo Gamma", color="white", fontsize=12)
        ax_metric2.tick_params(colors="white")
        ax_metric2.grid(True, linestyle="--", alpha=0.4, color="#64748b")

        self.fig3.tight_layout()
        self.canvas3.draw()

    def _on_save_result(self):
        if self.processed_gray is None:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh kết quả để lưu!")
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("All files", "*.*")]
        )
        if save_path:
            cv2.imwrite(save_path, self.processed_gray)
            messagebox.showinfo("Thành công", f"Đã lưu ảnh kết quả vào:\n{save_path}")


def main():
    app = ImageProcessingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
