from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('<h1 style="font-weight:bold;">This will be the blog index</h1> <p>work in progress</p>')


