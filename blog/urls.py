from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    #/blog/
    path("", views.index, name='index'),
    #/blog/signup
    path("signup", views.signUp, name='signup'),
    #/blog/login
    path("login", views.MyLoginView.as_view(), name='login'),
    #/blog/logout
    path("logout", views.logOut, name='logout'),
    #/blog/api/post
    path("api/post", views.PostViewSet.as_view(), name='post_list'),
    #/blog/api/post/<int:pk>
    path("api/post/<int:pk>", views.PostDetailViewSet.as_view(), name='post_detail'),
]