from rest_framework import serializers
from blog.models import Post , Comment


class PostSerializer(serializers.ModelSerializer):
    #user string related fields
    author = serializers.StringRelatedField()
    class Meta:
        model = Post
        fields = ['title','body','author','created_at','img','safe','comments_count']

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