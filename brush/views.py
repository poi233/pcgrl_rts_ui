import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

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
        'tiles': tiles,
        'random_start': False
    }
    sug_info = infer(game, representation, model_path, **kwargs)
    # format output
    if not sug_info:
        return JsonResponse(False, safe=False)
    res = {}
    for i in range(4):
        res[i] = {}
        res[i]['map'] = [[int(np.argmax(item)) for item in row] for row in sug_info[i]["info"]["terminal_observation"]]
        res[i]['base_count'] = sug_info[i]["info"]["base_count"]
        res[i]['base_distance'] = sug_info[i]["info"]["base_distance"]
        res[i]['resource_count'] = sug_info[i]["info"]["resource_count"]
        res[i]['resource_distance'] = sug_info[i]["info"]["resource_distance"]
        res[i]['resource_balance'] = sug_info[i]["info"]["resource_balance"]
        res[i]['obstacle'] = sug_info[i]["info"]["obstacle"]
        res[i]['region'] = sug_info[i]["info"]["region"]
        res[i]['area_control'] = sug_info[i]["info"]["area_control"]
    res["range"] = sug_info["range"]
    res["origin"] = sug_info["origin"]
    for item in res:
        print(res[item])
        print("--------------------------------")
    return JsonResponse(json.dumps(res), safe=False)
