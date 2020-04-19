from django.core.serializers import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from brush.inference import infer
import os
from django.conf import settings


def index(request):
    return render(request, 'brush/brush.html', {})

@csrf_exempt
def suggest(request):
    size = request.POST.get("size", "None")
    style = request.POST.get("style", "None")
    tiles = request.POST.get("tiles", "None")
    rep = request.POST.get("rep", "None")
    game = '%s_%s_rts' % (size, style)
    representation = rep
    model_path = ("%s_%s_%s" % (size, style, rep)).upper()
    kwargs = {
        'change_percentage': 0.4,
        'trials': 1,
        'verbose': False,
        'tiles': tiles
    }
    obs = infer(game, representation, model_path, **kwargs)
    print(obs)
    return JsonResponse("123", safe=False)