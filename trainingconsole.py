"""
Dumb console to load data and models for training.

python trainingconsole.py

Command list:
- "l <training_folder_name> [training_folder_name] ..."
  - Load one or more sets of training folders into memory.
  - e.g. "l training_L0 training_L1" will load all folders that start with
      "training_L0" or "training_L1" into memory.

- "m [model_folder_name]"
  - Load a preexisting model into memory or build a new model if no folder
      is specified.
  - e.g. "m model_L1_25" will load the model from the folder "model_L1_25"
      into memory.

- "s <training_folder_name> [training_folder_name] ..."
  - Select one or more sets of training folders and combine the data into
      a single array for model fitting.
  - e.g. "s training_L0" selects all data associated with "training_L0"
      folders.
  
- "t <output_folder_name> <epochs>"
  - Train the current model with the currently selected data for some epochs
      and output the resulting model to the specified output folder.
  - e.g. "t model_L1_30 5" will train the currently loaded model for 5 epochs
      using the selected data, placing the result into the "model_L1_30"
      folder when done.

- "q": exit
"""

import os
import os.path
import sys
from re import match

import numpy as np
from keras.layers import Conv1D, Conv2D, Dense, Dropout, Flatten, MaxPooling1D
from keras.models import model_from_json, Sequential
from keras.optimizers import RMSprop

_2D = False
offset = False
sensor_range = 10
width = 2

training_data = {}
offset = 0 if offset else 1
side_length = (sensor_range + 1 - offset) * 2 - 1
w = width * 2 + 1


def load_training(folder_path):
    with open(os.path.join(folder_path, "training_x.csv"), "r") as f:
        training_x = np.loadtxt(f, delimiter=",")
    if _2D:
        training_x = training_x.reshape((-1, side_length, side_length, 1))
    else:
        training_x = training_x.reshape((-1, sensor_range, w * 4))
    with open(os.path.join(folder_path, "training_y.csv"), "r") as f:
        training_y = np.loadtxt(f, delimiter=",")
    return training_x, training_y


def load_training_folders(path, training_folder):
    training_x, training_y = [], []
    print("{}:".format(training_folder))
    name_len = len(training_folder)
    for file_name in os.listdir(path):
        folder_path = os.path.join(path, file_name)
        if os.path.isdir(folder_path) and \
                file_name.startswith(training_folder) and \
                match("_[0-9]+", file_name[name_len:]):
            print(file_name)
            training_x2, training_y2 = load_training(folder_path)
            training_x.append(training_x2)
            training_y.append(training_y2)
            """
            if training_x is None:
                training_x, training_y = training_x2, training_y2
            else:
                training_x = np.concatenate((training_x, training_x2))
                training_y = np.concatenate((training_y, training_y2))
            """
    if len(training_x) == 0:
        return None, None
    training_x = np.concatenate(training_x)
    training_y = np.concatenate(training_y)
    print(training_x.shape, training_y.shape)
    return training_x, training_y


def save_model(folder_name, model):
    model_dir = os.path.join(os.path.split(__file__)[0], folder_name)
    if os.path.exists(model_dir) and not os.path.isdir(model_dir):
        return False
    elif not os.path.exists(model_dir):
        os.mkdir(model_dir)
    with open(os.path.join(model_dir, "model.json"), "w") as f:
        f.write(model.to_json())
    model.save_weights(os.path.join(model_dir, "model.h5"))
    return True


def load_model(folder_name):
    model_dir = os.path.join(os.path.split(__file__)[0], folder_name)
    if not os.path.isdir(model_dir):
        return None
    f = open(os.path.join(model_dir, "model.json"), "r")
    model = model_from_json(f.read())
    model.load_weights(os.path.join(model_dir, "model.h5"))
    model.compile(loss='mse', optimizer=RMSprop())
    return model


def build_model():
    model = Sequential()
    if _2D:
        model.add(Conv2D(filters=16,
                         kernel_size=(side_length // 10, side_length // 10),
                         strides=side_length // 10, activation='relu',
                         input_shape=(side_length, side_length, 1)))
        model.add(Conv2D(filters=32,
                         kernel_size=(side_length // 5, side_length // 5),
                         strides=side_length // 20, activation='relu',
                         input_shape=(side_length, side_length, 1)))
        # model.add(MaxPooling2D(pool_size=(side_length // 10, side_length // 10)))
    else:
        model.add(Conv1D(filters=64, kernel_size=sensor_range // 2,
                         activation='relu', input_shape=(sensor_range, w * 4)))
        # model.add(Conv1D(filters=32, kernel_size=sensor_range // 4, activation='relu'))
        model.add(Dropout(0.5))
        model.add(MaxPooling1D(pool_size=sensor_range // 2))
    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(Dense(4, activation='relu'))
    model.compile(loss='mse', optimizer=RMSprop())
    model.summary()
    return model


args = []
commands = []
model = None
working_dir = os.path.split(__file__)[0]
training_x, training_y = None, None

while True:
    commands = input("> ").strip().split(";")
    for command in commands:
        args = command.strip().split(" ")
        if args[0].startswith("e") or args[0].startswith("q"):
            sys.exit(0)



        # Load Training Data
        elif args[0].startswith("l"):
            load_folders = args[1:]
            for load_folder in load_folders:
                if load_folder in training_data:
                    del training_data[load_folder]
                training_x, training_y = load_training_folders(working_dir,
                                                               load_folder)
                if training_x is not None:
                    training_data[load_folder] = (training_x, training_y)
                    print("Loaded training data for '{}'.".format(load_folder))
                else:
                    print("Could not load training data for '{}'.".format(
                        load_folder))



        # Build or Load Model
        elif args[0].startswith("m"):
            if len(args) > 1:
                model = load_model(args[1])
                if model is None:
                    print(
                        "Could not load existing model folder at '{}'.".format(
                            args[1]))
                else:
                    print("Loaded existing model folder at '{}'.".format(
                        args[1]))
            else:
                model = build_model()
                print("Created new untrained model.")



        # Select Training Data
        elif args[0].startswith("s"):
            training_folders = args[1:]
            del training_x, training_y
            training_x, training_y = [], []
            for training_folder in training_folders:
                if training_folder in training_data:
                    training_x2, training_y2 = training_data[training_folder]
                    training_x.append(training_x2)
                    training_y.append(training_y2)
                    """
                    if training_x is None:
                        training_x, training_y = training_x2, training_y2
                    else:
                        training_x = np.concatenate((training_x, training_x2))
                        training_y = np.concatenate((training_y, training_y2))
                    """
                    print("Selected training data from '{}'.".format(
                        training_folder))
                else:
                    print("No training data found for '{}'. Skipping.".format(
                        training_folder))
            training_x = np.concatenate(training_x)
            training_y = np.concatenate(training_y)
            print(training_x.shape, training_y.shape)



        # Train Model
        elif args[0].startswith("t"):
            output_folder = args[1]
            epochs = int(args[2])
            print("Training current model for {} epochs.".format(epochs))
            model.fit(training_x, training_y, epochs=epochs)
            save_model(output_folder, model)
            print("Saved new model to '{}'.".format(output_folder))
