from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100,null=False,blank=False)
    body = models.CharField(max_length=255,null=False,blank=False)
    author = models.ForeignKey(User,on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.title

class Comment(models.Model):
    body = models.CharField(max_length=255,null=False,blank=False)
    author = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.body