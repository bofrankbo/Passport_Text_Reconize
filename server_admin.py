from flask import Flask, render_template, request, jsonify, send_file
import mysql.connector  # 使用 mysql-connector-python 來連接 MySQL

import mysql.connector
import pandas as pd
from io import BytesIO
import numpy as np
import os

app_admin = Flask(__name__)

# print(os.path.dirname(os.path.abspath(__file__)))
EXCEL_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "user_data.csv")

@app_admin.route("/admin.html")
def admin():
    return render_template("admin.html")

@app_admin.route("/")
def root():
    return render_template("admin.html")

# @app_admin.route('/records', methods=['GET'])
# def get_recognition_records():
#     try:
#         # 查詢所有辨識記錄
#         cursor.execute("SELECT * FROM users")
#         rows = cursor.fetchall()

#         # 將結果轉為 JSON 格式
#         records = []
#         for row in rows:
#             records.append({
#                 "id": row[0],
#                 "name": row[1],
#                 "surname": row[2],
#                 "sex": row[3],
#                 "date_of_birth": row[4].strftime('%Y-%m-%d'),
#                 "nationality": row[5],
#                 "passport_type": row[6],
#                 "passport_number": row[7],
#                 "issuing_country": row[8],
#                 "expiration_date": row[9].strftime('%Y-%m-%d'),
#                 "personal_number": row[10]
#             })
#         print(records)
#         return jsonify(records), 200

#     except Exception as e:
#         print(f"Error fetching records: {e}")
#         return jsonify({"success": False, "error": "Internal server error"}), 500



@app_admin.route("/search", methods=["GET"])
def search():
    personal_number = request.args.get("personal_number")
    
    if personal_number:
        try:
            # 讀取 Excel 文件
            df = pd.read_csv(EXCEL_FILE_PATH)

            # 查找符合身分證號的用戶資料
            user = df[df['personal_number'] == personal_number].iloc[0]

            # 返回查詢結果
            result = {
                "name": user["name"],
                "surname": user["surname"],
                "sex": user["sex"],
                "date_of_birth": user["date_of_birth"],
                "nationality": user["nationality"],
                "passport_type": user["passport_type"],
                "passport_number": user["passport_number"],
                "issuing_country": user["issuing_country"],
                "expiration_date": user["expiration_date"],
                "personal_number": user["personal_number"]
            }
            return jsonify(result)
        except IndexError:
            return jsonify({"error": "No data found"}), 404
    return jsonify({"error": "Personal number is required"}), 400

@app_admin.route("/export_csv")
def export_csv():
    # 讀取 Excel 文件
    df = pd.read_csv(EXCEL_FILE_PATH)

    # 創建 BytesIO 物件
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)  # 重設指標，準備發送

    # 返回 CSV 文件
    return send_file(output, mimetype='text/csv', download_name="users_data.csv", as_attachment=True)


if __name__ == '__main__':
    app_admin.run(port=8001)
