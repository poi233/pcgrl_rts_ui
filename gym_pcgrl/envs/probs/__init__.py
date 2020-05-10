from gym_pcgrl.envs.probs.rts_prob import RTSProblem
from gym_pcgrl.envs.probs.small_fair_rts_prob import SmallFairRTSProblem
from gym_pcgrl.envs.probs.small_fun_rts_prob import SmallFunRTSProblem
from gym_pcgrl.envs.probs.medium_fair_rts_prob import MediumFairRTSProblem
from gym_pcgrl.envs.probs.medium_fun_rts_prob import MediumFunRTSProblem
from gym_pcgrl.envs.probs.area_control_small_rts import AreaControlSmallRTSProblem
from gym_pcgrl.envs.probs.base_small_rts import BaseSmallRTSProblem
from gym_pcgrl.envs.probs.resource_small_rts import ResourceSmallRTSProblem
from gym_pcgrl.envs.probs.area_control_medium_rts import AreaControlMediumRTSProblem
from gym_pcgrl.envs.probs.base_medium_rts import BaseMediumRTSProblem
from gym_pcgrl.envs.probs.resource_medium_rts import ResourceMediumRTSProblem

# all the problems should be defined here with its corresponding class
PROBLEMS = {
    "rts": RTSProblem,
    "small_fair_rts": SmallFairRTSProblem,
    "medium_fair_rts": MediumFairRTSProblem,
    "area_control_small_rts": AreaControlSmallRTSProblem,
    "base_small_rts": BaseSmallRTSProblem,
    "resource_small_rts": ResourceSmallRTSProblem,
    "area_control_medium_rts": AreaControlMediumRTSProblem,
    "base_medium_rts": BaseMediumRTSProblem,
    "resource_medium_rts": ResourceMediumRTSProblem,
}
