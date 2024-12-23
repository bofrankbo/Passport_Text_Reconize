import os
import pytz

# Azure Blob Storage 設定
connection_string = "DefaultEndpointsProtocol=https;AccountName=testtravelagencystorage;AccountKey=hBF812iA3tmC6MWeHoHvVTD49pLqqFPdjhvbM1PMjw+ZakE/bQH3/9Eppm2qUWudsqU2CCwgs4cw+AStRpKHHQ==;EndpointSuffix=core.windows.net"
container_name = "data"

# CSV 檔案路徑
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/clients_data.csv")
TRIP_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/trip_data.csv")
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

# 設定當地時區，例如 'Asia/Taipei'
local_tz = pytz.timezone('Asia/Taipei')