from django.shortcuts import render


def index(request):
    return render(request, "base1.html")
# Create your views here.
