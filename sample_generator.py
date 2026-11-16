"""
Tạo các ảnh mẫu phục vụ thử nghiệm các phép biến đổi:
1. dark_scene.png: Ảnh tối / thiếu sáng (minh họa Gamma < 1 và Log)
2. overexposed.png: Ảnh chói sáng / dư sáng (minh họa Gamma > 1)
3. xray_simulation.png: Mô phỏng ảnh y tế / X-quang (minh họa Phép biến đổi Âm bản)
4. gray_ramp_shapes.png: Ảnh thang độ xám chuẩn và các chi tiết hình học kiểm tra biên
"""

import os
import sys
import cv2
import numpy as np

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def generate_samples(output_dir="sample_images"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Ảnh tổng hợp Thang độ xám & Hình học biên
    h, w = 400, 500
    ramp = np.tile(np.linspace(0, 255, w, dtype=np.uint8), (h, 1))
    cv2.circle(ramp, (120, 150), 60, 40, -1)
    cv2.circle(ramp, (120, 150), 40, 90, -1)
    cv2.rectangle(ramp, (250, 80), (370, 220), 180, -1)
    cv2.rectangle(ramp, (280, 110), (340, 190), 230, -1)
    cv2.putText(ramp, "SOBEL TEST", (100, 320), cv2.FONT_HERSHEY_SIMPLEX, 1.2, 20, 3)
    cv2.putText(ramp, "GAMMA & LOG", (100, 370), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 240, 2)
    cv2.imwrite(os.path.join(output_dir, "gray_ramp_shapes.png"), ramp)
    
    # 2. Ảnh tối / Ban đêm (Dark scene)
    dark = np.zeros((400, 500), dtype=np.uint8)
    for y in range(400):
        for x in range(500):
            val = int(10 + 15 * np.sin(x / 40.0) * np.cos(y / 40.0))
            dark[y, x] = max(0, min(255, val))
            
    cv2.rectangle(dark, (60, 80), (200, 320), 35, -1)
    for r in range(100, 300, 40):
        for c in range(80, 180, 30):
            cv2.rectangle(dark, (c, r), (c + 15, r + 20), 48, -1)
            
    np.random.seed(42)
    stars = np.random.randint(0, 380, (60, 2))
    for s in stars:
        dark[s[0], s[1]] = 75
        
    cv2.putText(dark, "HIDDEN DETAIL IN SHADOW", (50, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 42, 2)
    cv2.imwrite(os.path.join(output_dir, "dark_scene.png"), dark)
    
    # 3. Ảnh dư sáng / Cháy sáng (Overexposed scene)
    bright = np.zeros((400, 500), dtype=np.uint8)
    for y in range(400):
        for x in range(500):
            val = int(225 + 15 * np.sin(x / 50.0))
            bright[y, x] = max(0, min(255, val))
            
    cv2.circle(bright, (250, 180), 90, 205, -1)
    cv2.circle(bright, (250, 180), 50, 245, -1)
    cv2.rectangle(bright, (80, 60), (180, 280), 215, -1)
    cv2.rectangle(bright, (320, 60), (420, 280), 220, -1)
    cv2.putText(bright, "OVEREXPOSED CLOUD", (70, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 210, 2)
    cv2.imwrite(os.path.join(output_dir, "overexposed.png"), bright)
    
    # 4. Mô phỏng ảnh X-quang y tế (X-ray simulation)
    xray = np.zeros((400, 500), dtype=np.uint8)
    cv2.ellipse(xray, (250, 200), (180, 170), 0, 0, 360, 45, -1)
    for y in range(60, 350, 25):
        cv2.rectangle(xray, (235, y), (265, y + 18), 160, -1)
    for i, y in enumerate(range(100, 320, 35)):
        cv2.ellipse(xray, (160, y), (70, 20), -20, 0, 180, 140, 8)
        cv2.ellipse(xray, (340, y), (70, 20), 20, 0, 180, 140, 8)
    cv2.circle(xray, (180, 210), 18, 90, -1)
    cv2.putText(xray, "X-RAY PHANTOM", (140, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 130, 2)
    cv2.imwrite(os.path.join(output_dir, "xray_simulation.png"), xray)
    
    print(f"Đã tạo thành công 4 ảnh mẫu thử nghiệm tại thư mục '{output_dir}/'")


if __name__ == "__main__":
    generate_samples()
