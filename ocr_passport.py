# %% [markdown]
# <h3 style='font-weight: bold'>Import necesary packages</h3>

# %%
# %pip install matplotlib
# %pip install passporteye
# %pip install easyocr
# %pip install cv2


# %%
import os
import string as st
from dateutil import parser
import matplotlib.image as mpimg
import cv2
from passporteye import read_mrz
import json
import easyocr
import warnings
warnings.filterwarnings('ignore')

import pytesseract
from typing import Optional, Dict
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRPassport:
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        初始化 OCRPassport 類別，讀取必要資料並配置 OCR。
        """
        # if tesseract_cmd:
        #     os.environ["TESSDATA_PREFIX"] = tesseract_cmd
        # print("TESSDATA_PREFIX", os.environ["TESSDATA_PREFIX"])

        # 初始化 EasyOCR
        self.reader = easyocr.Reader(lang_list=['en'], gpu=False)  # 若有 GPU 可將 gpu 設為 True

        # 讀取國家代碼資料
        with open('country_codes.json', encoding='utf-8') as f:
            self.country_codes = json.load(f)

    def parse_date(self, string: str) -> str:
        """
        將字串轉換為日期格式。
        """
        try:
            date = parser.parse(string, yearfirst=True).date()
            return date.strftime('%d/%m/%Y')
        except Exception as e:
            print(f"日期解析失敗: {e}")
            return "Invalid Date"

    def clean(self, string: str) -> str:
        """
        清理字串並轉換為大寫。
        """
        return ''.join(i for i in string if i.isalnum()).upper()

    def get_country_name(self, country_code: str) -> str:
        """
        根據國家代碼查詢國家名稱。
        """
        for country in self.country_codes:
            if country['alpha-3'] == country_code:
                return country['name'].upper()
        return country_code

    def get_sex(self, code: str) -> str:
        """
        轉換性別代碼為字母。
        """
        if code in ['M', 'F']:
            return code.upper()
        return 'M' if code == '0' else 'F'

    def get_data(self, img_name: str) -> Dict[str, str]:
        """
        從護照圖片中提取資訊。
        """
        user_info = {}
        temp_image_path = 'tmp.png'

        try:
            # 讀取圖片並提取 MRZ（機器可讀區）
            mrz = read_mrz(img_name, save_roi=True)
            if mrz:
                # 儲存提取的 MRZ 圖片
                mpimg.imsave(temp_image_path, mrz.aux['roi'], cmap='gray')

                # 使用 OpenCV 調整圖片大小
                img = cv2.imread(temp_image_path)
                img = cv2.resize(img, (1110, 140))

                # 使用 EasyOCR 辨識文字
                allowlist = st.ascii_letters + st.digits + '< '
                code = self.reader.readtext(img, paragraph=False, detail=0, allowlist=allowlist)
                
                # 處理文字輸出
                a, b = code[0].upper(), code[1].upper()
                a = a.ljust(44, '<')  # 確保長度為 44
                b = b.ljust(44, '<')

                # 解析資料
                surname, names = a[5:44].split('<<', 1) if '<<' in a[5:44] else (a[5:44], '')
                user_info['name'] = names.replace('<', ' ').strip()
                user_info['surname'] = surname.replace('<', ' ').strip()
                user_info['sex'] = self.get_sex(self.clean(b[20]))
                user_info['date_of_birth'] = self.parse_date(b[13:19])
                user_info['nationality'] = self.get_country_name(self.clean(b[10:13]))
                user_info['passport_type'] = self.clean(a[:2])

                return user_info
            else:
                print("未能提取 MRZ 區域。")
                return {}

        except Exception as e:
            print(f"處理護照時發生錯誤: {e}")
            return {}
        finally:
            # 刪除臨時圖片
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    # %% [markdown]
    # <h3 style='font-weight: bold'>Examples</h3>

    # # %%
    # img_name = 'Handcam_Passport.jpg'
    # data = get_data(img_name)
    # print_data(data)

    # # %%
    # img_name = 'passport2.png'
    # data1 = get_data(img_name)
    # print_data(data1)

    # # %%
    # img_name = 'passport3.png'
    # data1 = get_data(img_name)
    # print_data(data1)