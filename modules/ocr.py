from flask import request, jsonify
import os
import csv
import io
from PIL import Image
from werkzeug.datastructures import FileStorage
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Azure Form Recognizer 設定
from .config import CSV_FILE_PATH, IMAGE_FOLDER, azure_formrec_endpoint, azure_formrec_key

if not os.path.exists(CSV_FILE_PATH):
    # 初始化 CSV 檔案，確保有標題行
    with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "personal_number", "name", "surname", "sex", "date_of_birth", "nationality",
            "passport_number", "issuing_country",
            "expiration_date"
        ])

def compress_image(image_file):
    image = Image.open(image_file)
    image = image.convert("RGB")  # 確保圖片是 RGB 格式
    output_io = io.BytesIO()
    quality = 95  # 初始壓縮品質
    max_size = 4 * 1024 * 1024  # 4MB

    while True:
        output_io = io.BytesIO()  # 每次壓縮迭代前重新創建 BytesIO 物件
        image.save(output_io, format='JPEG', quality=quality)
        size = output_io.tell()
        print(f"Compressing Size: {size}")
        if size <= max_size:
            break
        quality -= 5  # 每次減少5%的品質

    compressed_image_file = output_io.getvalue()
    compressed_size = len(compressed_image_file)
    print(f"Final compressed image size: {compressed_size} bytes")

    # 將壓縮後的圖片數據包裝回 FileStorage 物件中
    compressed_image_io = io.BytesIO(compressed_image_file)
    compressed_image_io.seek(0)
    compressed_image = FileStorage(stream=compressed_image_io, filename=image_file.filename, content_type=image_file.content_type)

    return compressed_image

# 圖片辨識
# MRZ 資料解析
# 儲存圖片到伺服器
def ocr_passport(request):
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image file found"}), 400

    client = DocumentAnalysisClient(
        azure_formrec_endpoint, AzureKeyCredential(azure_formrec_key))
    image_file = request.files['image']

    mrz = {}
    user_info = {}

    image_file = compress_image(image_file)

    try:
        poller = client.begin_analyze_document(
            "prebuilt-idDocument", document=image_file)
        result = poller.result()
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

    for document in result.documents:
        if document.fields.get("MachineReadableZone"):
            mrz = document.fields["MachineReadableZone"].value

    # # 檢查是否有 LastName 欄位，若無則使用 FirstName
    # if not mrz.get("LastName"):
    #     mrz['LastName'] = mrz['FirstName'].value

    user_info['name'] = mrz['FirstName'].value
    user_info['surname'] = mrz['LastName'].value
    user_info['sex'] = mrz['Sex'].value
    user_info['nationality'] = mrz['Nationality'].value
    user_info['passport_number'] = mrz['DocumentNumber'].value
    user_info['date_of_birth'] = mrz['DateOfBirth'].value.strftime('%Y-%m-%d')
    user_info['issuing_country'] = mrz['CountryRegion'].value
    user_info['expiration_date'] = mrz['DateOfExpiration'].value.strftime('%Y-%m-%d')

    mrz_content = document.fields["MachineReadableZone"].content
    mrz_content = mrz_content.replace(" ", "")
    mrz_content = mrz_content[45+28:45+42]
    personal_number = mrz_content.replace("<", "")
    user_info['personal_number'] = personal_number

    if personal_number == "":
        user_info['personal_number'] = user_info['passport_number']

    # 儲存圖片到伺服器
    image_file.seek(0)
    image_path = os.path.join(IMAGE_FOLDER, f"passport_{user_info['personal_number']}.{image_file.filename.split('.')[-1]}")
    image_file.save(image_path)

    return jsonify({"success": True, "result": user_info})