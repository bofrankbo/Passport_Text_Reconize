from flask import Flask, jsonify
from azure.storage.blob import BlobServiceClient, ContainerClient
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging
import atexit

# Flask 應用設定
app = Flask(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Azure Blob Storage 設定
connection_string = "DefaultEndpointsProtocol=https;AccountName=testtravelagencystorage;AccountKey=hBF812iA3tmC6MWeHoHvVTD49pLqqFPdjhvbM1PMjw+ZakE/bQH3/9Eppm2qUWudsqU2CCwgs4cw+AStRpKHHQ==;EndpointSuffix=core.windows.net"
container_name = "data"
local_excel_path = "data/data.xlsx"

# 初始化 BlobServiceClient 和 ContainerClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

def upload_excel_to_blob():
    """上傳本地 Excel 檔案到 Azure Blob Storage"""
    logging.info("Uploading Excel file to Azure Blob Storage...")
    try:
        now = datetime.now()
        blob_name = f"excel_backup_{now.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        blob_client = container_client.get_blob_client(blob_name)

        # 上傳檔案
        with open(local_excel_path, "rb") as data:
            data = data.read()
            print(data)
            blob_client.upload_blob(data, overwrite=True)

        logging.info(f"Excel file {blob_name} uploaded successfully.")
    except Exception as e:
        logging.error(f"Error uploading file: {e}")

def clean_old_files():
    """清理 Azure Blob Storage 中過舊的檔案，只保留一天內的檔案"""
    try:
        retention_days = 1
        cutoff_time = datetime.now() - timedelta(days=retention_days)

        blobs = container_client.list_blobs()
        for blob in blobs:
            blob_last_modified = blob.last_modified.replace(tzinfo=None)
            if blob_last_modified < cutoff_time:
                container_client.delete_blob(blob.name)
                logging.info(f"Deleted old file: {blob.name}")
    except Exception as e:
        logging.error(f"Error cleaning old files: {e}")

def scheduled_task():
    """定時任務：上傳檔案並清理舊檔案"""
    logging.info("Running scheduled task...")
    upload_excel_to_blob()
    clean_old_files()

# 停止程式時，確保 Scheduler 正確關閉
def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("Scheduler shut down successfully.")

from flask import Flask, jsonify, request
import logging
import atexit

app = Flask(__name__)

# 初始化定時任務
scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", hours=3)
try:
    scheduler.start()
    logging.info("Scheduler started successfully.")
except Exception as e:
    logging.error(f"Error starting Scheduler: {e}")

# 停止程式時，確保 Scheduler 正確關閉
def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("Scheduler shut down successfully.")

# 註冊應用關閉時調用的函數
atexit.register(shutdown_scheduler)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Flask and Azure Blob Storage integration!"})

@app.route("/upload", methods=["GET"])
def upload_now():
    """手動觸發上傳"""
    logging.info("Manual file upload triggered.")
    upload_excel_to_blob()
    return jsonify({"message": "File uploaded manually."})

@app.route("/clean", methods=["GET"])
def clean_now():
    """手動觸發清理"""
    clean_old_files()
    return jsonify({"message": "Old files cleaned manually."})

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Flask app with scheduled tasks...")
    app.run(host="0.0.0.0", debug=True)