# train_and_save.py
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
RATINGS_CSV = DATA_DIR / "ratings.csv"
ITEMS_CSV = DATA_DIR / "items.csv"
MODEL_PATH = MODEL_DIR / "item_sim.pkl"

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("train_and_save")


def load_data():
    """
    Load ratings.csv and items.csv. Return ratings_df and items_df.
    """
    if not RATINGS_CSV.exists():
        logger.warning("Ratings file not found at %s. Returning empty DataFrame.", RATINGS_CSV)
        ratings_df = pd.DataFrame(columns=["user_id", "item_id", "rating"])
    else:
        ratings_df = pd.read_csv(RATINGS_CSV)

    if not ITEMS_CSV.exists():
        logger.warning("Items file not found at %s. Returning empty DataFrame.", ITEMS_CSV)
        items_df = pd.DataFrame(columns=["item_id", "title", "description", "image"])
    else:
        items_df = pd.read_csv(ITEMS_CSV)

    return ratings_df, items_df


def build_user_item_matrix(ratings_df):
    """
    Build a user-item matrix (users x items) from ratings_df.
    Missing values -> 0.
    Returns pivot dataframe and list of item ids in column order.
    """
    if ratings_df.empty:
        logger.info("Ratings dataframe is empty. Returning empty matrix.")
        return pd.DataFrame(), []

    # Ensure the expected columns exist
    expected_cols = {"user_id", "item_id", "rating"}
    if not expected_cols.issubset(set(ratings_df.columns)):
        raise ValueError(f"ratings.csv must contain columns: {expected_cols}")

    # Use string item ids to stay consistent with app
    ratings_df = ratings_df.copy()
    ratings_df["item_id"] = ratings_df["item_id"].astype(str)
    ratings_df["user_id"] = ratings_df["user_id"].astype(str)

    # pivot: rows = users, cols = item_ids
    user_item = ratings_df.pivot_table(index="user_id", columns="item_id", values="rating", aggfunc="mean", fill_value=0)

    logger.info("Created user-item matrix with shape: %s", user_item.shape)
    item_ids = list(user_item.columns.astype(str))
    return user_item, item_ids


def compute_item_similarity(user_item_df, item_ids):
    """
    Compute item-item cosine similarity.
    Returns a dict: { item_id: {other_item_id: score, ...}, ... }
    """
    if user_item_df.empty or len(item_ids) == 0:
        logger.info("No user-item data to compute similarity. Returning empty dict.")
        return {}

    # Transpose -> rows are items, columns are users
    item_matrix = user_item_df.T.values  # shape (n_items, n_users)

    # If an item has zero-vector, cosine_similarity may produce nan; guard with small epsilon or handle afterwards.
    # compute cosine similarity (n_items x n_items)
    sim = cosine_similarity(item_matrix)  # returns float64 matrix

    # Clamp numerical noise and convert to python floats
    sim = np.nan_to_num(sim, nan=0.0, posinf=0.0, neginf=0.0)

    item_sim_dict = {}
    n_items = len(item_ids)
    for i, iid in enumerate(item_ids):
        sims = {}
        for j in range(n_items):
            if i == j:
                continue  # skip self
            other_id = item_ids[j]
            score = float(sim[i, j])
            # Optionally skip 0-scores
            if score != 0.0:
                sims[str(other_id)] = score
        # sort sims by score descending (optional)
        sorted_sims = dict(sorted(sims.items(), key=lambda kv: -kv[1]))
        item_sim_dict[str(iid)] = sorted_sims

    logger.info("Item similarity matrix built.")
    return item_sim_dict


def save_model(model_obj, path: Path):
    """
    Save the model object using joblib.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_obj, str(path))
    logger.info("Model saved at: %s", path)


def main():
    logger.info("Starting training process...")
    ratings_df, items_df = load_data()
    logger.info("Loaded data shapes -> ratings: %s, items: %s", getattr(ratings_df, "shape", None), getattr(items_df, "shape", None))

    user_item_df, item_ids = build_user_item_matrix(ratings_df)

    if len(item_ids) == 0:
        # No ratings: create trivial similarity map (maybe based on available items.csv)
        if not items_df.empty:
            available_item_ids = [str(i) for i in items_df["item_id"].tolist()]
            logger.info("No rating-based items found. Building empty similarity maps for items from items.csv.")
            item_sim = {iid: {} for iid in available_item_ids}
        else:
            logger.info("No items found in items.csv either. Saving empty model.")
            item_sim = {}
    else:
        item_sim = compute_item_similarity(user_item_df, item_ids)

    save_model(item_sim, MODEL_PATH)
    logger.info("🎯 Training complete!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Training failed: %s", e)
        raise