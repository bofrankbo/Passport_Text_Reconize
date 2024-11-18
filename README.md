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
2. Create a `.env` file and store `GOOGLE_API_KEY='your api key'` in it.
3. Compile `app.py` to start the server for training and testing.