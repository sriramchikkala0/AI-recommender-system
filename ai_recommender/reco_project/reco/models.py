from django.db import models

class Item(models.Model):
    title = models.CharField(max_length=200)

    def _str_(self):
        return self.title

class Rating(models.Model):
    user_id = models.IntegerField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rating = models.FloatField()

    def _str_(self):
        return f"user:{self.user_id} item:{self.item_id} rating:{self.rating}"