from django.shortcuts import render

def index(request):
    return render(request, 'brush/brush.html', {})