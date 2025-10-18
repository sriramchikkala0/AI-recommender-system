# reco/utils/recommender.py
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# load once on import
_RATINGS_DF = None
_USER_ITEM = None
_SIM_MATRIX = None
_ITEM_INDEX = None

def load_data(ratings_path='reco/data/ratings.csv'):
    global _RATINGS_DF, _USER_ITEM, __SIM_MATRIX, _ITEM_INDEX
    _RATINGS_DF = pd.read_csv(ratings_path)
    # pivot to user-item matrix
    _USER_ITEM = _RATINGS_DF.pivot_table(index='user_id', columns='item_id', values='rating').fillna(0)
    _ITEM_INDEX = _USER_ITEM.columns
    # compute user-user similarity
    _SIM_MATRIX = pd.DataFrame(cosine_similarity(_USER_ITEM), index=_USER_ITEM.index, columns=_USER_ITEM.index)

def recommend_for_user_with_meta(user_id: int, top_n: int = 5):
    """
    Return a list of item_ids recommended for user_id.
    """
    global _RATINGS_DF, _USER_ITEM, _SIM_MATRIX, _ITEM_INDEX
    if _RATINGS_DF is None:
        load_data()  # load default path

    if user_id not in _USER_ITEM.index:
        # new user fallback: return most popular items
        popular = _RATINGS_DF.groupby('item_id')['rating'].mean().sort_values(ascending=False).head(top_n).index.tolist()
        return popular

    # similarity vector for this user
    sims = _SIM_MATRIX.loc[user_id]
    # weighted ratings: sum(similarity * rating_of_other_users)
    weighted = (_USER_ITEM.T * sims).T.sum(axis=0)  # result per item
    # remove items already rated by user
    rated_items = _RATINGS_DF[_RATINGS_DF['user_id'] == user_id]['item_id'].unique()
    weighted = weighted.drop(labels=rated_items, errors='ignore')
    # pick top N
    top_items = weighted.sort_values(ascending=False).head(top_n).index.tolist()
    return top_items