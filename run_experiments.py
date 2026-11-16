"""
Script thực nghiệm toàn diện Đề tài 5:
- Khảo sát các phép biến đổi âm bản, logarit và gamma
- Phân tích ảnh hưởng của tham số qua histogram
- Kết hợp phát hiện biên Sobel để so sánh mức độ bảo toàn chi tiết sau biến đổi
Tự động lưu toàn bộ biểu đồ, ảnh kết quả và bảng số liệu định lượng vào thư mục experiments_output/
"""

import os
import sys
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from transformations import (
    ensure_grayscale,
    negative_transform,
    log_transform,
    gamma_transform,
    sobel_edges,
    compute_metrics,
    calc_histogram
)

# Cấu hình matplotlib hiển thị rõ ràng, font chữ đẹp
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8


def run_comprehensive_study(input_image_path: str, output_subdir: str):
    """
    Thực hiện khảo sát đầy đủ trên một ảnh cụ thể:
    1. So sánh tổng quát: Original vs Negative vs Log vs Gamma (0.4) vs Gamma (2.5)
    2. Khảo sát chuỗi tham số Gamma: [0.2, 0.4, 0.67, 1.0, 1.5, 2.5, 4.0]
    3. Trích xuất bảng số liệu định lượng (Mean Grad, Tenengrad, Edge Count, Contrast)
    """
    os.makedirs(output_subdir, exist_ok=True)
    img_bgr = cv2.imread(input_image_path)
    if img_bgr is None:
        print(f"Lỗi: Không tìm thấy ảnh {input_image_path}")
        return None
        
    gray = ensure_grayscale(img_bgr)
    img_name = os.path.splitext(os.path.basename(input_image_path))[0]
    
    print(f"\n=======================================================")
    print(f"[*] Đang xử lý thực nghiệm trên ảnh: {img_name}")
    print(f"=======================================================")

    # -------------------------------------------------------------
    # 1. TẠO CÁC ẢNH BIẾN ĐỔI CHÍNH
    # -------------------------------------------------------------
    neg = negative_transform(gray)
    log_img = log_transform(gray)
    gamma_04 = gamma_transform(gray, gamma=0.4)
    gamma_25 = gamma_transform(gray, gamma=2.5)
    
    transforms_dict = {
        "Ảnh gốc (Original)": gray,
        "Âm bản (Negative)": neg,
        "Logarit (Log, c auto)": log_img,
        "Gamma (γ = 0.4 - Sáng)": gamma_04,
        "Gamma (γ = 2.5 - Tối)": gamma_25
    }
    
    # -------------------------------------------------------------
    # 2. VẼ BẢNG SO SÁNH TỔNG QUAN: ẢNH | HISTOGRAM | BIÊN SOBEL
    # -------------------------------------------------------------
    fig, axes = plt.subplots(len(transforms_dict), 3, figsize=(15, 3.8 * len(transforms_dict)))
    
    metrics_records = []
    
    for idx, (title, img) in enumerate(transforms_dict.items()):
        # Tính toán Sobel và Metrics
        sb = sobel_edges(img)
        metrics = compute_metrics(gray, img)
        metrics_records.append({
            "Phép biến đổi": title,
            "Độ tương phản (Std)": f"{metrics['trans_contrast']:.2f}",
            "Mean Gradient": f"{metrics['trans_mean_grad']:.2f}",
            "Tỉ lệ Gradient": f"{metrics['grad_ratio']:.2f}",
            "Tenengrad (Chi tiết)": f"{metrics['trans_tenengrad']:.1f}",
            "Pixel biên Otsu": f"{metrics['trans_edge_pixels']:,}",
            "Mật độ biên (%)": f"{metrics['trans_edge_density']:.2f}%"
        })
        
        # Cột 1: Ảnh kết quả
        axes[idx, 0].imshow(img, cmap='gray', vmin=0, vmax=255)
        axes[idx, 0].set_title(f"{title}", fontsize=11, fontweight='bold')
        axes[idx, 0].axis('off')
        
        # Cột 2: Histogram
        hist = calc_histogram(img)
        axes[idx, 1].plot(hist, color='#1f77b4', lw=1.5)
        axes[idx, 1].fill_between(range(256), hist, color='#1f77b4', alpha=0.3)
        axes[idx, 1].set_xlim([0, 256])
        axes[idx, 1].set_title(f"Histogram ({title})", fontsize=10)
        axes[idx, 1].set_xlabel("Mức xám r", fontsize=9)
        axes[idx, 1].set_ylabel("Tần suất", fontsize=9)
        axes[idx, 1].grid(True, linestyle='--', alpha=0.5)
        
        # Cột 3: Bản đồ biên Sobel (Magnitude)
        axes[idx, 2].imshow(sb["magnitude_norm"], cmap='inferno')
        axes[idx, 2].set_title(f"Biên Sobel | Mean Grad: {metrics['trans_mean_grad']:.1f}", fontsize=10)
        axes[idx, 2].axis('off')
        
    plt.tight_layout()
    comparison_chart_path = os.path.join(output_subdir, f"{img_name}_comparison_overview.png")
    fig.savefig(comparison_chart_path, dpi=200)
    plt.close(fig)
    print(f" -> Đã lưu biểu đồ tổng quan: {comparison_chart_path}")

    # -------------------------------------------------------------
    # 3. KHẢO SÁT CHI TIẾT THAM SỐ GAMMA: gamma in [0.2 -> 4.0]
    # -------------------------------------------------------------
    gamma_values = [0.2, 0.4, 0.67, 1.0, 1.5, 2.5, 4.0]
    gamma_records = []
    
    fig_gamma, axes_gamma = plt.subplots(len(gamma_values), 3, figsize=(15, 3.2 * len(gamma_values)))
    
    for g_idx, g in enumerate(gamma_values):
        g_trans = gamma_transform(gray, gamma=g)
        sb_g = sobel_edges(g_trans)
        m = compute_metrics(gray, g_trans)
        
        gamma_records.append({
            "Gamma (γ)": g,
            "Đặc tính": "Làm sáng dải tối" if g < 1 else ("Nguyên bản" if g == 1 else "Làm tối & dãn dải sáng"),
            "Mean Gradient": m['trans_mean_grad'],
            "Tenengrad": m['trans_tenengrad'],
            "Edge Pixels": m['trans_edge_pixels'],
            "Edge Density (%)": m['trans_edge_density'],
            "Contrast (Std)": m['trans_contrast']
        })
        
        # Ảnh Gamma
        axes_gamma[g_idx, 0].imshow(g_trans, cmap='gray', vmin=0, vmax=255)
        axes_gamma[g_idx, 0].set_title(f"γ = {g}", fontsize=11, fontweight='bold')
        axes_gamma[g_idx, 0].axis('off')
        
        # Histogram
        h_g = calc_histogram(g_trans)
        axes_gamma[g_idx, 1].plot(h_g, color='#d62728' if g > 1 else ('#2ca02c' if g < 1 else '#333333'), lw=1.5)
        axes_gamma[g_idx, 1].fill_between(range(256), h_g, alpha=0.25)
        axes_gamma[g_idx, 1].set_xlim([0, 256])
        axes_gamma[g_idx, 1].set_title(f"Histogram (γ = {g})", fontsize=10)
        axes_gamma[g_idx, 1].grid(True, linestyle='--', alpha=0.4)
        
        # Sobel Edges
        axes_gamma[g_idx, 2].imshow(sb_g["magnitude_norm"], cmap='magma')
        axes_gamma[g_idx, 2].set_title(f"Sobel | Tenengrad: {m['trans_tenengrad']:.0f}", fontsize=10)
        axes_gamma[g_idx, 2].axis('off')
        
    plt.tight_layout()
    gamma_sweep_path = os.path.join(output_subdir, f"{img_name}_gamma_sweep.png")
    fig_gamma.savefig(gamma_sweep_path, dpi=200)
    plt.close(fig_gamma)
    print(f" -> Đã lưu khảo sát gamma: {gamma_sweep_path}")

    # -------------------------------------------------------------
    # 4. ĐỒ THỊ ĐỊNH LƯỢNG MỨC ĐỘ BẢO TOÀN CHI TIẾT THEO GAMMA
    # -------------------------------------------------------------
    df_gamma = pd.DataFrame(gamma_records)
    fig_metrics, ax1 = plt.subplots(figsize=(9, 5))
    
    color_ten = '#1f77b4'
    ax1.set_xlabel('Tham số Gamma (γ)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Tenengrad Focus Measure (Độ nét chi tiết)', color=color_ten, fontsize=11, fontweight='bold')
    line1 = ax1.plot(df_gamma["Gamma (γ)"], df_gamma["Tenengrad"], marker='o', lw=2.5, color=color_ten, label='Tenengrad Energy')
    ax1.tick_params(axis='y', labelcolor=color_ten)
    ax1.grid(True, linestyle=':', alpha=0.6)
    
    ax2 = ax1.twinx()
    color_edge = '#e65100'
    ax2.set_ylabel('Mật độ điểm biên Otsu (%)', color=color_edge, fontsize=11, fontweight='bold')
    line2 = ax2.plot(df_gamma["Gamma (γ)"], df_gamma["Edge Density (%)"], marker='s', lw=2.5, linestyle='--', color=color_edge, label='Mật độ biên (%)')
    ax2.tick_params(axis='y', labelcolor=color_edge)
    
    plt.title(f"Tương quan Tham số Gamma và Mức độ Bảo toàn Chi tiết Sobel ({img_name})", fontsize=12, fontweight='bold', pad=12)
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='best')
    plt.tight_layout()
    
    metrics_plot_path = os.path.join(output_subdir, f"{img_name}_gamma_metrics_graph.png")
    fig_metrics.savefig(metrics_plot_path, dpi=200)
    plt.close(fig_metrics)
    print(f" -> Đã lưu đồ thị định lượng gamma: {metrics_plot_path}")

    # -------------------------------------------------------------
    # 5. XUẤT BẢNG SỐ LIỆU ĐỊNH LƯỢNG (CSV & MARKDOWN)
    # -------------------------------------------------------------
    df_main = pd.DataFrame(metrics_records)
    csv_path = os.path.join(output_subdir, f"{img_name}_metrics.csv")
    df_main.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    return {
        "img_name": img_name,
        "df_main": df_main,
        "df_gamma": df_gamma,
        "chart_overview": comparison_chart_path,
        "chart_gamma": gamma_sweep_path,
        "chart_metrics": metrics_plot_path
    }


