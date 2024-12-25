import pandas as pd
from flask import jsonify, send_file
from .config import CSV_FILE_PATH, TRIP_FILE_PATH
import csv
from io import BytesIO


def save_client_info(request):
    print("Saving client info...")
    try:
        clients = request.get_json()
        if not clients:
            return jsonify({"success": False, "error": "No data received"}), 400

        existing_data = []
        with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            existing_data = list(csv_reader)

        for client in clients:
            required_fields = [
                "personal_number", "name", "surname", "sex", "date_of_birth", "nationality",
                "passport_number", "issuing_country",
                "expiration_date", "name_ch"
            ]
            for field in required_fields:
                if field not in client:
                    return jsonify({"success": False, "error": f"Missing field: {field} Client:{client}"}), 400

            personal_number = client.get("personal_number")
            passport_number = client.get("passport_number")

            # 如果沒有 personal_number，就使用 passport_number
            if personal_number == "":
                if passport_number == "":
                    return jsonify({"success": False, "error": "No passport number"}), 400
                else:
                    personal_number = passport_number

            updated = False
            # 檢查是否已經存在相同的 passport_number
            for i, row in enumerate(existing_data):
                if row and row[0] == personal_number:
                    print(f"Updating data for {personal_number}...")
                    # 覆寫資料
                    existing_data[i] = [
                        personal_number,
                        client.get("name", ""),
                        client.get("surname", ""),
                        client.get("sex", ""),
                        client.get("date_of_birth", ""),
                        client.get("nationality", ""),
                        passport_number,
                        client.get("issuing_country", ""),
                        client.get("expiration_date", ""),
                        client.get("name_ch", ""),
                    ]
                    updated = True
                    break  # 找到後就退出迴圈

            # 如果沒有更新資料，就新增一筆資料
            if not updated:
                print(f"Adding data for {personal_number}...")
                existing_data.append([
                    personal_number,
                    client.get("name", ""),
                    client.get("surname", ""),
                    client.get("sex", ""),
                    client.get("date_of_birth", ""),
                    client.get("nationality", ""),
                    passport_number,
                    client.get("issuing_country", ""),
                    client.get("expiration_date", ""),
                    client.get("name_ch", ""),
                ])

        # 寫回 CSV 檔案
        with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(existing_data)

        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


def get_client_data(request):
    personal_number = request.args.get("personal_number")
    df = pd.read_csv(CSV_FILE_PATH)

    # 回傳所有旅客資料
    if not personal_number:
        df = df.fillna("")
        return jsonify(df.to_dict(orient="records")), 200

    # 回傳特定旅客資料
    try:
        traveler = df[df["personal_number"] == personal_number].iloc[0]
        traveler = traveler.fillna("")

        return jsonify(traveler.to_dict()), 200
    except IndexError:
        return jsonify({"error": "Server can't find traveler"}), 404


def add_trip_data(request):
    new_trip = request.get_json()
    participants_list = [participant['personalNumber'] for participant in new_trip.get(
        "participants", []) if "personalNumber" in participant]
    df = pd.read_csv(TRIP_FILE_PATH)
    existing_trip = df[df["name"] == new_trip["name"]]

    if not existing_trip.empty:
        df.loc[df["name"] == new_trip["name"], ["destination", "startDate", "participants"]] = [
            new_trip["destination"],
            new_trip["startDate"],
            ";".join(participants_list)
        ]
        message = "行程已更新！"
    else:
        new_trip["id"] = len(df) + 1
        new_trip_data = pd.DataFrame([{
            "id": new_trip["id"],
            "name": new_trip["name"],
            "destination": new_trip["destination"],
            "startDate": new_trip["startDate"],
            "participants": ";".join(participants_list)
        }])
        df = pd.concat([df, new_trip_data], ignore_index=True)
        message = "行程已創建！"

    df.to_csv(TRIP_FILE_PATH, index=False, encoding='utf-8')
    return jsonify({"message": message, "trip": new_trip}), 200


def export_trip_data(trip_name):
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


def export_client_data():
    # 讀取 Excel 文件
    df = pd.read_csv(CSV_FILE_PATH)

    # 創建 BytesIO 物件
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)  # 重設指標，準備發送

    # 返回 CSV 文件
    return send_file(output, mimetype='text/csv', download_name="users_data.csv", as_attachment=True)


def import_client_data(request):
    if request.method == 'POST':
        if 'csvFile' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['csvFile']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(file)

                # 檢查是否包含所需的欄位
                required_columns = [
                    'personal_number', 'name', 'surname', 'sex', 'date_of_birth',
                    'nationality', 'passport_number',
                    'issuing_country', 'expiration_date', 'name_ch'
                ]

                if not all(column in df.columns for column in required_columns):
                    return jsonify({"error": "CSV file is missing required columns"}), 400

                df.to_csv(CSV_FILE_PATH, index=False, encoding='utf-8')

                return jsonify({"message": "File successfully uploaded and processed"}), 200

            except Exception as e:
                return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File Upload Failed"}), 400


def import_trip_data():
    pass
