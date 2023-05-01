import copy
import numpy as np
import random
import tkinter as tk
import time
from tkinter import ttk as ttk
from tkinter import Canvas
import copy
import os
import multiprocessing
import pandas as pd
import threading


class LongGame(tk.Tk):
    """
    The main application window.
    """

    def __init__(self, params, width_and_height=750):
        """
        :param params:  list of parameters
        :param width_and_height:  width and height of the application window
        """

        super().__init__()
        self.title("I Heard a Rumor")

        # Prevent the application window from being resized.
        self.resizable(False, False)

        # Set the height and width of the application.
        self.width_and_height = width_and_height
        self.resolution = params[0]
        self.size_factor = self.width_and_height / self.resolution

        # Set up the size of the canvas.
        self.geometry(str(self.width_and_height) + "x" + str(800))

        # create frame
        self.info_frame = tk.Frame(self)
        self.info_frame.pack()
        self.right_frame = tk.Frame(self.info_frame)
        self.left_frame = tk.Frame(self.info_frame)
        self.right_frame.grid(row=0, column=1)
        self.left_frame.grid(row=0, column=0)
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack()

        # create skip to end button
        self.next_skip_end = ttk.Button(self.left_frame, text="Skip to End", command=self.skip_to_end)
        self.next_skip_end.grid(row=1, column=0)
        # create quit button
        self.quit_button = ttk.Button(self.left_frame, text="Quit", command=self.destroy)
        self.quit_button.grid(row=2, column=0)

        # create stat box
        self.stat_box = tk.Text(self.right_frame, height=8, width=60)
        self.stat_box.pack()
        self.generation_50 = None
        self.generation_25 = None
        self.generation_75 = None

        # Create the canvas widget and add it to the Tkinter application window.
        self.canvas = Canvas(self.canvas_frame, width=self.width_and_height, height=self.width_and_height, bg='white')
        self.canvas.pack()

        # create color index
        self.color_index = {1: 'red', 2 / 3: 'blue', 1 / 3: 'green', 0: 'purple'}

        # create grid
        self.grid = Grid(params[0], params[1], params[2], params[3], params[4])
        self.L_params = params[5]
        self.grid.create_grid(self.L_params)
        # create rumor spreaders
        self.grid.create_rumor_spreader()
        # set generation limit
        self.generation_limit = params[6]
        # first generation
        self.generate_board()
        self.update()
        time.sleep(0.5)
        # spread rumor
        self.grid.spread_rumor()
        self.generate_board()
        self.update()

        while self.grid.generation <= self.generation_limit:
            time.sleep(0.005)
            self.next_generation()
            self.update()

    def generate_board(self):
        """
        Generate the board.
        """
        for x in range(0, self.resolution):
            for y in range(0, self.resolution):
                realx = x * self.size_factor
                realy = y * self.size_factor
                if (x, y) in self.grid.people_coords:
                    self.draw_square(realx, realy, self.size_factor, self.grid.people_grid[x, y])
        self.update_stat_box()

    def draw_square(self, y, x, size, person):
        """
        Draw a square on the canvas.
        :param y:  y coordinate
        :param x:   x coordinate
        :param size:  size of square
        :param person:  person object
        """
        # draw a square on the canvas, if the person has received the rumor, make the box striped
        if person.rumor_spread:
            self.canvas.create_rectangle(x, y, x + size, y + size,
                                         fill=self.color_index[max(person.get_suspicion(),
                                                                   person.get_sum_of_suspicion())],
                                         outline='black', width=3)
        else:
            if person.rumor_received:
                self.canvas.create_rectangle(x, y, x + size, y + size,
                                             fill=self.color_index[max(person.get_suspicion(),
                                                                       person.get_sum_of_suspicion())], outline='black')
            else:
                self.canvas.create_rectangle(x, y, x + size, y + size,
                                             fill=self.color_index[max(person.get_suspicion(),
                                                                       person.get_sum_of_suspicion())], outline='black',
                                             stipple='questhead')

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
        self.canvas.delete("all")
        self.grid.generation += 1
        self.generate_board()

    def update_stat_box(self):
        """
        update the stat box
        """
        # Clear the contents of the stat box.
        self.stat_box.delete('1.0', tk.END)

        # add grid stats.csv to stat box
        self.stat_box.insert(tk.END, "population density: " + str(self.grid.p) + "\n")
        self.stat_box.insert(tk.END, "L param " + str(self.L_params) + "\n")
        # add "game stats.csv" to stat box in bold font underlined
        self.stat_box.insert(tk.END, "Game stats.csv:\n", 'underline')
        self.stat_box.tag_configure('underline', underline=True)

        # compute each generation, what the percent of people who received the rumor is
        self.stat_box.insert(tk.END, "Generation: " + str(self.grid.generation) + "\n")
        rumor_received = 0
        total_people = len(self.grid.people_coords)
        for x, y in self.grid.people_coords:
            if self.grid.people_grid[x, y].rumor_received:
                rumor_received += 1
        percent_received = round(rumor_received / total_people * 100, 2)
        self.stat_box.insert(tk.END, "Percent of people who received the rumor: " + str(percent_received) + "%\n")

        # calculate which generation the population reach 25% rumor received
        if percent_received >= 25:
            if self.generation_25 is None:
                self.generation_25 = self.grid.generation
            self.stat_box.insert(tk.END, "Generation 25% rumor received: " + str(self.generation_25) + "\n")

        # calculate which generation the population reach 50% rumor received
        if percent_received >= 50:
            if self.generation_50 is None:
                self.generation_50 = self.grid.generation
            self.stat_box.insert(tk.END, "Generation 50% rumor received: " + str(self.generation_50) + "\n")

        # calculate which generation the population reach 75% rumor received
        if percent_received >= 75:
            if self.generation_75 is None:
                self.generation_75 = self.grid.generation
            self.stat_box.insert(tk.END, "Generation 75% rumor received: " + str(self.generation_75) + "\n")

    def skip_to_end(self):
        """
        skip to the end of the simulation
        """
        while self.grid.get_generation() < self.generation_limit - 1:
            self.next_generation()


