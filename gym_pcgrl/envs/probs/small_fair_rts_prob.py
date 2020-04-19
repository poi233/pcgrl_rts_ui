from gym_pcgrl.envs.probs import RTSProblem


class SmallFairRTSProblem(RTSProblem):
    def __init__(self):
        super().__init__()
        self._width = 8
        self._height = 8

        self._min_resource = self._width / 8
        self._max_resource = self._width / 2
        self._max_chock_points = self._width
        self._resource_distance_diff = self._width / 8

        self._rewards = {
            "base_count": 6,
            "base_distance": 2,
            # "base_space": 2,
            # "asymmetry": 1,
            "resource_count": 4,
            "resource_distance": 1,
            # "resource_clustering": 1,
            # "path_overlapping": 2,
            "obstacle": 3,
            "region": 6
        }
