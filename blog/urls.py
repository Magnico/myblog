from django.urls import path
from rest_framework import routers
from . import views
from django.conf.urls import include



app_name = 'blog'

router = routers.DefaultRouter()
router.register(r'api/post', views.PostViewSet, basename='post')
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
    path('', include(router.urls)),
]