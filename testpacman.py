import random
from sys import exit

from gym_pacman.envs.pacman_env import PacmanEnv
from gym_pacman.pacman import *

pygame.mixer.pre_init(22050, -16, 1, 1024)
pygame.mixer.init()
pygame.mixer.set_num_channels(7)
channel_backgound = pygame.mixer.Channel(6)
clock = pygame.time.Clock()
pygame.init()


pacman = PacmanEnv(invincible=False, randomized=True)

direc = 0

while True:
    # Keep window from complaining unresponsive
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)
    pacman.render()
    observation, _, done, info = pacman.step(direc)
    clock.tick(40)
    if random.random() < 0.05:
        direc = random.randint(0, 3)
    elif info["pacmanx"] == 0 and info["pacmany"] == 0:
        direc = random.randint(0, 3)
        possible = []
        for i in range(4):
            if observation[1][i] > 0:
                possible.append(i)
        if len(possible) > 0:
            direc = possible[random.randint(0, len(possible) - 1)]
    if done:
        pacman.reset()
