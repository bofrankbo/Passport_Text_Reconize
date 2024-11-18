# Passport OCR (Optical Character Recognition)
Extract user data from a passport image.

Extracted info includes:
- Surname
- Name
- Sex
- Date of Birth
- Nationality
- Passport type
- Passport number
- issuing country
- Expiration date
- Personal number (Note:  Personal numbers aren't used in all country.)

## Set Up
This project requires python version 3.11.7  
To set up the project, follow these steps:
1. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```
2. 可能會有部分沒有裝到: opencv-python, PassportEye, easyocr
3. 必須安裝 Tesseract OCR， 且一定要照建議路徑安裝
4. Compile `app.py` to start the server for training and testing.
5. 執行的時候可能會有要修改 library 的 bug，改完之後應該就沒問題了
