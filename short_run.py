import copy
import os
import numpy as np
import random
import tkinter as tk
import multiprocessing
import pandas as pd
import threading


class Game(tk.Tk):
    """
    The main application window.
    """

    def __init__(self, params, width_and_height=750):
        """
        Initialize the application.
        :param params:  list of parameters
        :param width_and_height:  width and height of the application window
        """

        super().__init__()

        # Set the height and width of the application.
        self.width_and_height = width_and_height
        self.resolution = params[0]
        self.size_factor = self.width_and_height / self.resolution

        self.generation_50 = None
        self.generation_25 = None
        self.generation_75 = None

        # create grid
        self.lock = threading.Lock()
        self.grid = Grid(params[0], params[1], params[2], params[3], params[4])
        self.L_params = params[5]
        self.grid.create_grid(self.L_params)
        # create rumor spreaders
        self.grid.create_rumor_spreader()
        # set generation limit
        self.generation_limit = params[6]

        # spread rumor
        self.grid.spread_rumor()
        self.percent_received = 0
        self.skip_to_end()

        # save stats
        self.save_stats()
        # quit
        self.destroy()

    def skip_to_end(self):
        """
        Skip to the end of the game.
        """
        while self.grid.generation < self.generation_limit:
            self.update_stat_box()
            self.next_generation()

    def save_stats(self):
        """
        Save the stats.csv to a file.
        """
        with self.lock:
            # create dataframe with columns PID, 25 percentile, 50 percentile, 75 percentile and final percentile
            data = {'L value': [self.L_params],
                    'P value': [self.grid.p],
                    'S1 value': [self.grid.s1],
                    '25 percentile': [self.generation_25],
                    '50 percentile': [self.generation_50],
                    '75 percentile': [self.generation_75],
                    'final percentile': [self.percent_received]}
            df = pd.DataFrame(data)

            # write to stats.csv
            df.to_csv('stats.csv', mode='a', header=not os.path.exists('stats.csv'), index=False)

    def generation(self):
        """
        copy the people grid and iterate over the copy to create the next generation
        """
        copy_people_grid = copy.deepcopy(self.grid.people_grid)
        for i, j in self.grid.people_coords:
            self.grid.people_grid[i, j].spread(copy_people_grid, self.grid.n)
        return copy_people_grid

    def next_generation(self):
        """
        create next generation of people
        :return:
        """
        self.grid.people_grid = self.generation()
        # self.canvas.delete("all")
        self.grid.generation += 1
        # self.generate_board()

    def update_stat_box(self):
        """
        update the stat box
        """
        # calculate the percent of people who received the rumor
        rumor_received = 0
        total_people = len(self.grid.people_coords)
        for x, y in self.grid.people_coords:
            if self.grid.people_grid[x, y].rumor_received:
                rumor_received += 1
        self.percent_received = round(rumor_received / total_people * 100, 2)

        # calculate which generation the population reach 25% rumor received
        if percent_received >= 25:
            if self.generation_25 is None:
                self.generation_25 = self.grid.generation

        # calculate which generation the population reach 50% rumor received
        if percent_received >= 50:
            if self.generation_50 is None:
                self.generation_50 = self.grid.generation

        # calculate which generation the population reach 75% rumor received
        if percent_received >= 75:
            if self.generation_75 is None:
                self.generation_75 = self.grid.generation


class Grid:
    """
    class that creates a grid of people and assigns suspicion levels to each person
    """

    def __init__(self, n, p, distribution_of_group_1, distribution_of_group_2, distribution_of_group_3):
        """
        :param n: size of grid
        :param p: probability of a person existing in a cell
        :param distribution_of_group_1:  distribution of suspicion levels for group 1
        :param distribution_of_group_2: distribution of suspicion levels for group 2
        :param distribution_of_group_3: distribution of suspicion levels for group 3
        """
        self.n = n
        self.p = p
        self.s1 = distribution_of_group_1
        self.s2 = distribution_of_group_2
        self.s3 = distribution_of_group_3
        self.people_grid = np.empty((n, n), dtype=object)
        self.people_coords = []
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

    def create_grid(self, L):
        """
        create grid of people by iterating over the grid and assigning people to each cell with probability p
        """
        for i in range(self.n):
            for j in range(self.n):
                if random.random() < self.p:
                    # create person object
                    self.people_grid[i, j] = Person(i, j, L)
                    r = random.random()
                    if r < self.s1:
                        self.people_grid[i, j].set_suspicion(1)
                        self.group_1.append(self.people_grid[i, j])
                    elif r < self.s1 + self.s2:
                        self.people_grid[i, j].set_suspicion(2)
                        self.group_2.append(self.people_grid[i, j])
                    elif r < self.s1 + self.s2 + self.s3:
                        self.people_grid[i, j].set_suspicion(3)
                        self.group_3.append(self.people_grid[i, j])
                    else:
                        self.people_grid[i, j].set_suspicion(4)
                        self.group_4.append(self.people_grid[i, j])
                    self.people_coords.append((i, j))

    def create_rumor_spreader(self):
        """
        select a random person from each group to be the rumor spreader and set their suspicion level to 1
        """
        # select a random person from each group to be the rumor spreader
        self.rumor_spreader_1 = random.choice(self.group_1)
        self.rumor_spreader_1.rumor_starter()
        self.rumor_spreader_2 = random.choice(self.group_2)
        self.rumor_spreader_2.rumor_starter()
        self.rumor_spreader_3 = random.choice(self.group_3)
        self.rumor_spreader_3.rumor_starter()
        self.rumor_spreader_4 = random.choice(self.group_4)
        self.rumor_spreader_4.rumor_starter()

    def spread_rumor(self):
        """
        spread rumor to neighbors
        """
        # spread rumor to neighbors
        self.rumor_spreader_1.spread(self.people_grid, self.n)
        self.rumor_spreader_2.spread(self.people_grid, self.n)
        self.rumor_spreader_3.spread(self.people_grid, self.n)
        self.rumor_spreader_4.spread(self.people_grid, self.n)

    def get_generation(self):
        return self.generation


