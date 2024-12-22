'''
    定時備份檔案到 Azure Blob Storage
'''

from apscheduler.schedulers.background import BackgroundScheduler
import logging
import atexit
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient
import os
import shutil
from modules.config import DATA_FOLDER, connection_string, container_name
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化 BlobServiceClient 和 ContainerClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

def upload_to_blob():
    """壓縮並上傳本地 data 資料夾到 Azure Blob Storage"""
    logging.info("Compressing and uploading data folder to Azure Blob Storage...")
    try:
        now = datetime.now()
        zip_filename = f"data_backup_{now.strftime('%Y-%m-%d_%H-%M-%S')}.zip"
        parent_folder = os.path.dirname(os.path.abspath(__file__))
        zip_filepath = os.path.join(f"{parent_folder}/tmp", zip_filename)

        # 壓縮 data 資料夾
        shutil.make_archive(zip_filepath.replace('.zip', ''), 'zip', DATA_FOLDER)

        # 上傳壓縮檔案
        blob_client = container_client.get_blob_client(zip_filename)
        with open(zip_filepath, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        logging.info(f"Compressed data folder uploaded successfully as {zip_filename}.")
        
        # 刪除本地壓縮檔案
        os.remove(zip_filepath)
    except Exception as e:
        logging.error(f"Error compressing and uploading data folder: {e}")


def clean_old_files():
    """清理 Azure Blob Storage 中過舊的檔案，只保留一天內的檔案，並且一天前的資料每24小時保留一份"""
    try:
        retention_days = 1
        cutoff_time = datetime.now() - timedelta(days=retention_days)

        blobs = container_client.list_blobs()
        blobs_to_delete = []
        last_kept_blob = None

        for blob in blobs:
            blob_last_modified = blob.last_modified.replace(tzinfo=None)
            if blob_last_modified < cutoff_time:
                if last_kept_blob is None or (blob_last_modified - last_kept_blob).total_seconds() >= 86400:
                    last_kept_blob = blob_last_modified
                else:
                    blobs_to_delete.append(blob.name)
            else:
                last_kept_blob = blob_last_modified

        for blob_name in blobs_to_delete:
            container_client.delete_blob(blob_name)
            logging.info(f"Deleted old file: {blob_name}")

    except Exception as e:
        logging.error(f"Error cleaning old files: {e}")

def scheduled_task():
    """定時任務：上傳檔案並清理舊檔案"""
    logging.info("Running scheduled task...")
    upload_to_blob()
    clean_old_files()

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