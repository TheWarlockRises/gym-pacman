from gym.envs.registration import register

register(
    id='Pacman-v0',
    entry_point='gym_pacman.envs:PacmanEnv',
)

register(
    id='Pacman-Random-v0',
    entry_point='gym_pacman.envs:RandomEnv',
)

register(
    id='Pacman-Rendered-v0',
    entry_point='gym_pacman.envs:RenderedEnv',
)