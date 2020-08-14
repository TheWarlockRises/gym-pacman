"""
Scoring and sensor needs to be manually tweaked before running this script.

python runscoring.py <model_folder> <output_folder> [seed_number]
  [level_number] [level_number] ...

e.g. "python runrandom.py model_all results_all 924873 1 2 3 4" will run levels
  using the seed 924873 where the possible levels to run in a given game
  are 1, 2, 3, or 4. After running, the results are output to the "results_all"
  folder. Instead of random actions, predictions are made using the model from
  the "model_all" folder.
"""

import os
import os.path
import sys

import gym
import numpy as np
import pygame
from keras.models import model_from_json

from gym_pacman import BasicScorer, sensor_1d_4, sensor_2d

initial_games = 20
goal_steps = 12000
seed = None  # Should be specified in argv.
level = None  # Should be specified in argv.
model_folder = "model_L0"
results_folder = "results_L0"

# Sensor Parameters
_2D = False
block = False
door_skip = True
offset = False
rotate = True
sensor_range = 10
tile_map = True
width = 2
scorer = BasicScorer()

if _2D:
    sensor = sensor_2d(sensor_range, block=block, door_skip=door_skip,
                       offset=offset, rotate=rotate, tile_map=tile_map,
                       width=width)
else:
    sensor = sensor_1d_4(sensor_range, block=block, door_skip=door_skip,
                         offset=offset, rotate=rotate, tile_map=tile_map,
                         width=width)

if len(sys.argv) > 1:
    model_folder = sys.argv[1]
    if len(sys.argv) > 2:
        results_folder = sys.argv[2]
        if len(sys.argv) > 3:
            seed = int(sys.argv[3])
            if len(sys.argv) > 4:
                level = list(map(int, sys.argv[4:]))
print(model_folder, results_folder, seed, level)

offset = 0 if offset else 1
side_length = (sensor_range + 1 - offset) * 2 - 1
w = width * 2 + 1


def load_model(folder_name):
    model_dir = os.path.join(os.path.split(__file__)[0], folder_name)
    if not os.path.isdir(model_dir):
        return None
    f = open(os.path.join(model_dir, "model.json"), "r")
    model = model_from_json(f.read())
    model.load_weights(os.path.join(model_dir, "model.h5"))
    return model


def save_training(folder_path, training_x, training_y,
                  game_info):  # scores, game_ids):
    if os.path.exists(folder_path) and not os.path.isdir(folder_path):
        return False
    elif not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if _2D:
        np.savetxt(os.path.join(folder_path, "training_x.csv"),
                   training_x.reshape(-1, side_length ** 2), delimiter=",",
                   fmt="%d")
    else:
        np.savetxt(os.path.join(folder_path, "training_x.csv"),
                   training_x.reshape(-1, w * 4), delimiter=",", fmt="%d")
    np.savetxt(os.path.join(folder_path, "training_y.csv"), training_y,
               delimiter=",", fmt="%d")
    np.savetxt(os.path.join(folder_path, "game_info.csv"), game_info,
               delimiter=",", fmt="%d")
    return True


model = load_model(model_folder)
model.summary()
env = gym.make("Pacman-v0", level=level, randomized=False, scorer=scorer,
               sensor=sensor)
random = np.random.RandomState(seed)

pygame.mixer.pre_init(22050, -16, 1, 1024)
pygame.mixer.init()
pygame.mixer.set_num_channels(7)
channel_backgound = pygame.mixer.Channel(6)
clock = pygame.time.Clock()
pygame.init()

game_info = []
training_x = []
training_y = []
for ig in range(initial_games):
    score = 0
    survived = 0
    memory_x = []
    memory_y = []

    env.seed(random.randint(2 ** 31))
    previous_observation = env.reset()
    if _2D:
        predic = model.predict(np.array(
            [previous_observation.reshape(side_length, side_length, 1)]))
    else:
        predic = model.predict(
            np.array([previous_observation.reshape(sensor_range, -1)]))
    direc = np.argmax(predic)
    if rotate:
        direc -= env.action
        direc %= 4

    for s in range(goal_steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
        env.render()
        observation, reward, done, info = env.step(direc)

        if len(previous_observation) > 0:
            memory_x.append(previous_observation)
            # TODO: Record for rotation.
            output = [0, 0, 0, 0]
            output[direc] = 1
            memory_y.append(output)

        if _2D:
            predic = model.predict(
                observation.reshape(1, side_length, side_length, 1))
        else:
            predic = model.predict(
                np.array([observation.reshape(sensor_range, -1)]))
        direc = np.argmax(predic)
        if rotate:
            if direc > 0:
                print(direc)
            direc += info["action"]
            direc %= 4

        previous_observation = observation

        score += reward
        if done:
            break
        else:
            survived += 1

    game_info.append([len(memory_x), score])
    training_x.extend(memory_x)
    training_y.extend(memory_y)
    print("Ran game {}: {} frames, {} points".format(ig, survived, score))

game_info = np.array(game_info)
training_x = np.array(training_x)
training_y = np.array(training_y)
save_training(results_folder, training_x, training_y, game_info)
