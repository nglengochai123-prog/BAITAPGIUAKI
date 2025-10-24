from django.shortcuts import render

# Create your views here.
import json
def index(request):
    return render(request, 'index.html')