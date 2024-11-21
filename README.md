# Passport OCR (Optical Character Recognition)

## Project Overview
Passport OCR 是一個用於從護照影像中提取用戶資料的應用。該系統利用光學字符識別（OCR）技術來從護照照片中提取以下資訊：

- 姓氏 (Surname)
- 名字 (Name)
- 性別 (Sex)
- 出生日期 (Date of Birth)
- 國籍 (Nationality)
- 護照類型 (Passport type)
- 護照號碼 (Passport number)
- 發證國家 (Issuing country)
- 到期日 (Expiration date)
- 身分證號碼 (Personal number) — 注意：並非所有國家都有身分證號碼欄位。

此專案使用了 `PassportEye`、`EasyOCR` 和 `Tesseract` 等開源庫進行圖像處理和文字辨識。

## Set Up (安裝教學)

### 1. 安裝 Python 3.11.7
此專案需要使用 Python 版本 3.11.7。你可以使用以下命令確認已安裝正確版本：

```sh
python --version
```

### 2. 安裝所需 Python 套件
請使用 `requirements.txt` 安裝所有依賴的 Python 套件。執行以下命令：

```sh
pip install -r requirements.txt
```

### 3. 安裝額外的 Python 套件
有些套件可能未包含在 `requirements.txt` 中，需要手動安裝：

```sh
pip install opencv-python
pip install PassportEye
pip install easyocr
```

### 4. 安裝 Tesseract OCR
你需要安裝 Tesseract OCR，是此專案的核心工具之一。

#### 安裝步驟：
- 下載 Tesseract OCR：[下載頁面](https://github.com/tesseract-ocr/tesseract)
- 注意事項：
  - 安裝後起按照預設路徑安裝
  - 其他問題請參考 [官方安裝教學](https://github.com/tesseract-ocr/tesseract/wiki) 完成安裝。

### 5. 編譯並運行 `main.py`
完成上述步驟後，執行 `main.py` 來啟動使用者網頁以及後台網頁。

### 6. 處理 Library Bug（若有）
在執行過程中，可能會遇到一些與套件相容性有關的 bug。這時請根據錯誤訊息進行修正，通常是沒有安裝到的套件問題。

## 使用指南
啟動後會開啟兩個伺服器，一個是使用者的伺服器，另一個是後台管理伺服器

### 護照辨識
你可以將護照圖片上傳到後端，並使用 OCR 技術進行自動辨識。成功後，系統會返回以下資料：

- 姓名、性別、出生日期、護照號碼、發證國家等詳細資訊。

### 後台
- 搜尋使用者
- 所有人的資料可以匯出為 CSV 文件，便於進行資料分析或存檔。

---

## 參考資料
- 護照辨識技術介紹：[Passport OCR GitHub](https://github.com/tem-ctrl/passport_ocr)