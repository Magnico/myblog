from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import SignUpForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Post

# Create your views here.
def index(request):
    return render(request, 'blog/index.html', {
        "posts": Post.objects.all().count(),
    })

class MyLoginView(LoginView):
    template_name = 'blog/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('blog:index')





def signup(request):
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
    return render(request, 'blog/signup.html', {'form': form})

def login(request):
    return render(request, 'blog/login.html')

def menu(request):
    return render(request, 'blog/menu.html')