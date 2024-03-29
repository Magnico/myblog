from blog.models import Post , Comment, UserTag
from django.contrib.auth.models import User
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    #user string related fields
    author = serializers.StringRelatedField()
    class Meta:
        model = Post
        fields = ['title','body','author','created_at','img','safe','comments_count',
                  'tagged_count','last_tag_date']

class RelatedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title','pk']

class CommentSerializer(serializers.ModelSerializer):
    #user string related fields
    author = serializers.StringRelatedField()
    post = RelatedPostSerializer()
    class Meta:
        model = Comment
        fields = ['body','author','post','created_at']

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['body','author','post']

class UserTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTag
        fields = ['user','post','created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email']