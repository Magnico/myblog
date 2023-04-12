from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100,null=False,blank=False)
    body = models.CharField(max_length=255,null=False,blank=False)
    author = models.ForeignKey(User,on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True,editable=False)
    img = models.ImageField(upload_to='uploads/images/%Y/%m/%d/',null=True,blank=True)
    safe = models.BooleanField(default=True)
    tagged_users = models.ManyToManyField(User, through='UserTag', related_name='tagged_users')

    @property
    def tagged_count(self):
        return self.tagged_users.count()
    
    @property
    def last_tag_date(self):
        return self.usertag_set.last().created_at if self.usertag_set.last() else None

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
    
class UserTag(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=False)
    post = models.ForeignKey(Post,on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True,editable=False)

    def __str__(self):
        return str(self.user.pk) + ' tagged to ' + str(self.post.pk)