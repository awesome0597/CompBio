# Rumor Spreader
Part A:<br>
The Rumor Spreader program simulates the spread of a rumor through a grid. The program has two separate modes the users
can run, each mode has its unique features:

1. **Simulator mode**: <br>
    this mode provides the user an interactive GUI where the user can accept default values for the set
    of parameters or choose their own set. After submitting the parameters, a graphic window will open displaying the 
    simulation run and the stats. The simulation will advance alone, however there is a “skip to the end” button which
    will give the user the final solution without needing to sit through the simulation. Throughout the simulation stats
    will be provided for the user, showing the current percent of the population exposed to rumor, and at what 
    generation the grid reaches certain percentage milestones.
2. **Research mode**: <br>
    this mode does not provide a GUI for the user and is used for research purposes only. The simulation will go over 
    different (defined beforehand) values for the different parameters, run the different simulations in the background,
    and finally provide a stats file “stats.csv” with each runs’ stats. This file can be used with the code in the 
    graph.py file to generate the graphs used to understand the spreading of the rumor with different parameters. 
    Since every parameter gets looped through, adding many parameters causes the number of simulations to run to grow 
    very quickly. To battle this, we decided to use multiprocessing so many simulations can be run together to save time.

To prevent critical code segments, we used a lock when writing to stats file. 

The people in the grid are defined by their color: S1 – red, S2- blue, S3- green and S4- purple. <br> 
To be able to differentiate between people who heard the rumor and those who didn't, we made the distinction of 
filling the square with the respective color for those who heard the rumor, and for those who didn’t their square is 
filled with a head figure and a dotted question mark.<br>
A person who's spreading the rumor is marked with wider edges. <br>

Part B:
A specific run of the rumor spreader program that positions the S4 group and empty spaces in the shape of spiral to create a slow spreading rate for the rumor.
The set parameters for the run:<br>
* Matrix Size: 100*100
* P = 0.9
* S1 = 0.3
* S2 = 0.28
* S3 = 0.28
* S4 = 0.14
* L = 3
MAX_GEN = 100.<br>
This program can also be run in two modes like the first part.






