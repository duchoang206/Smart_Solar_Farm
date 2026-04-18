# ☀️ Smart Solar Farm: Satellite-Based Site Selection Optimization

Dự án ứng dụng Computer Vision và Operations Research để tự động hóa việc chọn địa điểm lắp đặt pin năng lượng mặt trời từ dữ liệu vệ tinh Sentinel-2.

## ✨ Tính năng chính
- **Xử lý ảnh vệ tinh:** Tính toán chỉ số NDVI (thực vật) và NDWI (nước) từ các dải phổ B03, B04, B08.
- **Phân lô tự động:** Sử dụng thuật toán SLIC Super-pixels để chia bản đồ thành các lô đất dựa trên đặc tính địa hình.
- **Tối ưu hóa đầu tư:** Sử dụng Gurobi Optimizer để tìm danh mục lô đất tối đa hóa sản lượng điện trong giới hạn ngân sách 15% tổng giá trị khu vực.

## 📂 Cấu trúc dự án
- `src/`: Chứa mã nguồn xử lý ảnh và mô hình tối ưu hóa.
- `data/`: Chứa dữ liệu vệ tinh gốc và các bảng kết quả phân tích.
- `assets/`: Hình ảnh minh họa dự án.

## 🚀 Cách sử dụng
1. Cài đặt thư viện: `pip install pandas numpy matplotlib rasterio scikit-image gurobipy`
2. Chạy xử lý ảnh: `python src/image_processing.py`
3. Chạy tối ưu hóa: `python src/optimization.py`

## 👨‍💻 Tác giả
- **Hoàng Xuân Đức**  Sinh viên VNU-HUS.