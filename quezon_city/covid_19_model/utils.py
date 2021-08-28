import random
import json

def coin_toss(ptrue):
    """
    Generates a pseudo-random choice
    """
    if ptrue == 0: return False
    return random.uniform(0.0, 1.0) <= ptrue

def parse_json(filename):
    content = None
    with open(filename) as file:
        content = json.load(file)
    return content
