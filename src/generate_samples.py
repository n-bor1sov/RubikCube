import torch
from copy import deepcopy
import random
import json
from src.env import Cube
import pickle

# Assuming Cube class and move definitions are already provided

def generate_samples(k: int, l: int):
    samples = []
    for _ in range(l):
        cube = Cube()
        actions = []
        # Make random moves up to depth k
        for _ in range(k):
            move_index = random.randint(0, 11)
            cube.move(move_index)
            actions.append(move_index)
            state = (deepcopy(cube.get_state()), deepcopy(actions))
            samples.append(state)

    # Transform samples to dictionary format
    samples_dict = []
    for state, actions in samples:
        sample_dict = {
            "state": [state[0].tolist(), state[1].tolist()],
            "actions": actions
        }
        samples_dict.append(sample_dict)

    # Save the dictionary as a pickle file
    filename = "cube_samples.pkl"
    try:
        with open(filename, 'wb') as f:
            pickle.dump(samples_dict, f)
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

