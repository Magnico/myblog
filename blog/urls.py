from django.conf.urls import include
from rest_framework import routers
from django.urls import path
from . import views



app_name = 'blog'

router = routers.DefaultRouter()
router.register(r'api/post', views.PostViewSet, basename='post')
router.register(r'api/comment', views.CommentViewSet, basename='comment')
router.register(r'api/usertag', views.UserTagViewSet, basename='usertag')
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
    #/blog/api/comment
    path('', include(router.urls)),

]