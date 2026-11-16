"""
Thư viện các hàm biến đổi mức xám và phát hiện biên Sobel
Đề tài 5: Khảo sát các phép biến đổi âm bản, logarit và gamma;
Phân tích ảnh hưởng của tham số qua histogram;
Kết hợp phát hiện biên Sobel để so sánh mức độ bảo toàn chi tiết sau biến đổi.
"""

import cv2
import numpy as np


def ensure_grayscale(image: np.ndarray) -> np.ndarray:
    """Chuyển ảnh sang mức xám nếu là ảnh màu."""
    if len(image.shape) == 3 and image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 3 and image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    return image.copy()


# ==============================================================================
# 1. CÁC PHÉP BIẾN ĐỔI MỨC XÁM (POINT TRANSFORMATIONS)
# ==============================================================================

def negative_transform(image: np.ndarray, max_val: int = 255) -> np.ndarray:
    """
    Phép biến đổi âm bản (Image Negative):
    s = (L - 1) - r
    Với ảnh 8-bit, L = 256 => s = 255 - r
    """
    gray = ensure_grayscale(image)
    return (max_val - gray).astype(np.uint8)


def log_transform(image: np.ndarray, c: float = None) -> np.ndarray:
    """
    Phép biến đổi logarit:
    s = c * log(1 + r)
    Mặc định: c = 255 / log(1 + max(r)) để dãn toàn bộ dải mức xám về [0, 255].
    Có thể truyền c tùy chỉnh để khảo sát ảnh hưởng tham số.
    """
    gray = ensure_grayscale(image).astype(np.float32)
    max_pixel = np.max(gray)
    
    if max_pixel == 0:
        return np.zeros_like(gray, dtype=np.uint8)
        
    if c is None:
        c = 255.0 / np.log(1.0 + max_pixel)
        
    # Áp dụng công thức s = c * ln(1 + r)
    transformed = c * np.log(1.0 + gray)
    transformed = np.clip(transformed, 0, 255)
    return transformed.astype(np.uint8)


def gamma_transform(image: np.ndarray, gamma: float = 1.0, c: float = 1.0) -> np.ndarray:
    """
    Phép biến đổi lũy thừa / Gamma (Power-Law Transformation):
    s = c * (r / 255)^gamma * 255
    - gamma < 1: Tăng độ sáng cho các vùng tối (dãn dải mức xám thấp).
    - gamma = 1: Không đổi (ánh xạ tuyến tính).
    - gamma > 1: Làm tối và tăng độ tương phản các vùng sáng (nén dải mức xám thấp).
    """
    gray = ensure_grayscale(image).astype(np.float32)
    # Chuẩn hóa về [0, 1] để lũy thừa ổn định không bị tràn số
    normalized = gray / 255.0
    transformed = c * (normalized ** gamma) * 255.0
    transformed = np.clip(transformed, 0, 255)
    return transformed.astype(np.uint8)


# ==============================================================================
# 2. TOÁN TỬ SOBEL VÀ ĐO LƯỜNG BẢO TOÀN CHI TIẾT
# ==============================================================================

def sobel_edges(image: np.ndarray, ksize: int = 3) -> dict:
    """
    Áp dụng toán tử Sobel để tính gradient theo hướng x, y và độ lớn Gradient.
    Gx = [-1  0  1]        Gy = [-1 -2 -1]
         [-2  0  2]              [ 0  0  0]
         [-1  0  1]              [ 1  2  1]
    Độ lớn Gradient: G = sqrt(Gx^2 + Gy^2)
    """
    gray = ensure_grayscale(image)
    
    # Tính đạo hàm bậc 1 theo x và y với độ chính xác float32 / float64
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
    
    # Độ lớn Gradient chuẩn
    magnitude = np.sqrt(gx**2 + gy**2)
    
    # Chuẩn hóa về 0-255 để hiển thị trực quan
    magnitude_norm = np.clip(magnitude, 0, 255).astype(np.uint8)
    
    # Tạo ảnh nhị phân biên bằng ngưỡng Otsu
    _, edge_binary = cv2.threshold(magnitude_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return {
        "gx": gx,
        "gy": gy,
        "magnitude": magnitude,
        "magnitude_norm": magnitude_norm,
        "edge_binary": edge_binary
    }


def compute_metrics(original_gray: np.ndarray, transformed_gray: np.ndarray) -> dict:
    """
    Đo lường định lượng mức độ bảo toàn chi tiết và chất lượng ảnh:
    - Mean Gradient Magnitude: Thể hiện độ sắc nét tổng thể của chi tiết.
    - Tenengrad Measure: sum(Gx^2 + Gy^2), chỉ số đo mức độ nét/chi tiết phổ biến trong xử lý ảnh.
    - Edge Pixel Count & Ratio: Số lượng pixel biên phát hiện được (sau ngưỡng Otsu) so với ảnh gốc.
    - Standard Deviation (Độ lệch chuẩn mức xám): Đại diện cho độ tương phản toàn cục.
    """
    orig = ensure_grayscale(original_gray)
    trans = ensure_grayscale(transformed_gray)
    
    sb_orig = sobel_edges(orig)
    sb_trans = sobel_edges(trans)
    
    # 1. Gradient Magnitude trung bình
    mean_grad_orig = float(np.mean(sb_orig["magnitude"]))
    mean_grad_trans = float(np.mean(sb_trans["magnitude"]))
    
    # 2. Tenengrad Measure
    tenengrad_orig = float(np.mean(sb_orig["gx"]**2 + sb_orig["gy"]**2))
    tenengrad_trans = float(np.mean(sb_trans["gx"]**2 + sb_trans["gy"]**2))
    
    # 3. Số pixel biên Otsu
    edge_count_orig = int(np.sum(sb_orig["edge_binary"] > 0))
    edge_count_trans = int(np.sum(sb_trans["edge_binary"] > 0))
    total_pixels = orig.shape[0] * orig.shape[1]
    
    edge_density_orig = (edge_count_orig / total_pixels) * 100.0
    edge_density_trans = (edge_count_trans / total_pixels) * 100.0
    
    # 4. Độ tương phản toàn cục (Standard deviation)
    contrast_orig = float(np.std(orig))
    contrast_trans = float(np.std(trans))
    
    return {
        "orig_mean_grad": mean_grad_orig,
        "trans_mean_grad": mean_grad_trans,
        "grad_ratio": (mean_grad_trans / mean_grad_orig) if mean_grad_orig > 0 else 1.0,
        "orig_tenengrad": tenengrad_orig,
        "trans_tenengrad": tenengrad_trans,
        "orig_edge_pixels": edge_count_orig,
        "trans_edge_pixels": edge_count_trans,
        "orig_edge_density": edge_density_orig,
        "trans_edge_density": edge_density_trans,
        "edge_ratio": (edge_count_trans / edge_count_orig) if edge_count_orig > 0 else 1.0,
        "orig_contrast": contrast_orig,
        "trans_contrast": contrast_trans
    }


def calc_histogram(image: np.ndarray) -> np.ndarray:
    """Tính histogram 256 bins của ảnh mức xám."""
    gray = ensure_grayscale(image)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    return hist.flatten()
