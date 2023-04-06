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


class Grid:
    """
    class that creates a grid of people and assigns suspicion levels to each person
    """

    def __init__(self, n, p, distribution_of_group_1, distribution_of_group_2, distribution_of_group_3, L):
        """
        :param n: size of grid
        :param p: probability of a person existing in a cell
        :param distribution_of_group_1:  distribution of suspicion levels for group 1
        :param distribution_of_group_2: distribution of suspicion levels for group 2
        :param distribution_of_group_3: distribution of suspicion levels for group 3
        :param L: number of generations a person will not spread a rumor after spreading it
        """
        self.n = n
        self.p = p
        self.s1 = distribution_of_group_1
        self.s2 = distribution_of_group_2
        self.s3 = distribution_of_group_3
        self.L = L
        # create grid, suspicion grid, and people grid. ****** possibly easier to make a 3D tensor where each layer is
        # a grid
        self.grid = np.zeros((n, n))
        self.suspicion_grid = np.zeros((n, n))
        self.people_grid = np.zeros((n, n))
        # create lists for each group
        self.group_1 = []
        self.group_2 = []
        self.group_3 = []
        self.group_4 = []
        # create rumor spreaders
        self.rumor_spreader_1 = None
        self.rumor_spreader_2 = None
        self.rumor_spreader_3 = None
        self.rumor_spreader_4 = None
        # generation counter
        self.generation = 0

    def create_grid(self):
        """
        create grid of people by iterating over the grid and assigning people to each cell with probability p
        """
        for i in range(self.n):
            for j in range(self.n):
                if random.random() < self.p:
                    # assign person to cell
                    self.grid[i, j] = 1
                    # create person object
                    self.people_grid[i, j] = Person(i, j)

    def create_suspicion_grid(self):
        """
        create suspicion grid by iterating over the grid and assigning suspicion levels to each person
        """
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i, j]:
                    # assign suspicion level to person
                    # this sets the suspicion level of the person object and returns the suspicion level of the person
                    # to assign to the suspicion grid
                    self.suspicion_grid[i, j] = self.give_suspicion_type(self.people_grid[i, j])
                    if self.suspicion_grid[i, j] == 1:
                        self.group_1.append(self.people_grid[i, j])
                    elif self.suspicion_grid[i, j] == 2:
                        self.group_2.append(self.people_grid[i, j])
                    elif self.suspicion_grid[i, j] == 3:
                        self.group_3.append(self.people_grid[i, j])
                    elif self.suspicion_grid[i, j] == 4:
                        self.group_4.append(self.people_grid[i, j])

    def give_suspicion_type(self, person):
        """
        assign suspicion level to person object
        :param person: the person whose suspicion level is being assigned
        :return: the suspicion level assigned to the person
        """
        r = random.random()
        if r < self.s1:
            person.set_suspicion(1)
            return 1
        elif r < self.s1 + self.s2:
            person.set_suspicion(2)
            return 2
        elif r < self.s1 + self.s2 + self.s3:
            person.set_suspicion(3)
            return 3
        else:
            person.set_suspicion(4)
            return 4

    def create_rumor_spreader(self):
        """
        select a random person from each group to be the rumor spreader and set their suspicion level to 1
        """
        # select a random person from each group to be the rumor spreader
        self.rumor_spreader_1 = random.choice(self.group_1).rumor_starter()
        self.rumor_spreader_2 = random.choice(self.group_2).rumor_starter()
        self.rumor_spreader_3 = random.choice(self.group_3).rumor_starter()
        self.rumor_spreader_4 = random.choice(self.group_4).rumor_starter()


class Person:
    """
    class that creates a person object
    """

    def __init__(self, i, j):
        """
        :param i: x coordinate of person
        :param j: y coordinate of person
        """
        self.__i = i
        self.__j = j
        self.rumor_spreader = False
        self.rumor_received = False
        self.rumor_spread = False
        self.sum_of_suspicion = 0
        self.__suspicion = 0
        self.generation = 0

    def get_x(self):
        return self.__i

    def get_y(self):
        return self.__j

    def get_suspicion(self):
        return self.__suspicion

    def rumor_starter(self):
        """
        function for when a person is chosen to start a rumor.
        set suspicion level to 1 and set rumor_spreader to True
        :return:
        """
        self.sum_of_suspicion = 1
        self.rumor_spreader = True

    def set_suspicion(self, suspicion_level):
        """
        :param suspicion_level: the suspicion level to be assigned to the person
        """
        if suspicion_level == 1:
            self.__suspicion = 1
        elif suspicion_level == 2:
            self.__suspicion = 2
        elif suspicion_level == 3:
            self.__suspicion = 3
        elif suspicion_level == 4:
            self.__suspicion = 4

    def spread(self, grid, n, L):
        if self.rumor_received:
            if self.sum_of_suspicion > 0:
                if not self.rumor_spread:
                    self.rumor_spread = True
                    self.generation = Person.generation + L
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if 0 <= self.i + i < n and 0 <= self.j + j < n and not (i == 0 and j == 0):
                                grid[self.i + i, self.j + j].receive_rumor(self.belief_increase)
            else:
                self.rumor_received = False


# create main function that asks user for input and runs the simulation
def main():
    # get user input
    n = int(input("Enter the size of the grid: "))
    p = float(input("Enter the p(population density): "))
    s1 = float(input("Enter the percentage of S1: "))
    s2 = float(input("Enter the percentage of S2: "))
    s3 = float(input("Enter the percentage of S3: "))
    L = int(input("Enter the number of generations of silence: "))

    # create grid object
    grid = Grid(n, p, s1, s2, s3, L)
    # create grid
    grid.create_grid()
    # create suspicion grid
    grid.create_suspicion_grid()
    # create rumor spreaders
    grid.create_rumor_spreader()
