"""
python cleandata.py <training_folder_name> [training_folder_name] ...

THIS WILL OVERWRITE THE TRAINING DATA AND GAME INFO FILES!

e.g. "python cleandata.py training_L0" will clean all folders that start with
"training_L0" and have a number attached, such as "training_L0_9".
"""

import os
import os.path
import sys
from re import match

import numpy as np

training_folders = ["training"]  # Should be specified in argv.
_2D = False
offset = False
sensor_range = 10
width = 2

if __name__ == "__main__":
    if len(sys.argv) > 1:
        training_folders = sys.argv[1:]
    print(training_folders)

offset = 0 if offset else 1
side_length = (sensor_range + 1 - offset) * 2 - 1
w = width * 2 + 1


def load_training(folder_path):
    with open(os.path.join(folder_path, "game_info.csv"), "r") as f:
        game_info = np.loadtxt(f, delimiter=",")
        game_info = game_info.reshape((-1, 2))
    with open(os.path.join(folder_path, "training_x.csv"), "r") as f:
        training_x = np.loadtxt(f, delimiter=",")
    if _2D:
        training_x = training_x.reshape((-1, side_length, side_length))
    else:
        training_x = training_x.reshape((-1, sensor_range, w * 4))
    with open(os.path.join(folder_path, "training_y.csv"), "r") as f:
        training_y = np.loadtxt(f, delimiter=",")
    return training_x, training_y, game_info


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


working_dir = os.path.split(__file__)[0]
if working_dir == "":
    working_dir = "."

for folder_name in training_folders:
    name_len = len(folder_name)
    for training_folder in os.listdir(working_dir):
        folder_path = os.path.join(working_dir, training_folder)
        if os.path.isdir(folder_path) and \
                training_folder.startswith(folder_name) and \
                match("_[0-9]+", training_folder[name_len:]):
            print(training_folder)
            training_x, training_y, game_info = load_training(folder_path)
            old_count = len(training_x)
            print(training_x.shape)

            training_x2, training_y2, = [], []
            f = 0
            for i in range(len(game_info)):
                prev_x, prev_y = None, None
                g = 0
                game_frames = int(game_info[i][0])
                # print("Game {}: {} Frames".format(i, game_frames))
                for _ in range(game_frames):
                    # Process frame.
                    if prev_x is None:
                        prev_x = training_x[f]
                        prev_y = training_y[f]
                    else:
                        cur_x = training_x[f]
                        cur_y = training_y[f]
                        if (cur_x == prev_x).all():
                            prev_y = cur_y
                        else:
                            training_x2.append(prev_x)
                            training_y2.append(prev_y)
                            prev_x = cur_x
                            prev_y = cur_y
                            g += 1
                    f += 1
                training_x2.append(prev_x)
                training_y2.append(prev_y)
                game_info[i][0] = g + 1

            training_x2 = np.array(training_x2)
            training_y2 = np.array(training_y2)
            new_count = len(training_x2)
            print(training_x2.shape)
            print("Cut {} frames. ({:.3}x reduction)".format(
                old_count - new_count, old_count / new_count))
            save_training(folder_path, training_x2, training_y2, game_info)
            del training_x, training_y, game_info, training_x2, training_y2
