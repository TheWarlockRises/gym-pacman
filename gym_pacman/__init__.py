from gym.envs.registration import register

from .scorer import *
from .sensor import *

register(
    id='Pacman-v0',
    entry_point='gym_pacman.envs:PacmanEnv',
)
