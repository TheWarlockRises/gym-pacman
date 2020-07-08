import pygame

from gym_pacman.envs.pacman_env import PacmanEnv

pacman = PacmanEnv()

pygame.mixer.pre_init(22050, -16, 1, 1024)
pygame.mixer.init()
pygame.mixer.set_num_channels(7)
channel_backgound = pygame.mixer.Channel(6)
pygame.init()
