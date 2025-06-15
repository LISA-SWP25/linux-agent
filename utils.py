import yaml
import random

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def choose_random_command(commands):
    return random.choice(commands)
