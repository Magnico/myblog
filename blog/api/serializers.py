from rest_framework import serializers
from blog.models import Post


class PostSerializer(serializers.ModelSerializer):

    #user string related fields
    author = serializers.StringRelatedField()
    class Meta:
        model = Post
        fields = ['title','body','author']