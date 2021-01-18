from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
	user = models.CharField(max_length=64)
	title = models.CharField(max_length=64)
	price = models.FloatField()
	image_url = models.CharField(max_length=128)
	desc = models.TextField()
	active = models.BooleanField(default=True)
	category = models.CharField(max_length=64)

	def __str__(self):
		return f"Subject: {self.title}"


class Bid(models.Model):
	user = models.CharField(max_length=64)
	title = models.CharField(max_length=64)
	bid = models.FloatField()

	def __str__(self):
		return f"Bid: {self.bid} title: {self.title} user: {self.user}"

class Comment(models.Model):
	theme = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment")
	comment = models.TextField()
	user = models.CharField(max_length=64, default='potter')

	def __str__(self):
		return f"Comment: {self.comment}"

class Watchlist(models.Model):
	user = models.CharField(max_length=64)
	title = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watch")
	visibility = models.BooleanField(default=False)
	def __str__(self):
		return f"Title: {self.title} user: {self.user}"

class Categories(models.Model):
	title = models.CharField(max_length=64)

	def __str__(self):
		return f"Title: {self.title}"
