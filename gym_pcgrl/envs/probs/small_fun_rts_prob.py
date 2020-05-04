from gym_pcgrl.envs.probs import RTSProblem


class SmallFunRTSProblem(RTSProblem):
    def __init__(self):
        super().__init__()
        self._width = 8
        self._height = 8

        self._min_resource = self._width / 8 * 2
        self._max_resource = self._width / 2 * 2
        self._max_obstacles = self._width * 2
        self._resource_distance_diff = self._width / 8 * 2
        self._area_control_diff = self._width / 8 * 5


        # self._rewards = {
        #     "base_count": 6,
        #     "base_distance": 2,
        #     "area_control": 4,
        #     # "base_space": 2,
        #     # "asymmetry": 1,
        #     "resource_count": 4,
        #     "resource_distance": 2,
        #     # "resource_clustering": 1,
        #     # "path_overlapping": 2,
        #     "obstacle": 1,
        #     "region": 6
        # }
