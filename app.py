from flask import Flask, render_template, request, jsonify, send_file

import pandas as pd
from io import BytesIO
import os
import csv

app_admin = Flask(__name__)

# print(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "user_data.csv")
if not os.path.exists(CSV_FILE_PATH):
    # 初始化 CSV 檔案，確保有標題行
    with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "personal_number", "name", "surname", "sex", "date_of_birth", "nationality",
            "passport_type", "passport_number", "issuing_country",
            "expiration_date"
        ])

TRIP_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "trip_data.csv")
# 檢查 CSV 檔案是否存在，如果不存在，則創建一個空的 CSV 檔案
if not os.path.exists(TRIP_FILE_PATH):
    df = pd.DataFrame(columns=["id", "name", "destination", "startDate", "participants"])
    df.to_csv(TRIP_FILE_PATH, index=False)

@app_admin.route("/trip.html")
def trip():
    return render_template("backstage/trip.html")

@app_admin.route("/admin.html")
def admin():
    return render_template("backstage/admin.html")

@app_admin.route("/")
def root():
    return render_template("backstage/admin.html")

@app_admin.route("/suggest_id", methods=["GET"])
def suggest_id():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    # 讀取 CSV 文件
    df = pd.read_csv(CSV_FILE_PATH)
    df = df.fillna("NaN")

    # 根據身分證或護照號碼進行模糊配對，忽略大小寫
    matches = df[
        df["personal_number"].str.contains(query, case=False, na=False) |
        df["passport_number"].str.contains(query, case=False, na=False)
    ]

    # 回傳最多 10 個搜尋記錄
    suggestions = matches.head(10).to_dict(orient="records")
    return jsonify(suggestions)

@app_admin.route("/suggest_trip", methods=["GET"])
def suggest_trip():
    # 從前端獲取查詢參數
    query = request.args.get("query", "").strip()

    # 如果沒有查詢條件，直接返回空的建議
    if not query:
        return jsonify([])

    # 讀取 CSV 文件
    try:
        df = pd.read_csv(TRIP_FILE_PATH)
        df = df.fillna("NaN")

    except Exception as e:
        return jsonify({"error": f"Error reading the CSV file: {e}"}), 500

    # 針對 'name' 欄位進行模糊搜尋，忽略大小寫
    matches = df[df["name"].str.contains(query, case=False, na=False)]

    # 回傳最多 10 個搜尋記錄
    suggestions = matches.head(10).to_dict(orient="records")

    return jsonify(suggestions)

@app_admin.route("/submit_passport",methods=["POST"])
def submit_passport():
    try:
        # 接收 JSON 資料
        user_info = request.get_json()
        if not user_info:
            return jsonify({"success": False, "error": "No data received"}), 400

        # 確保所有必要欄位都有值
        required_fields = [
            "personal_number", "name", "surname", "sex", "date_of_birth", "nationality",
            "passport_type", "passport_number", "issuing_country",
            "expiration_date"
        ]
        for field in required_fields:
            if field not in user_info:
                return jsonify({"success": False, "error": f"Missing field: {field}"}), 400

        # 儲存到 CSV 檔案
        save_user_info(user_info)   

        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

def save_user_info(user_info):
    # 讀取現有的資料
    existing_data = []
    personal_number = user_info.get("personal_number")
    passport_number = user_info.get("passport_number")

    # 如果沒有 personal_number，就使用 passport_number
    if not personal_number:  
        if not passport_number:
            return jsonify({"success": False, "error": "No passport number"}), 400 # 沒有護照號碼
        else:
            personal_number = passport_number

    # 讀取 CSV 並檢查是否有相同的 passport_number
    with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        existing_data = list(csv_reader)

    # Flag to check if the passport_number is found
    updated = False

    # 檢查是否已經存在相同的 passport_number
    for i, row in enumerate(existing_data):
        if row and row[0] == personal_number:  # 假設 passport_number 是第 6 欄（索引 5）
            # 覆寫資料
            existing_data[i] = [
                personal_number,
                user_info.get("name", ""),
                user_info.get("surname", ""),
                user_info.get("sex", ""),
                user_info.get("date_of_birth", ""),
                user_info.get("nationality", ""),
                user_info.get("passport_type", ""),
                passport_number,
                user_info.get("issuing_country", ""),
                user_info.get("expiration_date", ""),
            ]
            updated = True
            break  # 找到後就退出迴圈

    # 如果沒有更新資料，就新增一筆資料
    if not updated:
        existing_data.append([
                personal_number,
                user_info.get("name", ""),
                user_info.get("surname", ""),
                user_info.get("sex", ""),
                user_info.get("date_of_birth", ""),
                user_info.get("nationality", ""),
                user_info.get("passport_type", ""),
                passport_number,
                user_info.get("issuing_country", ""),
                user_info.get("expiration_date", ""),
        ])

    # 寫回 CSV 檔案
    with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(existing_data)

