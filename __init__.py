import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='HaliteIIEnv',
    entry_point='envs.halite_env:HaliteIIEnv',
    timestep_limit=10000,
    reward_threshold=10000.0,
    nondeterministic=True,
)