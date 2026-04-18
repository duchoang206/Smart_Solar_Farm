import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import os

# --- 1. CẤU HÌNH ---
input_excel = "Ket_Qua_Phan_Tich.xlsx"
output_excel = "Ke_Hoach_Dau_Tu_Final.xlsx"

# Kiểm tra file đầu vào
if not os.path.exists(input_excel):
    print(f"❌ Lỗi: Không tìm thấy file '{input_excel}'. Bạn đã chạy bước xử lý ảnh chưa?")
    exit()

# --- 2. ĐỌC DỮ LIỆU TỪ EXCEL ---
df = pd.read_excel(input_excel)

# Lấy các cột dữ liệu quan trọng đưa vào list
ids = df["ID_Lô"].tolist()
costs = df["Ci_Chi_Phí"].tolist()
energies = df["Ei_Điện_Năng"].tolist()
is_waters = df["Wi_Là_Nước"].tolist() 
if isinstance(is_waters[0], str):
    is_waters = [1 if x == "CÓ" else 0 for x in is_waters]

num_lots = len(ids)
print(f"   -> Đã tải {num_lots} lô đất tiềm năng.")

# --- 3. THIẾT LẬP BÀI TOÁN GUROBI ---
print("2️⃣ Đang khởi tạo mô hình Gurobi...")

# A. Thiết lập Ngân sách (Giả sử bằng 15% tổng giá trị toàn bộ khu vực)
total_market_value = sum(costs)
BUDGET = total_market_value * 0.15
print(f"   -> Ngân sách đầu tư giới hạn: {BUDGET:,.0f} $")

try:
    # Khởi tạo mô hình
    m = gp.Model("Solar_Farm_Optimization")
    m.setParam('OutputFlag', 1) # Hiển thị log chi tiết

    # B. Tạo biến quyết định (Decision Variables)
    # x[i] = 1 nếu chọn lắp pin tại lô i, ngược lại = 0
    x = m.addVars(num_lots, vtype=GRB.BINARY, name="Select")

    # C. Hàm mục tiêu (Objective Function)
    # Tối đa hóa tổng sản lượng điện năng
    m.setObjective(gp.quicksum(energies[i] * x[i] for i in range(num_lots)), GRB.MAXIMIZE)

    # D. Các ràng buộc (Constraints)
    
    # 1. Ràng buộc Ngân sách
    m.addConstr(gp.quicksum(costs[i] * x[i] for i in range(num_lots)) <= BUDGET, "Budget_Limit")
    
    # 2. Ràng buộc Môi trường: Không được xây trên nước
    for i in range(num_lots):
        if is_waters[i] == 1:
            m.addConstr(x[i] == 0, f"No_Water_{i}")

    # --- 4. GIẢI BÀI TOÁN ---
    print("3️⃣ Gurobi đang tính toán phương án tối ưu...")
    m.optimize()

    # --- 5. XUẤT KẾT QUẢ ---
    if m.status == GRB.OPTIMAL:
        print(" ĐÃ TÌM THẤY PHƯƠNG ÁN TỐI ƯU!")
        
        selected_lots = []
        total_invest = 0
        total_power = 0
        
        # Duyệt qua các biến kết quả
        for i in range(num_lots):
            if x[i].x > 0.5: # Nếu Gurobi quyết định chọn (x=1)
                # Lấy dòng dữ liệu gốc từ Excel
                row_data = df.iloc[i].to_dict()
                selected_lots.append(row_data)
                
                total_invest += costs[i]
                total_power += energies[i]
        
        # Tạo bảng kết quả mới
        result_df = pd.DataFrame(selected_lots)
        
        # Thêm dòng tổng kết
        print(f"   - Tổng vốn đầu tư: {total_invest:,.0f} $ (Trong ngân sách {BUDGET:,.0f})")
        print(f"   - Tổng điện năng: {total_power:,.2f} kWh")
        print(f"   - Số lô đất được chọn: {len(selected_lots)}")
        
        # Xuất ra file Excel mới
        result_df.to_excel(output_excel, index=False)
        print(f"💾 Đã xuất danh sách lô đất cần mua vào file: '{output_excel}'")
        
        
    else:
        print("❌ Không tìm thấy giải pháp nào thỏa mãn.")

except gp.GurobiError as e:
    print(f"Lỗi Gurobi: {e}")
except Exception as e:
    print(f"Lỗi khác: {e}")