class ShortGame():
    """
    The main application window.
    """

    def __init__(self, params):
        """
        :param params:  list of parameters
        :param width_and_height:  width and height of the application window
        """

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
        if self.percent_received >= 25:
            if self.generation_25 is None:
                self.generation_25 = self.grid.generation

        # calculate which generation the population reach 50% rumor received
        if self.percent_received >= 50:
            if self.generation_50 is None:
                self.generation_50 = self.grid.generation

        # calculate which generation the population reach 75% rumor received
        if self.percent_received >= 75:
            if self.generation_75 is None:
                self.generation_75 = self.grid.generation
            # self.stat_box.insert(tk.END, "Generation 75% rumor received: " + str(self.generation_75) + "\n")


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

    board = ShortGame(entries)


def submit(entries, root, shortGame):
    """
    function that gets the user input from the entries
    :param entries: user input
    :param root: root window
    """
    # don't forget to add L
    params = [int(entries[0].get()), float(entries[1].get()), float(entries[2].get()), float(entries[3].get()),
              float(entries[4].get()), int(entries[5].get()), int(entries[6].get())]
    root.destroy()

    if shortGame:
        games = []
        for i in range(10):
            games.append(params)
        # Create a pool of processes and run the game for each set of entries
        pool = multiprocessing.Pool()
        pool.map(run_game, games)
        pool.close()
        pool.join()
        # stop the run
        print("Done")

    else:
        board = LongGame(params, 600)
        board.mainloop()


def start_menu():
    """
    function that creates the start menu
    """
    root = tk.Tk()
    root.title("I Heard a Rumor?")
    root.geometry("300x230")
    # this will create a label widget
    label_text = ["Enter the size of the grid:", "Enter P (Population Density):", "Enter Percentage of S1:",
                  "Enter Percentage of S2:", "Enter Percentage of S3:", "Enter L:", "Enter Generation Limit:"]
    labels = []
    for i in range(0, len(label_text)):
        labels.append(tk.Label(root, text=label_text[i]))
        # rows and columns as specified
        # grid method to arrange labels in respective
        labels[i].grid(row=i, column=0, sticky=tk.W, pady=2)

    default_entries = ["100", "0.7", "0.2", "0.3", "0.3", "0", "100"]
    entries = []
    for i in range(0, len(label_text)):
        entries.append(tk.Entry(root))
        # default text inside entry box
        entries[i].insert(0, default_entries[i])
        # this will arrange entry widgets
        entries[i].grid(row=i, column=1, pady=2)

    ttk.Button(root, text='Quit', command=root.destroy).grid(row=7, column=1, sticky=tk.W, pady=2)
    ttk.Button(root, text='Simulater', command=lambda: submit(entries, root, False)).grid(row=7, column=0,
                                                                                          sticky=tk.W, pady=2)
    ttk.Button(root, text='Research', command=lambda: submit(entries, root, True)).grid(row=7, column=0,
                                                                                        sticky=tk.E, pady=2)
    root.mainloop()


if __name__ == "__main__":
    start_menu()
