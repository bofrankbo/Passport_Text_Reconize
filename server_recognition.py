from flask import Flask, render_template, request, jsonify , Response, stream_with_context

import os
import time
import random
import json
import textwrap
import math
import csv
from IPython.display import display, Markdown
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

from ocr_passport import OCRPassport

current_file_path = os.path.abspath(__file__)
print(f"Current file path: {current_file_path}")

app = Flask(__name__)

# 確保資料夾存在
UPLOAD_FOLDER = "upload_images"
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "user_data.csv")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CSV_FILE_PATH):
    # 初始化 CSV 檔案，確保有標題行
    with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "name", "surname", "sex", "date_of_birth", "nationality",
            "passport_type", "passport_number", "issuing_country",
            "expiration_date", "personal_number"
        ])

@app.route("/model.html")
def model():
    return render_template("model.html")

@app.route("/predict.html")
def predict():
    return render_template("predict.html")

@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/contact.html")
def contact():
    return render_template("contact.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/process_passport",methods=["POST"])
def process_passport():
    print("process_passport")
    # 檢查是否有上傳圖片
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image file found"}), 400

    image_file = request.files['image']

    # 保存圖片到伺服器
    file_path = os.path.join("upload_images/", image_file.filename)
    image_file.save(file_path)

    # 在此處進行辨識（替換成你的 OCR 邏輯）
    # 初始化 OCR 類別（若需要指定 Tesseract 路徑可傳入 tesseract_cmd）
    ocr_passport = OCRPassport(tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    print("ocr_passport", file_path)
    user_info = ocr_passport.get_data(file_path)
    print("user_info", user_info)
    # text_passport = format_user_info(user_info)

    # 返回辨識結果
    return jsonify({"success": True, "result": user_info})

@app.route("/submit_passport",methods=["POST"])
def submit_passport():
    try:
        # 接收 JSON 資料
        user_info = request.get_json()
        if not user_info:
            return jsonify({"success": False, "error": "No data received"}), 400

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

        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == '__main__':
    #定義app在8080埠運行
    app.run(host="0.0.0.0",port=8000,debug=True)
    


