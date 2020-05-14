import os

from PIL import Image

from gym_pcgrl.envs.helper import get_range_reward, get_tile_locations, \
    calc_num_regions, calc_certain_tile, run_dikjstra
from gym_pcgrl.envs.probs.problem import Problem

"""
Generate a  RTS map where two player can play.

Args:
    target_enemy_dist: enemies should be at least this far from the player on spawn
"""


class RTSProblem(Problem):
    """
    The constructor is responsible of initializing all the game parameters
    """

    def __init__(self):
        super().__init__()
        self._width = 8
        self._height = 8
        self._prob = {"empty": 0.785, "base": 0.03, "resource": 0.06, "obstacle": 0.125}
        self._border_size = 0
        self._target_base = 2
        self._min_resource = self._width / 8
        self._max_resource = self._width
        self._max_obstacles = self._width / 2 * 3
        self._resource_distance_diff = 1
        self._resource_balance_diff = self._width / 4
        self._area_control_diff = self._width / 4 * 2
        self._base_distance_diff = self._width * 3 / 8
        self._map = None

        self._rewards = {
            "base_count": 10,
            "base_distance": 2,
            "area_control": 4,
            "resource_count": 2,
            "resource_distance": 5,
            "resource_balance": 4,
            "obstacle": 1,
            "region": 10
        }

    """
    Get a list of all the different tile names

    Returns:
        string[]: that contains all the tile names
    """

    def get_tile_types(self):
        return ["empty", "base", "resource", "obstacle"]

    """
    Adjust the parameters for the current problem

    Parameters:
        width (int): change the width of the problem level
        height (int): change the height of the problem level
        probs (dict(string, float)): change the probability of each tile
        intiialization, the names are "empty", "solid"
        target_path (int): the current path length that the episode turn when it reaches
        rewards (dict(string,float)): the weights of each reward change between the new_stats and old_stats
    """

    def adjust_param(self, **kwargs):
        super().adjust_param(**kwargs)

        # self._min_resource = kwargs.get('min_resource', self._max_resource)
        # self._max_resource = kwargs.get('max_resource', self._max_resource)
        self._max_obstacles = kwargs.get('max_obstacles', self._max_obstacles)
        self._resource_distance_diff = kwargs.get("resource_distance_diff", self._resource_distance_diff)
        self._map = kwargs.get("map", None)
        rewards = kwargs.get('rewards')
        if rewards is not None:
            for t in rewards:
                if t in self._rewards:
                    self._rewards[t] = rewards[t]

    """
    Get the current stats of the map

    Returns:
        dict(string,any): stats of the current map to be used in the reward, episode_over, debug_info calculations.
        The used status are "reigons": number of connected empty tiles, "path-length": the longest path across the map
    """

    def get_stats(self, map):
        map_locations = get_tile_locations(map, self.get_tile_types())
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
            map_stats["base_distance"] = int(self._base_distance_diff - abs(
                self._width / 2 - max(map_stats["base_distance"], dikjstra1[b2_y][b2_x])))
            map_stats["base_distance"] = int(self._base_distance_diff - abs(
                self._width / 2 - max(map_stats["base_distance"], dikjstra1[b2_y][b2_x])))
            # calculate resource distance
            if self._min_resource <= map_stats["resource_count"] <= self._max_resource:  # and map_stats["resource_count"] <= self._max_resource:
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
                map_stats["resource_distance"] = int(self._resource_distance_diff - abs(dist1 - dist2))
                map_stats["resource_balance"] = int(self._resource_balance_diff - abs(sum1 - sum2))
            # calculate area control
            base1 = 0
            base2 = 0
            for x in range(self._width):
                for y in range(self._height):
                    if dikjstra1[y][x] > dikjstra2[y][x]:
                        base2 += 1
                    elif dikjstra1[y][x] < dikjstra2[y][x]:
                        base1 += 1
            map_stats["area_control"] = self._area_control_diff - abs(base1 - base2)
        return map_stats

    """
    Get the current game reward between two stats

    Parameters:
        new_stats (dict(string,any)): the new stats after taking an action
        old_stats (dict(string,any)): the old stats before taking an action

    Returns:
        float: the current reward due to the change between the old map stats and the new map stats
    """

    def get_reward(self, new_stats, old_stats):
        # longer path is rewarded and less number of regions is rewarded
        rewards = {
            "base_count": get_range_reward(new_stats["base_count"], old_stats["base_count"], self._target_base,
                                           self._target_base),
            "base_distance": get_range_reward(new_stats["base_distance"], old_stats["base_distance"], 0,
                                              self._base_distance_diff),
            "resource_count": get_range_reward(new_stats["resource_count"], old_stats["resource_count"],
                                               self._min_resource, self._max_resource),
            "resource_distance": get_range_reward(new_stats["resource_distance"], old_stats["resource_distance"], 0,
                                                  self._resource_distance_diff),
            "resource_balance": get_range_reward(new_stats["resource_balance"], old_stats["resource_balance"], 0,
                                                 self._resource_balance_diff),
            "obstacle": get_range_reward(new_stats["obstacle"], old_stats["obstacle"], 0, self._max_obstacles),
            "region": get_range_reward(new_stats["region"], old_stats["region"], 1, 1),
            "area_control": get_range_reward(new_stats["area_control"], old_stats["area_control"], 0,
                                             self._area_control_diff),
        }
        # calculate the total reward
        return rewards["base_count"] * self._rewards["base_count"] + \
               rewards["base_distance"] * self._rewards["base_distance"] + \
               rewards["resource_count"] * self._rewards["resource_count"] + \
               rewards["region"] * self._rewards["region"] + \
               rewards["resource_distance"] * self._rewards["resource_distance"] + \
               rewards["resource_balance"] * self._rewards["resource_balance"] + \
               rewards["obstacle"] * self._rewards["obstacle"] + \
               rewards["area_control"] * self._rewards["area_control"]

    """
    Uses the stats to check if the problem ended (episode_over) which means reached
    a satisfying quality based on the stats

    Parameters:
        new_stats (dict(string,any)): the new stats after taking an action
        old_stats (dict(string,any)): the old stats before taking an action

    Returns:
        boolean: True if the level reached satisfying quality based on the stats and False otherwise
    """

    def get_episode_over(self, new_stats, old_stats):
        basic_rules = new_stats["base_count"] == self._target_base and \
                      self._min_resource <= new_stats["resource_count"] <= self._max_resource and \
                      new_stats["region"] == 1
        eval_total = new_stats["base_distance"] + new_stats["resource_distance"] + new_stats["resource_balance"] + \
                     new_stats["area_control"]
        optional_rules = eval_total > -10
        return basic_rules and optional_rules

    """
    Get any debug information need to be printed

    Parameters:
        new_stats (dict(string,any)): the new stats after taking an action
        old_stats (dict(string,any)): the old stats before taking an action

    Returns:
        dict(any,any): is a debug information that can be used to debug what is
        happening in the problem
    """

    def get_debug_info(self, new_stats, old_stats):
        return {
            "base_count": new_stats["base_count"],
            "base_distance": new_stats["base_distance"],
            "resource_count": new_stats["resource_count"],
            "resource_distance": new_stats["resource_distance"],
            "resource_balance": new_stats["resource_balance"],
            "obstacle": new_stats["obstacle"],
            "region": new_stats["region"],
            "area_control": new_stats["area_control"],
            "old_stats": old_stats
        }

    """
    Get an image on how the map will look like for a specific map

    Parameters:
        map (string[][]): the current game map

    Returns:
        Image: a pillow image on how the map will look like using the binary graphics
    """

    def render(self, map):
        if self._graphics == None:
            self._graphics = {
                "empty": Image.open(os.path.dirname(__file__) + "/rts/passable.png").convert('RGBA'),
                "base": Image.open(os.path.dirname(__file__) + "/rts/base.png").convert('RGBA'),
                "resource": Image.open(os.path.dirname(__file__) + "/rts/mineral.png").convert('RGBA'),
                "obstacle": Image.open(os.path.dirname(__file__) + "/rts/impassable.png").convert('RGBA'),
            }
        return super().render(map)
