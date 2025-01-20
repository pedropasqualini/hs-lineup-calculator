import pandas as pd
import random as rd
from tqdm import tqdm
from loguru import logger
from copy import deepcopy
from configuration import RANDOM_TARGET, NUM_ITERACTIONS

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

# Alters frequency of a lineup sometimes
def alter_num_line(line, classes):
    change = 0
    for deck in range(4):
        if (classes[line[deck]][1] > classes[line[deck]][0]):
            change += 1
        elif (classes[line[deck]][0] > classes[line[deck]][1]):
            change -= 1
    
    if (change > 0):
        if change > rd.randrange(RANDOM_TARGET):
            line[4] += 1
            for deck in range(4):
                classes[line[deck]][0] += 1
        
    if (change < 0):
        if (line[4] == 0):
            return
        change = -change
        if change > rd.randrange(RANDOM_TARGET):
            line[4] -= 1
            for deck in range(4):
                classes[line[deck]][0] -= 1

# Generates Artificial Field of about 400 lineups close to a bell curve of all possibilities given archetypes frequency
# Real world has bias, but this aproximation works well
def generate_field(deck_pct, lineups):
    lineups_tmp = deepcopy(lineups)
    classes = {}
    for deck in deck_pct.index:
        classes[deck] = [0, deck_pct[deck]*4]

    for line in lineups_tmp:
        line.append(0)
    
    for _ in tqdm(range(NUM_ITERACTIONS), desc="Generating field..."):
        for line in lineups_tmp:
            alter_num_line(line, classes)
        
    elements_to_remove = []
    
    for i in range(len(lineups_tmp)):
        if lineups_tmp[i][4] == 0:
            elements_to_remove.append(i)

    for element in elements_to_remove[::-1]:
        lineups_tmp.pop(element)

    df = pd.DataFrame(lineups_tmp)
    return df
