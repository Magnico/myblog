from blog.api.serializers import PostSerializer, CommentSerializer, CommentPostSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib import messages
from .models import Post, Comment
from .forms import SignUpForm


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


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by('pk')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
                 
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all().order_by('pk')
    permission_classes = [IsAuthenticated]
                 
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentPostSerializer
        return CommentSerializer
    

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