import pandas as pd
import os

# --- 1. CẤU HÌNH ---
INPUT_EXCEL  = "Ket_Qua_Phan_Tich.xlsx"   # File output từ image_processing.py
OUTPUT_EXCEL = "Ke_Hoach_Tham_Lam.xlsx"

# Kiểm tra file đầu vào
if not os.path.exists(INPUT_EXCEL):
    print(f"❌ Lỗi: Không tìm thấy file '{INPUT_EXCEL}'. Bạn đã chạy bước xử lý ảnh chưa?")
    exit()

# --- 2. ĐỌC DỮ LIỆU ---
print("1️⃣  Đang đọc dữ liệu từ Excel...")
df = pd.read_excel(INPUT_EXCEL)

# Chuẩn hóa cột Wi_Là_Nước (có thể là int hoặc string)
if df["Wi_Là_Nước"].dtype == object:
    df["Wi_Là_Nước"] = df["Wi_Là_Nước"].apply(lambda x: 1 if str(x).strip().upper() == "CÓ" else 0)

print(f"   -> Đã tải {len(df)} lô đất.")

# --- 3. TIỀN XỬ LÝ ---

# Loại bỏ các lô là nước (Wi = 1) — không thể xây dựng
df_land = df[df["Wi_Là_Nước"] == 0].copy()
print(f"   -> Còn lại {len(df_land)} lô đất hợp lệ (sau khi loại nước).")

# Loại bỏ các lô có chi phí = 0 để tránh chia cho 0
df_land = df_land[df_land["Ci_Chi_Phí"] > 0].copy()

# --- 4. TÍNH TỈ SUẤT SINH LỜI pi = Ei / Ci ---
df_land["Pi_Tỉ_Suất"] = df_land["Ei_Điện_Năng"] / df_land["Ci_Chi_Phí"]

# --- 5. SẮP XẾP THEO TIÊU CHUẨN THAM LAM (pi GIẢM DẦN) ---
df_sorted = df_land.sort_values(by="Pi_Tỉ_Suất", ascending=False).reset_index(drop=True)

print("\n📊 Top 10 lô có tỉ suất sinh lời cao nhất:")
print(df_sorted[["ID_Lô", "Loại_Đất", "Ei_Điện_Năng", "Ci_Chi_Phí", "Pi_Tỉ_Suất"]].head(10).to_string(index=False))

# --- 6. THIẾT LẬP NGÂN SÁCH ---
total_market_value = df["Ci_Chi_Phí"].sum()
BUDGET = total_market_value * 0.15
print(f"\n2️⃣  Ngân sách đầu tư (15% tổng giá trị): {BUDGET:,.0f} $")

# --- 7. THUẬT TOÁN THAM LAM ---
print("\n3️⃣  Đang chạy thuật toán Tham Lam...")

selected_rows = []
remaining_budget = BUDGET
total_power     = 0.0
total_invest    = 0.0

for _, row in df_sorted.iterrows():
    cost = row["Ci_Chi_Phí"]
    energy = row["Ei_Điện_Năng"]

    # Tiêu chuẩn tham lam: chọn lô nếu còn đủ ngân sách
    if cost <= remaining_budget:
        selected_rows.append(row.to_dict())
        remaining_budget -= cost
        total_invest     += cost
        total_power      += energy

# --- 8. KẾT QUẢ ---
result_df = pd.DataFrame(selected_rows)

print("\n✅ KẾT QUẢ THUẬT TOÁN THAM LAM:")
print(f"   - Số lô đất được chọn : {len(selected_rows)}")
print(f"   - Tổng vốn đầu tư     : {total_invest:,.0f} $ / {BUDGET:,.0f} $ ngân sách")
print(f"   - Ngân sách còn lại   : {remaining_budget:,.0f} $")
print(f"   - Tổng điện năng      : {total_power:,.2f} kWh")
if total_invest > 0:
    print(f"   - Tỉ suất trung bình  : {total_power / total_invest:.6f} kWh/$")

# --- 9. XUẤT EXCEL ---
if not result_df.empty:
    # Sắp xếp cột cho dễ đọc
    col_order = ["ID_Lô", "Loại_Đất", "Diện_Tích", "NDVI", "NDWI",
                 "Ei_Điện_Năng", "Ci_Chi_Phí", "Pi_Tỉ_Suất", "Wi_Là_Nước"]
    col_order = [c for c in col_order if c in result_df.columns]
    result_df = result_df[col_order]

    result_df.to_excel(OUTPUT_EXCEL, index=False)
    print(f"\n💾 Đã xuất kết quả vào file: '{OUTPUT_EXCEL}'")
else:
    print("\n⚠️  Không có lô nào được chọn. Kiểm tra lại ngân sách hoặc dữ liệu đầu vào.")