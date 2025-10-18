import os
import json
import pickle
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(BASE_DIR, "models", "item_sim.pkl")
ITEMS_PATH = os.path.join(DATA_DIR, "items.csv")
RATINGS_PATH = os.path.join(DATA_DIR, "ratings.csv")

app = Flask(__name__)
CORS(app)
app.json.sort_keys = False # To prevent jsonify from sorting keys alphabetically
# === Load Items ===
def load_items():
    items = pd.read_csv(ITEMS_PATH)
    return items

# === Load Ratings ===
def load_ratings():
    if not os.path.exists(RATINGS_PATH):
        return pd.DataFrame(columns=["user_id", "item_id", "rating"])
    return pd.read_csv(RATINGS_PATH)

# === Save Ratings ===
def save_ratings(df):
    df.to_csv(RATINGS_PATH, index=False)

# === Load Model ===
def load_model():
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print("⚠ Model load failed:", e)
            return {}
    return {}

# === Build Item Similarity Model ===
def train_model():
    print("⚙ Training model...")
    ratings = load_ratings()
    if ratings.empty:
        return {}
    matrix = ratings.pivot_table(index="user_id", columns="item_id", values="rating").fillna(0)
    sim = cosine_similarity(matrix.T)
    item_sim = pd.DataFrame(sim, index=matrix.columns, columns=matrix.columns).to_dict()
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(item_sim, f)
    print("✅ Model trained and saved.")
    return item_sim

# === Globals ===
items_df = load_items()
ratings_df = load_ratings()
item_sim = load_model()

# === API Routes ===

@app.route("/items/<item_id>")
def get_item(item_id):
    match = items_df[items_df["item_id"].astype(str) == str(item_id)]
    if match.empty:
        return jsonify({"error": "item not found", "loaded_items": len(items_df)}), 404
    return jsonify(match.iloc[0].to_dict())

@app.route("/recommend/<user_id>")
def recommend(user_id):
    user_id = int(user_id)
    ratings = load_ratings()
    if user_id not in ratings["user_id"].unique():
        return jsonify({"user_id": user_id, "recommendations": []}), 200 # Return 200 for no recommendations

    # Find items rated by this user
    user_items = ratings[ratings["user_id"] == user_id]["item_id"].tolist()
    scores = {}
    for item in user_items:
        similar = item_sim.get(item, {})
        for other, score in similar.items():
            if str(other) != str(item): # Ensure item IDs are compared as strings
                scores[other] = scores.get(other, 0) + score

    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_items = [{"item_id": str(i), "score": float(s)} for i, s in sorted_items[:5]]
    return jsonify({"user_id": user_id, "recommendations": top_items})

@app.route("/rate", methods=["POST"])
def rate_item():
    data = request.get_json()
    user_id = int(data.get("user_id"))
    item_id = int(data.get("item_id"))
    rating = float(data.get("rating"))

    df = load_ratings()
    existing = df[(df["user_id"] == user_id) & (df["item_id"] == item_id)]
    if not existing.empty:
        df.loc[existing.index, "rating"] = rating
    else:
        df = pd.concat([df, pd.DataFrame([[user_id, item_id, rating]], columns=["user_id", "item_id", "rating"])])
    save_ratings(df.reset_index(drop=True)) # Reset index after concat
    return jsonify({"status": "ok"})

@app.route("/user/<user_id>/ratings")
def get_user_ratings(user_id):
    df = load_ratings()
    user_ratings = df[df["user_id"] == int(user_id)]
    return jsonify(user_ratings.to_dict(orient="records"))

@app.route("/train", methods=["POST", "GET"])
def trigger_training():
    global item_sim
    item_sim = train_model()
    return jsonify({"status": "trained", "items": len(item_sim)})

@app.route("/stats/items")
def item_stats():
    df = load_ratings()
    if df.empty:
        return jsonify([])
    stats = df.groupby("item_id")["rating"].count().reset_index(name="popularity")
    stats = stats.sort_values("popularity", ascending=False)
    data = [{"name": str(r.item_id), "value": int(r.popularity)} for r in stats.itertuples()]
    return jsonify(data)

@app.route("/")
def root():
    return jsonify({
        "routes": ["/items/<id>", "/recommend/<user_id>", "/rate", "/train", "/user/<id>/ratings", "/stats/items"]
    })

if __name__ == "__main__":
    print("🌠 Starting Flask API on http://127.0.0.1:5000")
    app.run(debug=True)