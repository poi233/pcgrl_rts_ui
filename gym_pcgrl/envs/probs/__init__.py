from gym_pcgrl.envs.probs.rts_prob import RTSProblem
from gym_pcgrl.envs.probs.small_fair_rts_prob import SmallFairRTSProblem
from gym_pcgrl.envs.probs.small_fun_rts_prob import SmallFunRTSProblem
from gym_pcgrl.envs.probs.medium_fair_rts_prob import MediumFairRTSProblem
from gym_pcgrl.envs.probs.medium_fun_rts_prob import MediumFunRTSProblem
from gym_pcgrl.envs.probs.large_fair_rts_prob import LargeFairRTSProblem
from gym_pcgrl.envs.probs.larget_fun_rts_prob import LargeFunRTSProblem



# all the problems should be defined here with its corresponding class
PROBLEMS = {
    "rts": RTSProblem,
    "small_fair_rts": SmallFairRTSProblem,
    "small_fun_rts": SmallFunRTSProblem,
    "medium_fair_rts": MediumFairRTSProblem,
    "medium_fun_rts": MediumFunRTSProblem,
    "large_fair_rts": LargeFairRTSProblem,
    "large_fun_rts": LargeFunRTSProblem
}
