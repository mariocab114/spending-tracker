from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from categorizer import categorize

app = Flask(__name__)
CORS(app)  # lets the React page (different port) call this API

REQUIRED_COLUMNS = {"description", "amount"}


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/categorize", methods=["POST"])
def categorize_transactions():
    # 1. Make sure a file was sent
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # 2. Read the CSV with pandas
    try:
        df = pd.read_csv(request.files["file"])
    except Exception:
        return jsonify({"error": "Could not read the file as a CSV"}), 400

    # 3. Check the columns we need are there
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return jsonify({"error": f"Missing columns: {', '.join(sorted(missing))}"}), 400

    # 4. Clean the data: amounts must be numbers, skip rows missing either field
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["description", "amount"])

    # 5. Categorize using your existing categorizer
    df["category"] = df["description"].astype(str).apply(categorize)

    # 6. Total spending per category, biggest first
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
    app.run(debug=True, port=5000)