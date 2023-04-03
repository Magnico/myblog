from django.contrib.auth.models import User
from django.db import models

def get_upload_path(instance, filename):
    return 'uploads/images/{}/{}/{}/{}'.format(instance.created_at.year, instance.created_at.month, instance.created_at.day, filename)

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100,null=False,blank=False)
    body = models.CharField(max_length=255,null=False,blank=False)
    author = models.ForeignKey(User,on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True,editable=False)
    img = models.ImageField(upload_to=get_upload_path,null=True,blank=True)
    safe = models.BooleanField(default=True)

    @property
    def comments_count(self):
        return self.comment_set.count()

    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        #Delete the image when the post is deleted
        self.img.delete(save=False)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk:
            #Look for the original image
            original = Post.objects.get(pk=self.pk)
            #If the original image is different from the new one, delete the original image
            if original.img and original.img != self.img:
                original.img.delete(save=False)
        super().save(*args, **kwargs)

class Comment(models.Model):
    body = models.CharField(max_length=255,null=False,blank=False)
    author = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True,editable=False)

    def __str__(self):
        return self.body