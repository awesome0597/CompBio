# crate a 100 X 100 cell grid where people will exist with probability p. each person has a level of suspicion,
# which is a random number between 1 and 4. S4 doesn't believe anyone, S3 believes with probability of 1/3,
# S2 believes with probability of 2/3, S1 believes with probability of 1. the distribution of people is a
# hyperparameter, and the percentage of believers is a hyperparameter. one person from every group is randomly
# selected to be the rumor spreader. the rules of spreading suspicion are as follows: a person spreads a rumor to all
# of their neighbors. a person that receives a rumor from a neighbor will believe it with probability of their
# suspicion level. spreading the rumor is done in the generation following the rumor being received. if a person
# receives a rumor from multiple neighbors, they will believe it with probability of the sum of their suspicion
# levels. a person that spread a rumor won't spread it again for L generations. L being a hyperparameter.

import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib as mpl
import matplotlib.patheffects as path_effects
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import matplotlib.image as mpimg
import matplotlib.font_manager as font_manager
import matplotlib.patheffects as path_effects


class Person:
    generation = 0

    def __init__(self, suspicion_level):
        self.suspicion = suspicion_level
        self.sum_of_suspicion = 0
        self.rumor_received = False
        self.rumor_spread = False


# create a grid of suspicion levels with the same grid as the people grid and percentage of each level as a
# hyperparameter
def create_suspicion_grid(n, p, s1, s2, s3):
    grid = np.zeros((n, n))
    S1 = []
    S2 = []
    S3 = []
    S4 = []
    for i in range(n):
        for j in range(n):
            if random.random() < p:
                grid[i, j] = give_suspicion_type(s1, s2, s3)
                if grid[i, j] == 1:
                    S1.append((i, j))
                elif grid[i, j] == 2:
                    S2.append((i, j))
                elif grid[i, j] == 3:
                    S3.append((i, j))
                elif grid[i, j] == 4:
                    S4.append((i, j))
    return grid


# select suspicion level based on the percentage of each level
def give_suspicion_type(s1, s2, s3):
    r = random.random()
    if r < s1:
        return Person(1)
    elif r < s1 + s2:
        return Person(2)
    elif r < s1 + s2 + s3:
        return Person(3)
    else:
        return Person(4)
