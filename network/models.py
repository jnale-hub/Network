from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    name = models.CharField(max_length=25, blank=True)
    following = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="followers")
    picture = models.URLField(default="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png")


class Post(models.Model):
    content = models.CharField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Post by {self.author} | {self.date}"
