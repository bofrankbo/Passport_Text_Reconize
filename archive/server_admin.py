# 有用到 mysql 的檔案
# 實作希望用excel檔案來儲存資料，所以暫時封存


"""
Readme.md
6. 安裝 mysql 創建一個database
    ```CREATE DATABASE passport_db;
    USE passport_db;

    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50),
        surname VARCHAR(50),
        sex VARCHAR(10),
        date_of_birth DATE,
        nationality VARCHAR(50),
        passport_type VARCHAR(10),
        passport_number VARCHAR(20),
        issuing_country VARCHAR(50),
        expiration_date DATE,
        personal_number VARCHAR(20)
    );```
"""

from flask import Flask, render_template, request, jsonify, send_file
import mysql.connector  # 使用 mysql-connector-python 來連接 MySQL

import mysql.connector
import pandas as pd
from io import BytesIO
import numpy as np

app_admin = Flask(__name__)

# MySQL 連線設置
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="passport_db"
)
cursor = db.cursor()

@app_admin.route("/admin.html")
def admin():
    return render_template("admin.html")

@app_admin.route("/")
def root():
    return render_template("admin.html")

@app_admin.route('/records', methods=['GET'])
def get_recognition_records():
    try:
        # 查詢所有辨識記錄
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        # 將結果轉為 JSON 格式
        records = []
        for row in rows:
            records.append({
                "id": row[0],
                "name": row[1],
                "surname": row[2],
                "sex": row[3],
                "date_of_birth": row[4].strftime('%Y-%m-%d'),
                "nationality": row[5],
                "passport_type": row[6],
                "passport_number": row[7],
                "issuing_country": row[8],
                "expiration_date": row[9].strftime('%Y-%m-%d'),
                "personal_number": row[10]
            })
        print(records)
        return jsonify(records), 200

    except Exception as e:
        print(f"Error fetching records: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@app_admin.route("/search", methods=["GET"])
def search():
    personal_number = request.args.get("personal_number")
    
    if personal_number:
        cursor.execute("SELECT * FROM users WHERE personal_number = %s", (personal_number,))
        user = cursor.fetchone()
        
        if user:
            # 將查詢結果轉為字典返回
            result = {
                "name": user[1],
                "surname": user[2],
                "sex": user[3],
                "date_of_birth": user[4].strftime('%Y-%m-%d'),
                "nationality": user[5],
                "passport_type": user[6],
                "passport_number": user[7],
                "issuing_country": user[8],
                "expiration_date": user[9].strftime('%Y-%m-%d'),
                "personal_number": user[10]
            }
            return jsonify(result)
        else:
            return jsonify({"error": "No data found"}), 404
    return jsonify({"error": "Personal number is required"}), 400

@app_admin.route("/export_csv")
def export_csv():
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    # 創建 DataFrame
    df = pd.DataFrame(rows, columns=["id", "name", "surname", "sex", "date_of_birth", 
                                     "nationality", "passport_type", "passport_number", 
                                     "issuing_country", "expiration_date", "personal_number"])

    # 將資料轉換為 CSV 格式並轉換為二進制流
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)  # 將指標回到開頭，準備發送給客戶端

    # 返回 CSV 文件，並使用二進制格式
    return send_file(output, mimetype='text/csv', download_name="users_data.csv", as_attachment=True)

if __name__ == '__main__':
    app_admin.run(port=8001)
