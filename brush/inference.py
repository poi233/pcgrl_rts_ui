"""
Run a trained agent and get generated maps
"""
from django.conf import settings

import model
from utils import make_vec_envs
import numpy as np


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
        model.FullyConvPolicy = model.FullyConvPolicyBigMap
        kwargs['cropped_size'] = 12
    elif "large" in game:
        model.FullyConvPolicy = model.FullyConvPolicyBigMap
        kwargs['cropped_size'] = 16

    kwargs['render'] = False
    # agent = PPO2.load(model_path)
    agent = getattr(settings, model_path, None)
    fixed_tiles = process(kwargs.get('tiles', []))
    if not canCreateMap(fixed_tiles, game.split("_")[0], game.split("_")[1]):
        return False
    res = []
    for i in range(kwargs.get('trials', 1)):
        env = make_vec_envs(env_name, representation, None, 1, **kwargs)
        info = None
        obs = env.reset()
        dones = False
        cur_pos = {'x': None, 'y': None}
        while not dones:
            action = get_action(cur_pos, fixed_tiles, representation)
            if action is None:
                action, _ = agent.predict(obs)
            obs, _, dones, info = env.step(action)
            cur_pos['x'] = info[0]['pos'][0]
            cur_pos['y'] = info[0]['pos'][1]
            # check_tiles(fixed_tiles, obs)
            if kwargs.get('verbose', False):
                print(info[0])
            if dones:
                break
            # if dones and satisfy_fixed_tiles(fixed_tiles):
            #     break
        res.append(info[0]['terminal_observation'])
        # time.sleep(0.2)
    return res


def get_action(cur_pos, fixed_tiles, representation):
    action = None
    if representation == 'narrow' or representation == 'turtle':
        if cur_pos['x'] is None:
            action = np.ndarray(shape=(1,))
            action[0] = 0
        elif isFixed(cur_pos, fixed_tiles):
            action = np.ndarray(shape=(1,))
            action[0] = fixed_tiles[(cur_pos['y'], cur_pos['x'])] + 1
    if representation == 'wide':
        if isFixed(cur_pos, fixed_tiles):
            action = []
    return action

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


def satisfy_fixed_tiles(fixed_tiles):
    count = 0
    for tile in fixed_tiles:
        if fixed_tiles[tile]:
            count += 1
    return count >= len(fixed_tiles) * 0.8


def check_tiles(fixed_tiles, obs):
    for tile in fixed_tiles:
        if int(obs[0][tile[0]][tile[1]][tile[2]]) == 1:
            fixed_tiles[tile] = True
        else:
            fixed_tiles[tile] = False


def process(tiles):
    all_tiles = tiles.split("|")
    res = {}
    for tile in all_tiles:
        if tile == "":
            break
        tmp = tile.split(",")
        res[(int(tmp[0]), int(tmp[1]))] = int(tmp[2])
    return res

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
