import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from categorizer import categorize

app = Flask(__name__)

# Reject uploads bigger than 1 MB so a huge file can't freeze the server
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

# Only the React front end is allowed to call this API
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

REQUIRED_COLUMNS = {"description", "amount"}


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "File is too large (max 1 MB)."}), 413


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/categorize", methods=["POST"])
def categorize_transactions():
    # 1. Make sure a file was sent
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # 2. Only accept .csv files
    file = request.files["file"]
    if not file.filename or not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Please upload a .csv file"}), 400

    # 3. Read the CSV with pandas
    try:
        df = pd.read_csv(file)
    except Exception:
        return jsonify({"error": "Could not read the file as a CSV"}), 400

    # 4. Check the columns we need are there
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return jsonify({"error": f"Missing columns: {', '.join(sorted(missing))}"}), 400

    # 5. Clean the data: amounts must be numbers, skip rows missing either field
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["description", "amount"])

    # 6. Categorize using the existing categorizer
    df["category"] = df["description"].astype(str).apply(categorize)

    # 7. Total spending per category, biggest first
    totals = df.groupby("category")["amount"].sum().round(2).sort_values(ascending=False)

    return jsonify({
        "transactions": df.fillna("").to_dict(orient="records"),
        "category_totals": [
            {"category": category, "total": float(total)}
            for category, total in totals.items()
        ],
        "total_spent": round(float(df["amount"].sum()), 2),
    })


if __name__ == "__main__":
    # Debug mode is off unless you turn it on with FLASK_DEBUG=1
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="127.0.0.1", port=5000, debug=debug)