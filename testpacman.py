import random
from sys import exit

from gym_pacman.envs.pacman_env import PacmanEnv
from gym_pacman.pacman import *
from gym_pacman.sensor import sensor_1d_4

pygame.mixer.pre_init(22050, -16, 1, 1024)
pygame.mixer.init()
pygame.mixer.set_num_channels(7)
channel_backgound = pygame.mixer.Channel(6)
clock = pygame.time.Clock()
pygame.init()

offset = True
pausing = False
sensor_range = 10
width = 2

pacman = PacmanEnv(invincible=False, randomized=True,
                   sensor=sensor_1d_4(sensor_range, offset=offset, width=width))
pacman.reset()

direc = 0
offset = 0 if offset else 1
w = width * 2 + 1

while True:
    # Keep window from complaining unresponsive
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)
    pacman.render()
    observation, _, done, info = pacman.step(direc)
    pause = pausing
    if pause:
        print(observation)
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pause = False
        clock.tick(60)
    else:
        clock.tick(40)
    if random.random() < 0.05:
        direc = random.randint(0, 3)
    elif info["pacmanx"] == 0 and info["pacmany"] == 0:
        direc = random.randint(0, 3)
        possible = []
        for i in range(4):
            if observation[offset][i * w + width] > 0:
                possible.append(i)
        if len(possible) > 0:
            direc = possible[random.randint(0, len(possible) - 1)]
    if done:
        pacman.reset()
