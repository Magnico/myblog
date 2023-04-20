from django_filters import rest_framework as filters
from blog.models import Post

class PostFilter(filters.FilterSet):
    user = filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    safe = filters.BooleanFilter(field_name='safe')

    class Meta:
        model = Post
        fields = ['user', 'safe']