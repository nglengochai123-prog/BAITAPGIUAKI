from django.shortcuts import render

# Create your views
def hso(request):
    return render(request, 'hso.html')