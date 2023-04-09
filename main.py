import numpy as np
import random
import tkinter as tk
from tkinter import ttk as ttk
from tkinter import Canvas


class Game:
    def __init__(self, grid):
        self.grid = grid

    def run(self):
        for i in range(100):
            for j in range(100):
                if self.grid.grid[i, j] == 1:
                    self.grid.people_grid[i, j].spread(self.grid.people_grid, self.grid.n)


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
        :param L: number of generations a person will not spread a rumor after spreading it
        """
        self.n = n
        self.p = p
        self.s1 = distribution_of_group_1
        self.s2 = distribution_of_group_2
        self.s3 = distribution_of_group_3
        # self.L = L
        # create grid, suspicion grid, and people grid. ****** possibly easier to make a 3D tensor where each layer is
        # a grid
        self.grid = np.zeros((n, n))
        self.suspicion_grid = np.zeros((n, n))
        self.people_grid = np.empty((n, n), dtype=object)
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
        # self.generation = 0

    def get_location(self):
        return self.__i, self.__j

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
        self.belief_increase()

    def belief_increase(self):
        """
        function for when a person receives a rumor
        """
        # raise the sum of suspicion by the suspicion level of the person who spread the rumor, if sum of suspicion
        # is more than 1, set it to 1
        self.sum_of_suspicion += self.__suspicion
        if self.sum_of_suspicion > 1:
            self.sum_of_suspicion = 1

    def spread(self, grid, n):
        if self.rumor_received:
            # can spread rumor if generation equals 0
            # if self.generation == 0:
            if not self.rumor_spread:
                if random.random() < self.sum_of_suspicion:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if 0 <= self.i + i < n and 0 <= self.j + j < n and not (i == 0 and j == 0):
                                grid[self.i + i, self.j + j].receive_rumor()
                self.rumor_spread = True
                # self.generation = L
                self.rumor_received = False
            # else:
            #     self.generation -= 1  # decrement generation


def submit(entries):
    # don't forget to add L
    grid = Grid(int(entries[0].get()), float(entries[1].get()), float(entries[2].get()), float(entries[3].get()),
                float(entries[4].get()))
    # create grid
    grid.create_grid()
    # create suspicion grid
    grid.create_suspicion_grid()
    # create rumor spreaders
    grid.create_rumor_spreader()
    # spread rumor
    grid.spread_rumor()
    # create game
    game = Game(grid)
    # start running
    game.run()


# create main function that asks user for input and runs the simulation
def main():
    root = tk.Tk()
    root.title("I Heard a Rumor?")
    root.geometry("300x200")
    # this will create a label widget
    label_text = ["Enter the size of the grid:", "Enter P (Population Density):", "Enter Percentage of S1:",
                  "Enter Percentage of S2:", "Enter Percentage of S3:", "Enter L:"]
    labels = []
    for i in range(0, 6):
        labels.append(tk.Label(root, text=label_text[i]))
        # rows and columns as specified
        # grid method to arrange labels in respective
        labels[i].grid(row=i, column=0, sticky=tk.W, pady=2)

    default_entries = ["100", "0.7", "0.5", "0.2", "0.2", "0"]
    entries = []
    for i in range(0, 6):
        entries.append(tk.Entry(root))
        # default text inside entry box
        entries[i].insert(0, default_entries[i])
        # this will arrange entry widgets
        entries[i].grid(row=i, column=1, pady=2)

    ttk.Button(root, text='Quit', command=root.destroy).grid(row=6, column=1, sticky=tk.W, pady=2)
    ttk.Button(root, text='Submit', command=lambda: [submit(entries), root.destroy()]).grid(row=6, column=0,
                                                                                            sticky=tk.E, pady=2)
    root.mainloop()


if __name__ == "__main__":
    main()
