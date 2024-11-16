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

@app.route("/crawl.html")
def crawl():
    return render_template("crawl.html")

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

    text_passport = (
        f"Name: {user_info['name']}, "
        f"Surname: {user_info['surname']}, "
        f"Sex: {user_info['sex']}, "
        f"Date of Birth: {user_info['date_of_birth']}, "
        f"Nationality: {user_info['nationality']}, "
        f"Passport Type: {user_info['passport_type']}"
    )

    # 返回辨識結果
    return jsonify({"success": True, "result": text_passport})
    
if __name__ == '__main__':
    #定義app在8080埠運行
    app.run(host="0.0.0.0",port=8000,debug=True)
    


