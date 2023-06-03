from django_filters import rest_framework as filters
from blog.models import Post, Comment

class PostFilter(filters.FilterSet):
    user = filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    safe = filters.BooleanFilter(field_name='safe')
    created_at_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    orderings = filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('safe', 'safe'),
        )
    )

    class Meta:
        model = Post
        fields = ['user', 'safe','created_at_after','created_at_before']


class CommentFilter(filters.FilterSet):
    created_at_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Comment
        fields = ['created_at_after','created_at_before']

