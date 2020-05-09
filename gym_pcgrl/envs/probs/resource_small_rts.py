from gym_pcgrl.envs.probs import RTSProblem


class ResourceSmallRTSProblem(RTSProblem):
    def __init__(self):
        super().__init__()

        self._rewards = {
            "base_count": 10,
            "base_distance": 2,
            "area_control": 4,
            "resource_count": 2,
            "resource_distance": 10,
            "resource_balance": 10,
            "obstacle": 1,
            "region": 10
        }


    def get_episode_over(self, new_stats, old_stats):
        basic_rules = new_stats["base_count"] == self._target_base and \
                      self._min_resource <= new_stats["resource_count"] <= self._max_resource and \
                      new_stats["region"] == 1
        optional_rules = new_stats["resource_distance"] > 0 and new_stats["resource_balance"] > 0
        return basic_rules and optional_rules

