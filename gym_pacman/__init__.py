from gym.envs.registration import register

from .envs import *
from .res import *
from . import *

register(
    id='Pacman-v0',
    entry_point='gym_pacman.envs:PacmanEnv',
)