class Person:
    """
    class that creates a person object
    """

    def __init__(self, i, j, L):
        """
        :param i: x coordinate of person
        :param j: y coordinate of person
        """
        self.__i = i
        self.__j = j
        self.__L = L
        self.rumor_spreader = False
        self.rumor_received = False
        self.heard_rumor = False
        self.rumor_spread = False
        self.__sum_of_suspicion = 0
        self.__suspicion = 0
        self.generation = 0

    def get_sum_of_suspicion(self):
        return self.__sum_of_suspicion

    def get_location(self):
        return self.__i, self.__j

    def get_L(self):
        return self.__L

    def start_generation(self):
        self.generation += self.__L

    def get_suspicion(self):
        return self.__suspicion

    def rumor_starter(self):
        """
        function for when a person is chosen to start a rumor.
        set suspicion level to 1 and set rumor_spreader to True
        """
        self.__sum_of_suspicion = 1
        self.rumor_spreader = True
        self.rumor_received = True
        self.heard_rumor = True

    def set_suspicion(self, suspicion_level):
        """
        :param suspicion_level: the suspicion level to be assigned to the person
        """
        if suspicion_level == 1:
            self.__suspicion = 1
        elif suspicion_level == 2:
            self.__suspicion = 2 / 3
        elif suspicion_level == 3:
            self.__suspicion = 1 / 3
        elif suspicion_level == 4:
            self.__suspicion = 0

    def receive_rumor(self):
        """
        function for when a person receives a rumor
        """
        self.rumor_received = True
        self.heard_rumor = True
        self.belief_increase()

    def belief_increase(self):
        """
        function for when a person receives a rumor
        """
        # raise the sum of suspicion by the suspicion level of the person who spread the rumor, if sum of suspicion
        # is more than 1, set it to 1
        self.__sum_of_suspicion += self.__suspicion
        if self.__sum_of_suspicion > 1:
            self.__sum_of_suspicion = 1

    def spread(self, grid, n):
        """
        spread rumor to neighbor
        :param grid:  the grid of people
        :param n:  the size of the grid
        """
        location = self.get_location()
        if self.heard_rumor and self.generation == 0:
            if not self.rumor_spread:
                if random.random() < self.__sum_of_suspicion:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if 0 <= location[0] + i < n and 0 <= location[1] + j < n and not (i == 0 and j == 0) and \
                                    grid[location[0] + i, location[1] + j] is not None:
                                grid[location[0] + i, location[1] + j].receive_rumor()

                    grid[location[0], location[1]].rumor_spread = True
                    grid[location[0], location[1]].start_generation()

                grid[location[0], location[1]].heard_rumor = False
                grid[location[0], location[1]].__sum_of_suspicion = 0
            else:
                grid[location[0], location[1]].rumor_spread = False
                grid[location[0], location[1]].heard_rumor = False
                if grid[location[0], location[1]].generation == 0:
                    grid[location[0], location[1]].__sum_of_suspicion = 0
                else:
                    grid[location[0], location[1]].generation -= 1  # decrement generation

        else:
            if self.heard_rumor and self.generation != 0:
                self.heard_rumor = False
                grid[location[0], location[1]].generation -= 1  # decrement generation
                grid[location[0], location[1]].rumor_spread = False
                if grid[location[0], location[1]].generation == 0:
                    grid[location[0], location[1]].__sum_of_suspicion = 0
            else:
                grid[location[0], location[1]].rumor_spread = False


def run_game(args):
    entries = args
    # print process id
    print("Process id: ", os.getpid())
    board = Game(entries)
    board.mainloop()


if __name__ == "__main__":
    L_value = [3, 5]
    P_value = [0.5, 0.65, 0.8, 1]
    S1 = [0.3, 0.4, 0.55]
    S2 = [0.3, 0.2, 0.1]
    S3 = [0.3, 0.2, 0.15]

    games = []
    for L in L_value:
        for P in P_value:
            for i in range(len(S1)):
                for j in range(10):
                    entries = [100, P, S1[i], S2[i], S3[i], L, 100]
                    games.append(entries)

    # Create a pool of processes and run the game for each set of entries
    pool = multiprocessing.Pool()
    pool.map(run_game, games)
    pool.close()
    pool.join()
    # stop the run
    print("Done")

