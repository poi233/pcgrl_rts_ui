from django.core.serializers import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'brush/brush.html', {})

@csrf_exempt
def suggest(request):
    size = request.POST.get("size", "None")
    style = request.POST.get("style", "None")
    tiles = request.POST.get("tiles", "None")
    print(size)
    return JsonResponse(size + "&" + style + "&" + tiles, safe=False)