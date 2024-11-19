# Basic imports
import matplotlib.pyplot as plt
import numpy as np
import math
import time
from random import choice
import argparse

# Qiskit imports
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.visualization import plot_histogram

# from dotenv import load_dotenv
from qiskit.providers.basic_provider import BasicSimulator
from qiskit_aer import AerSimulator

# import basic plot tools
from qiskit.visualization import plot_histogram

# Imports for LED array
# import board
# import neopixel_spi as neopixel

# Array containing the initial lights out grid values
lights = [
    [0, 1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 1, 1],
    [1, 0, 1, 1, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 1],
    [1, 1, 1, 0, 1, 1, 0, 0, 1],
    [0, 1, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 0, 1, 0, 1, 1, 1],
    [0, 1, 0, 0, 1, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 1, 0, 1],
    [0, 1, 1, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 1, 0, 0, 0],
    [1, 0, 1, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
]


# Dictionary that corelates the grid index to an index on the LED array (Centered in the LED array)
# 1,9 - 1,14
# 6,9 - 6,14
LED_array_indices = {
    0: [38, 41, 37, 42],
    1: [46, 49, 45, 50],
    2: [54, 53, 57, 58],
    3: [36, 43, 155, 148],
    4: [44, 51, 147, 140],
    5: [52, 59, 139, 132],
    6: [154, 149, 153, 150],
    7: [146, 141, 145, 142],
    8: [138, 133, 137, 134],
}

# Delay before showing the next iteration
delay = 1


def compute_quantum_solution(lights):
    """
    This function creates a quantum circuit and uses it to compute the solution to the light-sout grid.

    Args:
        lights (list of int): A list of integers each representing one square in the lights-out grid and
                              whether it is on or off.
    Returns:
        quantum_solution (str): A string representing each square in the grid.
                                If a square is 1, it must be pressed to solved the grid.
    """
    # Initialize quantum circuit board
    tile = QuantumRegister(9)
    flip = QuantumRegister(9)
    oracle = QuantumRegister(1)
    auxiliary = QuantumRegister(1)
    result = ClassicalRegister(9)
    # 20 qubit
    qc = QuantumCircuit(tile, flip, oracle, auxiliary, result)

    def map_board(lights, qc, qr):
        j = 0
        for i in lights:
            if i == 1:
                qc.x(qr[j])
                j += 1
            else:
                j += 1

    # Initialize
    def initialize_smart(l, qc, tile):
        map_board(l, qc, tile)
        qc.h(flip[:3])
        qc.x(oracle[0])
        qc.h(oracle[0])

    def flip_1(qc, flip, tile):
        # push 0
        qc.cx(flip[0], tile[0])
        qc.cx(flip[0], tile[1])
        qc.cx(flip[0], tile[3])
        # push 1
        qc.cx(flip[1], tile[0])
        qc.cx(flip[1], tile[1])
        qc.cx(flip[1], tile[2])
        qc.cx(flip[1], tile[4])
        # push 2
        qc.cx(flip[2], tile[1])
        qc.cx(flip[2], tile[2])
        qc.cx(flip[2], tile[5])

    def inv_1(qc, flip, tile):
        # copy 0,1,2
        qc.cx(tile[0], flip[3])
        qc.cx(tile[1], flip[4])
        qc.cx(tile[2], flip[5])

    def flip_2(qc, flip, tile):
        # apply flip[3,4,5]
        qc.cx(flip[3], tile[0])
        qc.cx(flip[3], tile[3])
        qc.cx(flip[3], tile[4])
        qc.cx(flip[3], tile[6])
        qc.cx(flip[4], tile[1])
        qc.cx(flip[4], tile[3])
        qc.cx(flip[4], tile[4])
        qc.cx(flip[4], tile[5])
        qc.cx(flip[4], tile[7])
        qc.cx(flip[5], tile[2])
        qc.cx(flip[5], tile[4])
        qc.cx(flip[5], tile[5])
        qc.cx(flip[5], tile[8])

    def inv_2(qc, flip, tile1):
        # copy 3,4,5
        qc.cx(tile[3], flip[6])
        qc.cx(tile[4], flip[7])
        qc.cx(tile[5], flip[8])

    def flip_3(qc, flip, tile):
        qc.cx(flip[6], tile[3])
        qc.cx(flip[6], tile[6])
        qc.cx(flip[6], tile[7])
        qc.cx(flip[7], tile[4])
        qc.cx(flip[7], tile[6])
        qc.cx(flip[7], tile[7])
        qc.cx(flip[7], tile[8])
        qc.cx(flip[8], tile[5])
        qc.cx(flip[8], tile[7])
        qc.cx(flip[8], tile[8])

    def lights_out_oracle(qc, tile, oracle, auxiliary):
        qc.x(tile[6:9])
        qc.mcx(tile[6:9], oracle[0], auxiliary, mode="basic")
        qc.x(tile[6:9])

    def diffusion(qc, flip):
        qc.h(flip[:3])
        qc.x(flip[:3])
        qc.h(flip[2])
        qc.ccx(flip[0], flip[1], flip[2])
        qc.h(flip[2])
        qc.x(flip[:3])
        qc.h(flip[:3])

    initialize_smart(lights, qc, tile)

    for i in range(2):
        flip_1(qc, flip, tile)
        inv_1(qc, flip, tile)
        flip_2(qc, flip, tile)
        inv_2(qc, flip, tile)
        flip_3(qc, flip, tile)

        lights_out_oracle(qc, tile, oracle, auxiliary)

        flip_3(qc, flip, tile)
        inv_2(qc, flip, tile)
        flip_2(qc, flip, tile)
        inv_1(qc, flip, tile)
        flip_1(qc, flip, tile)

        diffusion(qc, flip)

    # Uncompute
    qc.h(oracle[0])
    qc.x(oracle[0])

    # get the whole solution from the top row of the solution
    # If you get a solution, you don't need to erase the board, so you don't need the flip_3 function.
    flip_1(qc, flip, tile)
    inv_1(qc, flip, tile)
    flip_2(qc, flip, tile)
    inv_2(qc, flip, tile)

    # Measuremnt
    qc.measure(flip, result)

    # Make the Out put order the same as the input.
    qc = qc.reverse_bits()

    backend = AerSimulator()
    transpiled_qc = transpile(qc, backend=backend)
    result = backend.run(transpiled_qc, shots=5000).result()
    counts = result.get_counts()

    score_sorted = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    final_score = score_sorted[0:40]
    quantum_solution = final_score[0][0]
    return quantum_solution


def visualize_lights_out_grid_to_console(grid, selected=None):
    """
    This function prints out the lights-out grid to the console in a nice format.

    Args:
        grid (list of int): A list of integers each representing one square in the lights-out grid and
                            whether it is on or off.
    Returns:
        None
    """
    rows = []
    root = int(math.sqrt(len(grid)))

    # Chunk the list into sub lists based on each row
    chunked_grid = [grid[x : x + root] for x in range(0, len(grid), root)]

    # Iterate through each row and print as an empty or full square
    for row in chunked_grid:
        temp_list = []
        for index, square in enumerate(row):
            if square == 1:
                temp_list.append("\u25A0")
            else:
                temp_list.append("\u25A1")
        rows.append(temp_list)

    # Print final result split by rows to make it looks nice
    print(*rows, sep="\n")
    print("\n")


def visualize_lights_out_grid_to_LED(grid, selected=None):
    """
    This function shows the lights-out grid on the LED arrray.

    Args:
        grid (list of int): A list of integers each representing one square in the lights-out grid and
                            whether it is on or off.
        grid (int): (Optional) The index that is pressed on the board for that step.
    Returns:
        None
    """

    # For later
    # NUM_PIXELS = 192
    # PIXEL_ORDER = neopixel.RGB

    # spi = board.SPI()

    # pixels = neopixel.NeoPixel_SPI(
    #     spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False
    # )

    off_color = (
        0x83209E  # Other colors: 0x7F00FF for Violet, 0xBF40BF for Bright Purple
    )
    on_color = 0x808080  #
    selected_color = 0xFA0100  #

    # Iterate through each row and print as an empty or full square
    for index, square in enumerate(grid):
        LED_array_index_list = LED_array_indices[index]
        if selected != None and index == selected:
            for coord in LED_array_index_list:
                pixels[coord] = selected_color
        elif square == 1:
            for coord in LED_array_index_list:
                pixels[coord] = on_color
        else:
            for coord in LED_array_index_list:
                pixels[coord] = off_color
    pixels.show()
    # Sleep so that the display doesn't change too fast
    time.sleep(delay)


def visualize_solution(grid, solution, console):
    """
    This function receives the lights-out grid and
    the solution to the grid that was generated from the quantum circuit.
    It then applies the solution to the grid by going through each step and flipping the squares appropriately.

    Args:
        grid (list of int): A list of integers each representing one square in the lights-out grid and
                            whether it is on or off.
        solution (string): The sequence of events to be followed to turn the whole grid off. This solution
                           is obtained from the Qiskit code.
        console (bool): Determines whether the lights out grid is also printed to the console during each
                        step.
    Returns:
        None
    """
    # Find square root of the length of the grid
    root = int(math.sqrt(len(grid)))

    # Convert solution to list of ints if it's a string
    if isinstance(solution, str):
        solution = [int(x) for x in solution]

    # Function to switch 1 -> 0 and vice versa
    def switch(square):
        if square:
            square = 0
            return square
        else:
            square = 1
            return square

    # Visualize the grid the first time before operations
    if console:
        visualize_lights_out_grid_to_console(grid)

    # visualize_lights_out_grid_to_LED(grid)
    time.sleep(1)

    for index, step in enumerate(solution):
        if step == 1:
            # Show grid before all squares have been flipped, include the square that is pressed
            if console:
                visualize_lights_out_grid_to_console(grid, index)

            # visualize_lights_out_grid_to_LED(grid, index)

            # Flip the square itself
            grid[index] = switch(grid[index])

            # Flip squares surrounding the square

            # Above
            # Check to make sure negative value doesn't wrap around the list
            if 0 <= (index - root) < len(grid):
                try:
                    grid[index - root] = switch(grid[index - root])
                except:
                    pass

            # Below
            if 0 <= (index + root) < len(grid):
                try:
                    grid[index + root] = switch(grid[index + root])
                except:
                    pass

            # Left
            # if index not in (0, 3, 6):
            if index not in tuple(range(0, len(grid), root)):
                try:
                    grid[index - 1] = switch(grid[index - 1])
                except:
                    pass
            # Right
            # if index not in (2, 5, 8):
            if index not in tuple(range(root - 1, len(grid), root)):
                try:
                    grid[index + 1] = switch(grid[index + 1])
                except:
                    pass

            # Show grid after all squares have been flipped
            if console:
                visualize_lights_out_grid_to_console(grid)

            # visualize_lights_out_grid_to_LED(grid)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--console",
        help="Displays the lights out grid in the console",
        required=False,
        action="store_true",
    )
    return parser.parse_args()


def main(**kwargs):
    args = parse_arguments()
    while True:
        print(lights)
        print("Choosing random grid arrangement...")
        lights_grid = choice(lights).copy()
        print("Grid chosen:", lights_grid)
        print("Computing quantum solution...")
        quantum_solution = compute_quantum_solution(lights_grid)
        print("Quantum solution found!")
        print("Visualizing solution...")
        visualize_solution(lights_grid, quantum_solution, args.console)


if __name__ == "__main__":
    main()
