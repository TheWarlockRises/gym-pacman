import random

from gym_pacman.envs.pacman_env import PacmanEnv
from gym_pacman.pacman import *

pygame.mixer.pre_init(22050, -16, 1, 1024)
pygame.mixer.init()
pygame.mixer.set_num_channels(7)
channel_backgound = pygame.mixer.Channel(6)
clock = pygame.time.Clock()
pygame.init()

pacman = PacmanEnv(True)

direc = 0

while True:
    pacman.render()
    done = pacman.step(direc)
    clock.tick(40)
    if random.random() < 0.1 or pacman.player.velX == 0 and pacman.player.velY == 0:
        direc = random.randint(0, 3)
    if done:
        break
