import os
import pytz

# Azure Blob Storage 設定
azure_blob_connection_string = "DefaultEndpointsProtocol=https;AccountName=testtravelagencystorage;AccountKey=hBF812iA3tmC6MWeHoHvVTD49pLqqFPdjhvbM1PMjw+ZakE/bQH3/9Eppm2qUWudsqU2CCwgs4cw+AStRpKHHQ==;EndpointSuffix=core.windows.net"
azure_blob_container_name = "data"

# Azure form rec 設定
azure_formrec_key = "EhGrb10wo83t9y6EZfbtaMSmSwyOqwkiw3UiiGVnG6EmvLTQ56ScJQQJ99ALACYeBjFXJ3w3AAALACOGSL9B"
azure_formrec_endpoint = "https://testtravelagencyformrec.cognitiveservices.azure.com/"


# CSV 檔案路徑
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/clients_data.csv")
TRIP_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/trip_data.csv")
IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/upload_images")
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

# 設定當地時區，例如 'Asia/Taipei'
local_tz = pytz.timezone('Asia/Taipei')