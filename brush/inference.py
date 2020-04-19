"""
Run a trained agent and get generated maps
"""
import model
from stable_baselines import PPO2

import time
from utils import make_vec_envs

import os
from django.conf import settings


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
    env = make_vec_envs(env_name, representation, None, 1, **kwargs)
    obs = env.reset()
    dones = False
    for i in range(kwargs.get('trials', 1)):
        while not (dones and satisfy_fixed_tiles(fixed_tiles)):
            action, _ = agent.predict(obs)
            obs, _, dones, info = env.step(action)
            check_tiles(fixed_tiles, obs)
            if kwargs.get('verbose', False):
                print(info[0])
            if dones and satisfy_fixed_tiles(fixed_tiles):
                break
        # time.sleep(0.2)
    return obs[0]

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
        res[(int(tmp[0]), int(tmp[1]), int(tmp[2]))] = False
    return res

################################## MAIN ########################################
game = 'small_fair_rts'
representation = 'narrow'
model_path = '../static/models/{}/{}/model_1.pkl'.format(game, representation)
# model_path = os.path.join(settings.BASE_DIR, model_name)
kwargs = {
    'change_percentage': 0.4,
    'trials': 1,
    'verbose': True
}


if __name__ == '__main__':
    obs = infer(game, representation, model_path, **kwargs)
    print(obs)
