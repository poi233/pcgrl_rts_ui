import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from brush.inference import infer


def index(request):
    return render(request, 'brush/brush.html', {})


@csrf_exempt
def suggest(request):
    # get input
    size = request.POST.get("size", "None")
    style = request.POST.get("style", "None")
    tiles = request.POST.get("tiles", "None")
    rep = request.POST.get("rep", "None")
    # call infer
    game = '%s_%s_rts' % (size, style)
    representation = rep
    model_path = ("%s_%s_%s" % (size, style, rep)).upper()
    kwargs = {
        'change_limit': 5000,
        'change_percentage': 0.4,
        'trials': 2,
        'verbose': True,
        'tiles': tiles
    }
    maps = infer(game, representation, model_path, **kwargs)
    # format output
    if not maps:
        return JsonResponse(False, safe=False)
    res = [[[int(np.argmax(item)) for item in row] for row in map] for map in maps]
    for item in res:
        for row in item:
            print(row)
        print("--------------------------------")
    return JsonResponse(res, safe=False)
