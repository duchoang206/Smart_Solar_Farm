import pandas as pd
import numpy as np
import os

# --- 1. CẤU HÌNH ---
INPUT_EXCEL  = "Ket_Qua_Phan_Tich.xlsx"
OUTPUT_EXCEL = "Ke_Hoach_QHD.xlsx"
BUDGET_SCALE = 1000  # Chia tỉ lệ ngân sách để ma trận không quá lớn (đơn vị: nghìn $)

if not os.path.exists(INPUT_EXCEL):
    print(f"❌ Lỗi: Không tìm thấy file '{INPUT_EXCEL}'. Bạn đã chạy bước xử lý ảnh chưa?")
    exit()

# --- 2. ĐỌC DỮ LIỆU ---
print("1️⃣  Đang đọc dữ liệu từ Excel...")
df = pd.read_excel(INPUT_EXCEL)

if df["Wi_Là_Nước"].dtype == object:
    df["Wi_Là_Nước"] = df["Wi_Là_Nước"].apply(lambda x: 1 if str(x).strip().upper() == "CÓ" else 0)

# Lọc lô hợp lệ
df_land = df[(df["Wi_Là_Nước"] == 0) & (df["Ci_Chi_Phí"] > 0)].copy().reset_index(drop=True)
n = len(df_land)
print(f"   -> Tổng số lô hợp lệ (đất liền): {n}")

# --- 3. NGÂN SÁCH & CHIA TỈ LỆ ---
total_market_value = df["Ci_Chi_Phí"].sum()
BUDGET_RAW = total_market_value * 0.15

# Chia tỉ lệ để ma trận vừa bộ nhớ
W = int(BUDGET_RAW // BUDGET_SCALE)
costs_scaled    = [max(1, int(c // BUDGET_SCALE)) for c in df_land["Ci_Chi_Phí"].tolist()]
energies        = df_land["Ei_Điện_Năng"].tolist()

print(f"   -> Ngân sách gốc         : {BUDGET_RAW:,.0f} $")
print(f"   -> Đơn vị chia tỉ lệ     : {BUDGET_SCALE:,} $/đơn vị")
print(f"   -> W (sau chia tỉ lệ)    : {W} đơn vị")

# Ước lượng bộ nhớ ma trận
mem_mb = (n + 1) * (W + 1) * 8 / (1024 ** 2)
print(f"   -> Kích thước ma trận    : ({n+1}) x ({W+1}) ≈ {mem_mb:.1f} MB")

if mem_mb > 2048:
    print(f"\n⚠️  CẢNH BÁO: Ma trận ~{mem_mb:.0f} MB — nguy cơ tràn bộ nhớ RAM!")
    print(f"   => Tăng BUDGET_SCALE lên để giảm kích thước ma trận.")
    exit()

# --- 4. QUY HOẠCH ĐỘNG (BELLMAN EQUATION) ---
print(f"\n2️⃣  Đang xây dựng bảng QHĐ F[{n+1}][{W+1}]...")

# F[i][j] = sản lượng điện tối đa khi xét i lô đầu tiên, ngân sách = j đơn vị
# Dùng numpy để tăng tốc
F = np.zeros((n + 1, W + 1), dtype=np.float64)

for i in range(1, n + 1):
    ci = costs_scaled[i - 1]   # chi phí lô i (đã chia tỉ lệ)
    ei = energies[i - 1]       # điện năng lô i

    for j in range(W + 1):
        # Trường hợp 1: Không chọn lô i
        F[i][j] = F[i - 1][j]

        # Trường hợp 2: Chọn lô i (chỉ khi đủ ngân sách)
        if j >= ci:
            val_if_pick = F[i - 1][j - ci] + ei
            if val_if_pick > F[i][j]:
                F[i][j] = val_if_pick

    print(f"   Đã xử lý lô {i:>3}/{n}  —  F[{i}][{W}] = {F[i][W]:,.2f} kWh")

print(f"\n   ✅ Sản lượng tối ưu tuyệt đối: {F[n][W]:,.2f} kWh")

# --- 5. TRUY VẾT NGHIỆM (BACKTRACKING) ---
print("\n3️⃣  Đang truy vết nghiệm tối ưu...")

selected_indices = []
j = W
for i in range(n, 0, -1):
    # Nếu F[i][j] > F[i-1][j] → lô i đã được chọn
    if F[i][j] > F[i - 1][j]:
        selected_indices.append(i - 1)         # chỉ số 0-based trong df_land
        j -= costs_scaled[i - 1]               # lùi ngân sách

selected_indices.reverse()

# --- 6. KẾT QUẢ ---
total_invest = sum(df_land.iloc[idx]["Ci_Chi_Phí"] for idx in selected_indices)
total_power  = sum(df_land.iloc[idx]["Ei_Điện_Năng"] for idx in selected_indices)

print(f"\n✅ KẾT QUẢ QUY HOẠCH ĐỘNG:")
print(f"   - Số lô được chọn       : {len(selected_indices)}")
print(f"   - Tổng vốn đầu tư       : {total_invest:,.0f} $ / {BUDGET_RAW:,.0f} $")
print(f"   - Ngân sách còn lại     : {BUDGET_RAW - total_invest:,.0f} $")
print(f"   - Tổng điện năng tối ưu : {total_power:,.2f} kWh")

# --- 7. IN MA TRẬN TRẠNG THÁI (thu gọn, tối đa 10 cột) ---
print("\n📊 Ma trận trạng thái F[i][j] (thu gọn, 10 cột đều nhau):")
sample_cols = np.linspace(0, W, min(11, W + 1), dtype=int).tolist()
header = f"{'i \\ j':>8}" + "".join(f"{c:>10}" for c in sample_cols)
print(header)
print("-" * len(header))
for i in range(n + 1):
    label = f"i={i}" if i > 0 else "i=0"
    row = f"{label:>8}" + "".join(f"{F[i][c]:>10.0f}" for c in sample_cols)
    print(row)

# --- 8. XUẤT EXCEL ---
result_df = df_land.iloc[selected_indices].copy()

if "Pi_Tỉ_Suất" not in result_df.columns:
    result_df["Pi_Tỉ_Suất"] = result_df["Ei_Điện_Năng"] / result_df["Ci_Chi_Phí"]

col_order = ["ID_Lô", "Loại_Đất", "Diện_Tích", "NDVI", "NDWI",
             "Ei_Điện_Năng", "Ci_Chi_Phí", "Pi_Tỉ_Suất", "Wi_Là_Nước"]
col_order = [c for c in col_order if c in result_df.columns]
result_df  = result_df[col_order]

result_df.to_excel(OUTPUT_EXCEL, index=False)
print(f"\n💾 Đã xuất kết quả vào file: '{OUTPUT_EXCEL}'")