import csv
import os
from django.conf import settings
from .models import Item, Rating
from decimal import Decimal

ROOT = os.path.dirname(_file_)  # path to reco app folder

def load_sample_data():
    """Load items and ratings from reco/data/{items.csv,ratings_sample.csv}."""
    items_path = os.path.join(ROOT, "data", "items.csv")
    ratings_path = os.path.join(ROOT, "data", "ratings_sample.csv")

    # Create items
    if os.path.exists(items_path):
        with open(items_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_id = int(row["item_id"])
                title = row.get("title", "")
                image_url = row.get("image_url", "")
                Item.objects.update_or_create(
                    item_id=item_id,
                    defaults={"title": title, "image_url": image_url},
                )
    else:
        print(f"items.csv not found at: {items_path}")

    # Create ratings
    if os.path.exists(ratings_path):
        with open(ratings_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = int(row["user_id"])
                item_id = int(row["item_id"])
                rating = float(row["rating"])
                # assume Rating model has user_id (int), item (FK to Item or item_id), rating (float)
                # We'll try to link to an Item instance:
                try:
                    item = Item.objects.get(item_id=item_id)
                except Item.DoesNotExist:
                    # create minimal item if missing
                    item = Item.objects.create(item_id=item_id, title=f"Item {item_id}", image_url="")
                Rating.objects.update_or_create(
                    user_id=user_id,
                    item=item,
                    defaults={"rating": rating},
                )
    else:
        print(f"ratings_sample.csv not found at: {ratings_path}")

    print("Sample data loaded.")