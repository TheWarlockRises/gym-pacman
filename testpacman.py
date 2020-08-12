import numpy as np
from sys import exit

from gym_pacman.envs.pacman_env import PacmanEnv
from gym_pacman.pacman import *
from gym_pacman.sensor import *

pygame.mixer.pre_init(22050, -16, 1, 1024)
pygame.mixer.init()
pygame.mixer.set_num_channels(7)
channel_backgound = pygame.mixer.Channel(6)
clock = pygame.time.Clock()
pygame.init()

pausing = False
fps = 40
_2D = True
level = None
seed = None
door_skip = True
offset = False
rotate = True
tile_map = True
sensor_range = 5
view = 0
width = 2

if _2D:
    sensor = sensor_2d(sensor_range, door_skip=door_skip, offset=offset,
                       rotate=rotate, tile_map=tile_map, view=view)
else:
    sensor = sensor_1d_4(sensor_range, door_skip=door_skip, offset=offset,
                         rotate=rotate, tile_map=tile_map, view=view,
                         width=width)

random = np.random.RandomState(seed)
pacman = PacmanEnv(level=level, invincible=False, randomized=True,
                   sensor=sensor)
pacman.seed(random.randint(2 ** 31))
pacman.reset()

direc = 0
offset = 0 if offset else 1
w = width * 2 + 1
dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))
# was_stuck = False

while True:
    # Keep window from complaining unresponsive
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)
    pacman.render()
    observation, _, done, info = pacman.step(direc)
    pause = pausing
    if pause:
        if rotate:
            print(pacman.action)
        print(observation.T)
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pause = False
        clock.tick(60)
    else:
        clock.tick(fps)

    if info["pacmanx"] == 0 and info["pacmany"] == 0:
        direc = random.randint(4)
        possible = []

        if _2D:
            if rotate:
                observation = np.rot90(observation, k=4 - info["action"])
            center = len(observation) // 2
            for i in range(4):
                if observation[center + dirs[i][0]][center + dirs[i][1]] > 0:
                    possible.append(i)

        elif len(observation[offset]) // w == 4:
            if rotate:
                observation = np.roll(observation, info["action"] * w, axis=1)
                # print(observation)
            for i in range(4):
                if observation[offset][i * w + width] > 0:
                    possible.append(i)

        # if was_stuck:
        # print("deja vu")
        # pausing = True
        if len(possible) > 0:
            direc = possible[random.randint(len(possible))]
        # was_stuck = True
    # else:
    # was_stuck = False
    elif random.random() < 0.05:
        direc = random.randint(4)

    if done:
        # was_stuck = False
        new_seed = random.randint(2 ** 31)
        pacman.seed(new_seed)
        if seed is not None:
            print(new_seed)
        pacman.reset()
