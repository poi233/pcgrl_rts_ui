from gym_pcgrl.envs.probs import RTSProblem


class SmallFairRTSProblem(RTSProblem):
    def __init__(self):
        super().__init__()
        self._width = 8
        self._height = 8
        self._min_resource = self._width / 8
        self._max_resource = self._width
        self._max_obstacles = self._width / 2 * 3
        self._resource_distance_diff = 1
        self._resource_balance_diff = self._width / 4
        self._area_control_diff = self._width / 4 * 2
        self._base_distance_diff = self._width * 3 / 8

    def get_episode_over(self, new_stats, old_stats):
        basic_rules = new_stats["base_count"] == self._target_base and \
                      self._min_resource <= new_stats["resource_count"] <= self._max_resource and \
                      new_stats["region"] == 1
        eval_total = new_stats["base_distance"] + new_stats["resource_distance"] + new_stats["resource_balance"] + \
                     new_stats["area_control"]
        optional_rules = eval_total > -10
        return basic_rules and optional_rules

