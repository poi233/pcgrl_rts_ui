import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from gym_pcgrl.envs.helper import get_range_reward, get_tile_locations, \
    calc_num_regions, calc_certain_tile, run_dikjstra

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
        res[i]['origin'] = cal_map_stats(res[i]['map'], 8 if size == 'small' else 12)
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
    res["origin"]["map"] = [[int(sug_info["origin"]["map"][i][j]) for j in range(len(sug_info["origin"]["map"]))] for i in range(len(sug_info["origin"]["map"]))]
    res["origin"]["origin"] = cal_map_stats(res["origin"]["map"], 8 if size == 'small' else 12)
    for item in res:
        print(res[item])
        print("--------------------------------")
    return JsonResponse(json.dumps(res), safe=False)


def cal_map_stats(origin_map, width):
    tiles = ["empty", "base", "resource", "obstacle"]
    map = [["" for j in range(width)] for i in range(width)]
    for i in range(width):
        for j in range(width):
            map[i][j] = tiles[origin_map[i][j]]
    map_locations = get_tile_locations(map, tiles)
    map_stats = {
        "base_count": calc_certain_tile(map_locations, ["base"]),
        "resource_count": calc_certain_tile(map_locations, ["resource"]),
        "obstacle": calc_certain_tile(map_locations, ["obstacle"]),
        "base_distance": -500,
        "resource_distance": -500,
        "resource_balance": -500,
        "area_control": -500,
        "region": calc_num_regions(map, map_locations, ["empty", "base", "resource"])
    }
    if map_stats["base_count"] == 2:
        # general parameter
        b1_x, b1_y = map_locations["base"][0]
        b2_x, b2_y = map_locations["base"][1]
        dikjstra1, _ = run_dikjstra(b1_x, b1_y, map, ["empty", "base", "resource"])
        dikjstra2, _ = run_dikjstra(b2_x, b2_y, map, ["empty", "base", "resource"])
        # calculate distance
        map_stats["base_distance"] = abs(width / 2 - max(map_stats["base_distance"], dikjstra1[b2_y][b2_x]))
        map_stats["base_distance"] = abs(width / 2 - max(map_stats["base_distance"], dikjstra1[b2_y][b2_x]))
        # calculate resource distance
        resources = []
        resources.extend(map_locations["resource"])
        sum1 = 0
        sum2 = 0
        dist1 = 100000
        dist2 = 100000
        for r_x, r_y in resources:
            if dikjstra1[r_y][r_x] > 0:
                sum1 += dikjstra1[r_y][r_x]
                dist1 = min(dist1, dikjstra1[r_y][r_x])
            if dikjstra2[r_y][r_x] > 0:
                sum2 += dikjstra2[r_y][r_x]
                dist2 = min(dist2, dikjstra2[r_y][r_x])
        map_stats["resource_distance"] = int(abs(dist1 - dist2))
        map_stats["resource_balance"] = int(abs(sum1 - sum2))
        # calculate area control
        base1 = 0
        base2 = 0
        for x in range(width):
            for y in range(width):
                if dikjstra1[y][x] > dikjstra2[y][x]:
                    base2 += 1
                elif dikjstra1[y][x] < dikjstra2[y][x]:
                    base1 += 1
        map_stats["area_control"] = abs(base1 - base2)
    return map_stats

