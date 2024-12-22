import pandas as pd
from flask import jsonify
from .config import CSV_FILE_PATH, TRIP_FILE_PATH

def suggest_id(request):
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    df = pd.read_csv(CSV_FILE_PATH)
    df = df.fillna("NaN")
    matches = df[
        df["personal_number"].str.contains(query, case=False, na=False) |
        df["passport_number"].str.contains(query, case=False, na=False)
    ]
    suggestions = matches.head(10).to_dict(orient="records")
    return jsonify(suggestions)

def suggest_trip(request):
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    try:
        df = pd.read_csv(TRIP_FILE_PATH)
        df = df.fillna("NaN")
    except Exception as e:
        return jsonify({"error": f"Error reading the CSV file: {e}"}), 500

    matches = df[df["name"].str.contains(query, case=False, na=False)]
    suggestions = matches.head(10).to_dict(orient="records")
    return jsonify(suggestions)