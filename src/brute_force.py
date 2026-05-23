import pandas as pd
import os
from itertools import combinations

# --- 1. CẤU HÌNH ---
INPUT_EXCEL  = "Ket_Qua_Phan_Tich.xlsx"
OUTPUT_EXCEL = "Ke_Hoach_Vet_Can.xlsx"
MAX_LOTS_BRUTE = 20  # Giới hạn an toàn: 2^20 = ~1 triệu tổ hợp

if not os.path.exists(INPUT_EXCEL):
    print(f"❌ Lỗi: Không tìm thấy file '{INPUT_EXCEL}'. Bạn đã chạy bước xử lý ảnh chưa?")
    exit()

# --- 2. ĐỌC DỮ LIỆU ---
print("1️⃣  Đang đọc dữ liệu từ Excel...")
df = pd.read_excel(INPUT_EXCEL)

if df["Wi_Là_Nước"].dtype == object:
    df["Wi_Là_Nước"] = df["Wi_Là_Nước"].apply(lambda x: 1 if str(x).strip().upper() == "CÓ" else 0)

# Lọc lô hợp lệ (không phải nước, chi phí > 0)
df_land = df[(df["Wi_Là_Nước"] == 0) & (df["Ci_Chi_Phí"] > 0)].copy().reset_index(drop=True)
n = len(df_land)
print(f"   -> Tổng số lô hợp lệ: {n}")

# --- 3. NGÂN SÁCH ---
BUDGET = df["Ci_Chi_Phí"].sum() * 0.15
print(f"   -> Ngân sách (15% tổng): {BUDGET:,.0f} $")

# --- 4. CẢNH BÁO QUY MÔ ---
if n > MAX_LOTS_BRUTE:
    print(f"\n⚠️  CẢNH BÁO: {n} lô → 2^{n} = {2**n:,} tổ hợp — quá lớn để vét cạn toàn bộ!")
    print(f"   => Tự động giới hạn còn {MAX_LOTS_BRUTE} lô có tỉ suất π = E/C cao nhất.")
    df_land["Pi"] = df_land["Ei_Điện_Năng"] / df_land["Ci_Chi_Phí"]
    df_land = df_land.nlargest(MAX_LOTS_BRUTE, "Pi").reset_index(drop=True)
    n = len(df_land)

total_combinations = 2 ** n
print(f"\n2️⃣  Bắt đầu vét cạn {total_combinations:,} tổ hợp ({n} lô)...")

costs    = df_land["Ci_Chi_Phí"].tolist()
energies = df_land["Ei_Điện_Năng"].tolist()

# --- 5. VÉT CẠN ---
best_energy  = -1
best_cost    = 0
best_indices = []
checked      = 0
feasible     = 0

# Duyệt tất cả tập con theo kích thước tăng dần (tối ưu nhỏ trước)
for size in range(1, n + 1):
    for combo in combinations(range(n), size):
        checked += 1
        total_cost   = sum(costs[i]    for i in combo)
        total_energy = sum(energies[i] for i in combo)

        # Kiểm tra ràng buộc ngân sách
        if total_cost <= BUDGET:
            feasible += 1
            # Cập nhật nghiệm tốt nhất
            if total_energy > best_energy:
                best_energy  = total_energy
                best_cost    = total_cost
                best_indices = list(combo)

    # In tiến độ mỗi kích thước
    pct = checked / total_combinations * 100
    print(f"   Size {size:>2}: đã kiểm tra {checked:>10,} tổ hợp ({pct:5.1f}%) — "
          f"tốt nhất hiện tại: {best_energy:,.2f} kWh")

# --- 6. KẾT QUẢ ---
print(f"\n✅ KẾT QUẢ VÉT CẠN:")
print(f"   - Tổng tổ hợp đã kiểm tra  : {checked:,}")
print(f"   - Tổ hợp thỏa ngân sách     : {feasible:,}")
print(f"   - Số lô được chọn           : {len(best_indices)}")
print(f"   - Tổng vốn đầu tư           : {best_cost:,.0f} $ / {BUDGET:,.0f} $")
print(f"   - Ngân sách còn lại         : {BUDGET - best_cost:,.0f} $")
print(f"   - Tổng điện năng (tối ưu)   : {best_energy:,.2f} kWh")

# --- 7. XUẤT EXCEL ---
result_df = df_land.iloc[best_indices].copy()

# Tính tỉ suất nếu chưa có
if "Pi_Tỉ_Suất" not in result_df.columns:
    result_df["Pi_Tỉ_Suất"] = result_df["Ei_Điện_Năng"] / result_df["Ci_Chi_Phí"]

col_order = ["ID_Lô", "Loại_Đất", "Diện_Tích", "NDVI", "NDWI",
             "Ei_Điện_Năng", "Ci_Chi_Phí", "Pi_Tỉ_Suất", "Wi_Là_Nước"]
col_order = [c for c in col_order if c in result_df.columns]
result_df = result_df[col_order]

result_df.to_excel(OUTPUT_EXCEL, index=False)
print(f"\n💾 Đã xuất kết quả vào file: '{OUTPUT_EXCEL}'")