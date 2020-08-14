"""
Scoring and sensor needs to be manually tweaked before running this script.

python runrandom.py <output_folder> [seed_number] [level_number]
  [level_number] ...

e.g. "python runrandom.py training_all 924873 1 2 3 4" will run randomized
  levels using the seed 924873 where the possible levels to run in a given game
  are 1, 2, 3, or 4. After running, the data is output to the "training_all"
  folder.
"""

import os
import os.path
import sys
from multiprocessing import Process

import gym
import numpy as np

from gym_pacman import BasicScorer
from gym_pacman.sensor import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Every process will 100% a thread on your computer so be careful.
initial_games = 1000
num_processes = 2
goal_steps = 1200
level = None  # Should be specified in argv.
seed = None  # Should be specified in argv.
training_folder = "training"  # Should be specified in argv.

# Either the score or survival requirement needs to be met.
random_turn_chance = 0.05
score_requirement = 1000
survival_requirement = 1201
scorer = BasicScorer(ghost_hit=-10000, pellet_eat=100, power_pellet_eat=500)

# Sensor Parameters
_2D = False
block = False
door_skip = True
offset = False
rotate = True
sensor_range = 10
tile_map = True
width = 2

if _2D:
    sensor = sensor_2d(sensor_range, block=block, door_skip=door_skip,
                       offset=offset, rotate=rotate, tile_map=tile_map,
                       width=width)
else:
    sensor = sensor_1d_4(sensor_range, block=block, door_skip=door_skip,
                         offset=offset, rotate=rotate, tile_map=tile_map,
                         width=width)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        training_folder = sys.argv[1]
        if len(sys.argv) > 2:
            seed = int(sys.argv[2])
            if len(sys.argv) > 3:
                level = list(map(int, sys.argv[3:]))
    print(training_folder, seed, level)

# Run training...
offset = 0 if offset else 1
w = width * 2 + 1
dirs = ((1, 0), (0, -1), (-1, 0), (0, 1))


def save_training(folder_path, training_x, training_y,
                  game_info):  # scores, game_ids):
    if os.path.exists(folder_path) and not os.path.isdir(folder_path):
        return False
    elif not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if _2D:
        side_length = (sensor_range + 1 - offset) * 2 - 1
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


def run_training(training_folder, num, games, level, seed):
    if seed is not None:
        seed += num
    print("Process {} (seed {}) will save to '{}'".format(num, seed,
                                                          training_folder))
    env = gym.make("Pacman-v0", level=level, randomized=True, scorer=scorer,
                   sensor=sensor)
    good_games = 0
    game_p = max(1, games // 100)
    random_seed = np.random.RandomState(seed)
    game_info = []
    training_x = []
    training_y = []
    for ig in range(games):
        random = np.random.RandomState(random_seed.randint(2 ** 31))
        score = 0
        survived = 0
        memory_x = []
        memory_y = []

        env.seed(random_seed.randint(2 ** 31))
        previous_observation = env.reset()
        previous_action = env.action

        # Start in some direction that isn't a wall.
        direc = random.randint(4)
        possible = []
        r_observation = previous_observation
        if _2D:
            if rotate:
                r_observation = np.rot90(r_observation, k=4 - previous_action)
            center = len(r_observation) // 2
            for i in range(4):
                if r_observation[center + dirs[i][0]][center + dirs[i][1]] > 0:
                    possible.append(i)

        elif len(r_observation[offset]) // w == 4:
            if rotate:
                r_observation = np.roll(r_observation, previous_action * w,
                                        axis=1)
            for i in range(4):
                if r_observation[offset][i * w + width] > 0:
                    possible.append(i)
        if len(possible) > 0:
            direc = possible[random.randint(len(possible))]

        # Run up to goal_steps.
        for s in range(goal_steps):
            observation, reward, done, info = env.step(direc)

            memory_x.append(previous_observation)
            output = [0, 0, 0, 0]
            if rotate:
                output[(direc - previous_action) % 4] = 1
            else:
                output[direc] = 1
            memory_y.append(output)

            if info["pacmanx"] == 0 and info["pacmany"] == 0:
                direc = random.randint(4)
                possible = []
                r_observation = observation
                if _2D:
                    if rotate:
                        r_observation = np.rot90(r_observation,
                                                 k=4 - env.action)
                    center = len(r_observation) // 2
                    for i in range(4):
                        if r_observation[center + dirs[i][0]][
                            center + dirs[i][1]] > 0:
                            possible.append(i)

                elif len(r_observation[offset]) // w == 4:
                    if rotate:
                        r_observation = np.roll(r_observation,
                                                info["action"] * w, axis=1)
                    for i in range(4):
                        if r_observation[offset][i * w + width] > 0:
                            possible.append(i)
                if len(possible) > 0:
                    direc = possible[random.randint(len(possible))]
            elif random.random() < random_turn_chance:
                direc = random.randint(4)

            previous_action = info["action"]
            previous_observation = observation

            score += reward
            if done:
                break
            else:
                survived += 1

        if score >= score_requirement or survived >= survival_requirement:
            game_info.append([len(memory_x), score])
            good_games += 1
            training_x.extend(memory_x)
            training_y.extend(memory_y)

        if ig % game_p == 0:
            print("Process {} ran game {}.".format(num, ig))

    print(
        "Process {} (seed {}): {} frames from {} games in the training data.".format(
            num, seed, len(training_x), good_games, level))
    if len(training_x) > 0:
        game_info = np.array(game_info)
        training_x = np.array(training_x)
        training_y = np.array(training_y)
        save_training(training_folder, training_x, training_y, game_info)


processes = []

if __name__ == "__main__":
    games_per_process = initial_games // num_processes
    folder_num = 0
    for i in range(num_processes):
        games = games_per_process + (
            1 if i < initial_games % num_processes else 0)
        if games <= 0:
            break
        # Find directory that does not exist.
        while True:
            folder_name = "{}_{}".format(training_folder, folder_num)
            folder_path = os.path.join(os.path.split(__file__)[0], folder_name)
            folder_num += 1
            if not os.path.exists(folder_path):
                break
        process = Process(target=run_training,
                          args=(folder_path, i, games, level, seed))
        processes.append(process)
    for p in processes:
        p.start()
    for p in processes:
        p.join()
