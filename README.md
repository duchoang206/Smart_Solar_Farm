# ☀️ Smart Solar Farm: Tối ưu hóa Vị trí Đầu tư Năng lượng Mặt trời bằng Vệ tinh

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Gurobi](https://img.shields.io/badge/Gurobi-Optimization-red)
![Computer Vision](https://img.shields.io/badge/Computer%20Vision-Sentinel--2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📖 Tổng quan Dự án.
**Smart Solar Farm** là một giải pháp tự động hóa quy trình khảo sát địa điểm đầu tư năng lượng tái tạo. Dự án thay thế các phương pháp khảo sát thủ công tốn kém bằng cách kết hợp dữ liệu ảnh vệ tinh đa phổ và các mô hình toán học tối ưu.

Mục tiêu cốt lõi là **tối đa hóa sản lượng điện năng** thu được dựa trên một mức ngân sách giới hạn, đồng thời tự động loại bỏ các khu vực địa hình không phù hợp (như mặt nước).

---

## 🧠 Phương pháp & Thuật toán.

Dự án được chia thành 2 module chính, ứng dụng Thị giác máy tính (Computer Vision) và Nghiên cứu Vận trù học (Operations Research).

### Giai đoạn 1: Xử lý ảnh vệ tinh (Computer Vision).
Hệ thống sử dụng ảnh vệ tinh từ **Sentinel-2** (định dạng `.SAFE`) để phân tích bề mặt Trái Đất.
* **Trích xuất dải màu:** Đọc các băng tần quang phổ B04 (Red), B03 (Green), và B08 (Near-Infrared - NIR).
* **Tính toán chỉ số quang phổ:**
    * Chỉ số thực vật (NDVI): $$NDVI=\frac{NIR-Red}{NIR+Red}$$
    * Chỉ số nước (NDWI): $$NDWI=\frac{Green-NIR}{Green+NIR}$$
* **Phân mảnh hình ảnh (Segmentation):** Sử dụng thuật toán **SLIC Super-pixels** (với $n\_segments=300$, $compactness=20$) để tự động nhóm các pixel có chung đặc điểm địa hình thành các lô đất độc lập.
* **Phân loại & Định giá:** Dựa vào NDVI/NDWI, hệ thống phân loại đất thành 4 nhóm: *Nước, Rừng, Đất trống, Cây bụi* và gán chi phí đầu tư ($C_i$) cũng như tiềm năng điện năng ($E_i$) tương ứng cho từng lô đất.

### Giai đoạn 2: Tối ưu hóa (Operations Research)
Sử dụng **Gurobi Optimizer** để giải bài toán Quy hoạch Phân nguyên (Mixed-Integer Programming - MIP) nhằm chọn ra danh sách các lô đất tối ưu nhất.

* **Biến quyết định ($x_i$):** $x_i \in \{0, 1\}$. $x_i = 1$ nếu chọn lô đất $i$, ngược lại bằng $0$.
* **Hàm mục tiêu:** Tối đa hóa tổng sản lượng điện năng.
    $$Maximize \sum (E_i \times x_i)$$
* **Ràng buộc ngặt (Constraints):**
    1.  **Ngân sách:** Tổng chi phí đầu tư không vượt quá 15% tổng giá trị thị trường của toàn bộ khu vực khảo sát.
        $$\sum (C_i \times x_i) \leq Budget$$
    2.  **Môi trường:** Không xây dựng trên các lô đất được xác định là mặt nước ($W_i = 1$).
        $$x_i = 0 \quad \text{nếu} \quad W_i = 1$$

---

## 📂 Cấu trúc Dự án.

```text
Smart_Solar_Farm/
├── data/                   
│   ├── raw/                # Nơi chứa thư mục ảnh vệ tinh gốc (.SAFE)
│   └── processed/          # Chứa các file kết quả trung gian (.xlsx, .csv)
├── src/                    
│   ├── image_processing.py # Script trích xuất ảnh, tính NDVI/NDWI và phân lô
│   └── optimization.py     # Script giải bài toán Gurobi
├── assets/                 # Hình ảnh minh họa dự án
├── requirements.txt        # Danh sách thư viện Python
└── README.md               # Tài liệu dự án