def main():
    sample_dir = "sample_images"
    results_base = "experiments_output"
    os.makedirs(results_base, exist_ok=True)
    
    sample_images = [
        os.path.join(sample_dir, "dark_scene.png"),
        os.path.join(sample_dir, "overexposed.png"),
        os.path.join(sample_dir, "xray_simulation.png"),
        os.path.join(sample_dir, "gray_ramp_shapes.png")
    ]
    
    all_summaries = []
    
    for img_path in sample_images:
        res = run_comprehensive_study(img_path, results_base)
        if res:
            all_summaries.append(res)
            
    # Tạo bảng báo cáo Markdown tổng kết
    summary_md_path = os.path.join(results_base, "SUMMARY_RESULTS.md")
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("# TỔNG HỢP KẾT QUẢ THỰC NGHIỆM ĐỀ TÀI 5\n\n")
        f.write("**Đề tài:** Khảo sát các phép biến đổi âm bản, logarit và gamma\n")
        f.write("**Yêu cầu:** Cài đặt ba phép biến đổi; phân tích ảnh hưởng của tham số qua histogram; kết hợp phát hiện biên Sobel để so sánh mức độ bảo toàn chi tiết sau biến đổi.\n\n")
        f.write("---\n\n")
        
        for item in all_summaries:
            name = item["img_name"]
            f.write(f"## 1. Phân tích trên ảnh `{name}`\n\n")
            f.write("### Bảng 1: So sánh định lượng giữa các phép biến đổi\n\n")
            # Fallback nếu tabulate chưa cài
            try:
                f.write(item["df_main"].to_markdown(index=False))
            except Exception:
                f.write(item["df_main"].to_string(index=False))
            f.write("\n\n")
            f.write("### Bảng 2: Khảo sát chi tiết dải tham số Gamma (Power-Law)\n\n")
            try:
                f.write(item["df_gamma"].to_markdown(index=False))
            except Exception:
                f.write(item["df_gamma"].to_string(index=False))
            f.write("\n\n---\n\n")
            
    print(f"\n[DONE] Toàn bộ thực nghiệm hoàn tất! Xem tóm tắt tại: {summary_md_path}")


if __name__ == "__main__":
    main()