# 新增行程的接口
@app_admin.route("/add_trip", methods=["POST"])
def add_trip():
    new_trip = request.get_json()

    # 提取客戶的身分證字號
    participants_list = [
        participant['personalNumber']
        for participant in new_trip.get("participants", [])
        if "personalNumber" in participant
    ]

    # 讀取現有的 CSV 資料
    df = pd.read_csv(TRIP_FILE_PATH)

    # 檢查是否有重複行程名稱
    existing_trip = df[df["name"] == new_trip["name"]]

    if not existing_trip.empty:
        # 如果行程名稱存在，更新該行程
        df.loc[df["name"] == new_trip["name"], ["destination", "startDate", "participants"]] = [
            new_trip["destination"],
            new_trip["startDate"],
            ";".join(participants_list)
        ]
        message = "行程已更新！"
    else:
        # 設置新的行程 ID
        new_trip["id"] = len(df) + 1

        # 新行程的資料
        new_trip_data = pd.DataFrame([{
            "id": new_trip["id"],
            "name": new_trip["name"],
            "destination": new_trip["destination"],
            "startDate": new_trip["startDate"],
            "participants": ";".join(participants_list)
        }])

        # 使用 concat() 合併新行程資料
        df = pd.concat([df, new_trip_data], ignore_index=True)
        message = "行程已創建！"

    # 將資料寫回 CSV 檔案
    df.to_csv(TRIP_FILE_PATH, index=False, encoding='utf-8')

    return jsonify({"message": message, "trip": new_trip}), 200

# @app_admin.route("/search", methods=["GET"])
# def search():
#     passport_number = request.args.get("passport_number")
#     if passport_number:
#         try:
#             # 讀取 Excel 文件
#             df = pd.read_csv(EXCEL_FILE_PATH)
#             df = df.fillna("NaN")

#             # 查找符合身分證號的用戶資料
#             user = df[df['passport_number'] == passport_number].iloc[0]

#             # 返回查詢結果
#             result = {
#                 "name": user["name"],
#                 "surname": user["surname"],
#                 "sex": user["sex"],
#                 "date_of_birth": user["date_of_birth"],
#                 "nationality": user["nationality"],
#                 "passport_type": user["passport_type"],
#                 "passport_number": user["passport_number"],
#                 "issuing_country": user["issuing_country"],
#                 "expiration_date": user["expiration_date"],
#                 "personal_number": user["personal_number"]
#             }
#             return jsonify(result)
#         except IndexError:
#             return jsonify({"error": "No data found"}), 404
#     return jsonify({"error": "Passport number is required"}), 400

@app_admin.route("/get_client", methods=["GET"])
def get_client():
    personal_number = request.args.get("personal_number")

    if not personal_number:
        return jsonify({"error": "Personal number is required"}), 400

    try:
        # 讀取旅客資料
        df = pd.read_csv(CSV_FILE_PATH)
        traveler = df[df["personal_number"] == personal_number].iloc[0]
        # print(df.columns)

        # 回傳旅客資訊
        return jsonify({
            "personal_number": traveler["personal_number"],
            "name": traveler["name"],
            "surname": traveler["surname"],
            "sex": traveler["sex"],
            "date_of_birth": traveler["date_of_birth"],
            "nationality": traveler["nationality"],
            "passport_type": traveler["passport_type"],
            "passport_number": traveler["passport_number"],
            "issuing_country": traveler["issuing_country"],
            "expiration_date": traveler["expiration_date"],
        }), 200
    except IndexError:
        return jsonify({"error": "No traveler found"}), 404

# export
# 匯出所有的客戶資料
@app_admin.route("/export_csv")
def export_csv():
    # 讀取 Excel 文件
    df = pd.read_csv(CSV_FILE_PATH)

    # 創建 BytesIO 物件
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)  # 重設指標，準備發送

    # 返回 CSV 文件
    return send_file(output, mimetype='text/csv', download_name="users_data.csv", as_attachment=True)

# 匯出此行程的旅客資料
@app_admin.route("/export_trip/<trip_name>", methods=["GET"])
def export_trip(trip_name):
    try:
        # 讀取行程資料
        trips_df = pd.read_csv(TRIP_FILE_PATH)
        trip = trips_df[trips_df["name"] == trip_name]

        if trip.empty:
            return jsonify({"error": "Trip not found"}), 404

        # 獲取參與者的身分證號
        participants = trip.iloc[0]["participants"].split(";")

        # 讀取旅客資料
        travelers_df = pd.read_csv(CSV_FILE_PATH)

        # 篩選出參與者的完整資料
        exported_travelers = travelers_df[travelers_df["personal_number"].isin(participants)][
            ["name", "surname", "sex", "personal_number", "passport_number"]
        ]

        # 設置檔案名稱
        csv_filename = f"{trip_name}.csv"

        # 將資料寫入 BytesIO 物件（記憶體中的檔案）
        output = BytesIO()
        exported_travelers.to_csv(output, index=False, encoding="utf-8")
        output.seek(0)  # 重置檔案指標

        # 返回 CSV 文件
        return send_file(output, as_attachment=True, download_name=csv_filename, mimetype="text/csv")

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app_admin.run(port=8001, debug=True)
