"""
Run a trained agent and get generated maps
"""
import random

import numpy as np
from django.conf import settings
import random

import model
from utils import make_vec_envs


def infer(game, representation, model_path, **kwargs):
    """
     - max_trials: The number of trials per evaluation.
     - infer_kwargs: Args to pass to the environment.
    """
    env_name = '{}-{}-v0'.format(game, representation)
    if "small" in game:
        model.FullyConvPolicy = model.FullyConvPolicySmallMap
        kwargs['cropped_size'] = 8
    elif "medium" in game:
        model.FullyConvPolicy = model.FullyConvPolicySmallMap
        kwargs['cropped_size'] = 12
    elif "large" in game:
        model.FullyConvPolicy = model.FullyConvPolicyBigMap
        kwargs['cropped_size'] = 16

    kwargs['render'] = False
    # agent = PPO2.load(model_path)
    agent = getattr(settings, model_path, None)
    fixed_tiles = process(kwargs.get('tiles', []))
    initial_map = createMap(kwargs['cropped_size'], fixed_tiles)
    kwargs['old_map'] = initial_map
    change_limit = kwargs.get('change_limit', 5000)
    # if not canCreateMap(fixed_tiles, game.split("_")[0], game.split("_")[1]):
    #     return False
    sug_info = {}
    for i in range(kwargs.get('trials', 1)):
        sug_info[i] = {}
        env = make_vec_envs(env_name, representation, None, 1, **kwargs)
        info = None
        obs = env.reset()
        dones = False
        cur_pos = {'x': None, 'y': None}
        while not dones:
            if i == 0:
                action, _ = agent.predict(obs)
                obs, _, dones, info = env.step(action)
            else:
                obs, _, dones, info = step(cur_pos, fixed_tiles, representation, env, agent, obs)
            cur_pos['x'] = info[0]['pos'][0]
            cur_pos['y'] = info[0]['pos'][1]
            if kwargs.get('verbose', False):
                print(info[0])
            if dones:
                break
            # if info[0]['changes'] > change_limit:
            #     return False
        sug_info[i]["info"] = info[0]
    sug_info["range"] = get_range(game.split("_")[0], game.split("_")[1])
    return sug_info


def step(cur_pos, fixed_tiles, representation, env, agent, obs):
    action = None
    # change this tile or not
    will_change = random.randint(1, 100)
    if will_change < 20:
        action, _ = agent.predict(obs)
        obs, _, dones, info = env.step(action)
        return obs, _, dones, info
    # narrow
    if representation == 'narrow':
        if cur_pos['x'] is None:
            action = np.ndarray(shape=(1,))
            action[0] = 0
        elif isFixed(cur_pos, fixed_tiles):
            action = np.ndarray(shape=(1,))
            action[0] = fixed_tiles[(cur_pos['y'], cur_pos['x'])] + 1
        else:
            action, _ = agent.predict(obs)
    # turtle
    if representation == 'turtle':
        if cur_pos['x'] is None:
            action = np.ndarray(shape=(1,), dtype=np.int16)
            action[0] = int(random.randint(0, 3))
        elif isFixed(cur_pos, fixed_tiles):
            action = np.ndarray(shape=(1,), dtype=np.int16)
            action[0] = fixed_tiles[(cur_pos['y'], cur_pos['x'])] + 4
            env.step(action)
            action[0] = int(random.randint(0, 3))
        else:
            action, _ = agent.predict(obs)
    # wide
    if representation == 'wide':
        action, _ = agent.predict(obs)
        y, x, tile = np.unravel_index(action, (8, 8, 4))
        pos = {'x': x[0], 'y': y[0]}
        if isFixed(pos, fixed_tiles):
            action[0] -= tile[0]
            action[0] += fixed_tiles[(pos['y'], pos['x'])]
    # final step
    obs, _, dones, info = env.step(action)
    return obs, _, dones, info


def canCreateMap(fixed_tiles, size, style):
    base_count = 0
    resource_count = 0
    obstacle_count = 0
    for pos in fixed_tiles:
        if fixed_tiles[pos] == 1:
            base_count += 1
        elif fixed_tiles[pos] == 2:
            resource_count += 1
        elif fixed_tiles[pos] == 3:
            obstacle_count += 1
    if style == 'fair':
        return base_count <= 2 and resource_count <= 8 / 2 and obstacle_count <= 8
    else:
        return base_count <= 2 and resource_count <= 8 and obstacle_count <= 8 * 2


def isFixed(pos, fixed_tiles):
    return (pos['y'], pos['x']) in fixed_tiles


def process(tiles):
    all_tiles = tiles.split("|")
    res = {}
    for tile in all_tiles:
        if tile == "":
            break
        tmp = tile.split(",")
        res[(int(tmp[0]), int(tmp[1]))] = int(tmp[2])
    return res

def get_range(size, style):
    if size == "small":
        width = 8
    else:
        width = 12
    if style == "fair":
        times = 1
    else:
        times = 2
    tmp = dict()
    # values of indexes: 0-min possible value, 1-max possible value, 2-min optimal value, 3-max optimal value
    tmp["base_distance"] = [width * 3 / 8 - width * 2 + width / 2, width * 3 / 8, 0, width * 3 / 8]
    tmp["resource_count"] = [0, width * width - 2, width / 8, width / 2]
    tmp["resource_distance"] = [1 - width * 2, 1, 0, 1]
    tmp["resource_balance"] = [width / 4 - width * 2 * 4, width / 4, width / 4, width / 4]
    tmp["obstacle"] = [0, width * width, 0, width / 2 * 3]
    tmp["area_control"] = [width / 4 * 2 - width * width, width / 4 * 2, width / 4 * 2, width / 4 * 2]

    return tmp

def get_range_eval(val, input_pack):
    min_possible, max_possible, min_optimal, max_optimal = input_pack
    left = min_optimal - min_possible
    right = max_possible - max_optimal
    distance = max(left, right)
    evaluation = 0
    if val <= max_optimal and val >= min_optimal:
        evaluation = 100
    elif val < min_optimal:
        evaluation = (min_optimal - val) / distance
    elif val > max_optimal:
        evaluation = (val - max_optimal) / distance

    return evaluation

def createMap(size, fixed_tiles):
    initial_map = np.zeros((size, size), dtype=int)
    for item in fixed_tiles:
        initial_map[item[0]][item[1]] = fixed_tiles[item]
    return initial_map
################################## MAIN ########################################
# game = 'small_fair_rts'
# representation = 'narrow'
# model_path = '../static/models/{}/{}/model_1.pkl'.format(game, representation)
# # model_path = os.path.join(settings.BASE_DIR, model_name)
# kwargs = {
#     'change_percentage': 0.4,
#     'trials': 1,
#     'verbose': True
# }
#
# if __name__ == '__main__':
#     obs = infer(game, representation, model_path, **kwargs)
#     print(obs)
