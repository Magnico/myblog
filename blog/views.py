from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from django.contrib.auth.views import LoginView
from blog.api.serializers import PostSerializer
from rest_framework.response import Response
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib import messages
from .forms import SignUpForm
from .models import Post


# Create your views here.
def index(request):
    return render(request, 'blog/base_index.html', {
        "posts": Post.objects.all().count(),
    })


class MyLoginView(LoginView):
    template_name = 'blog/base_form.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('blog:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actionText'] = 'Log In'
        return context


class PostViewSet(GenericAPIView, ListModelMixin, CreateModelMixin):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
                           
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

def signUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('blog:login')
        else:
            messages.error(request, 'Invalid registration data')
    form = SignUpForm()
    return render(request, 'blog/base_form.html', {'form': form, 'actionText': 'Sign Up'})

def logOut(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('blog:login')