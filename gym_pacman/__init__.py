from gym.envs.registration import register

from .envs import PacmanEnv
from .res import *

register(
    id='Pacman-v0',
    entry_point='gym_pacman.envs:PacmanEnv',
)
