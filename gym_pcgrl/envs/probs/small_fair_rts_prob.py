from gym_pcgrl.envs.probs import RTSProblem


class SmallFairRTSProblem(RTSProblem):
    def __init__(self):
        super().__init__()

    def get_episode_over(self, new_stats, old_stats):
        basic_rules = new_stats["base_count"] == self._target_base and \
                      self._min_resource <= new_stats["resource_count"] <= self._max_resource and \
                      new_stats["region"] == 1
        eval_total = new_stats["base_distance"] + new_stats["resource_distance"] + new_stats["resource_balance"] + \
                     new_stats["area_control"]
        optional_rules = eval_total > -10
        return basic_rules and optional_rules

