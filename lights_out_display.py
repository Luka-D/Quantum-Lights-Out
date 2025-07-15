import time

def visualize_solution_on_sensehat(hat, initial_grid, bitstring_solution, delay=1.0):
    """
    Visualizes the Lights Out solution on the Sense HAT LED matrix.
    Displays initial grid, animates presses, and shows final state.

    Args:
        initial_grid (list of int): List of 9 binary values representing lights ON/OFF.
        bitstring_solution (str): 9-bit string from quantum circuit (e.g., '101000010').
        delay (float): Time to wait between animation steps in seconds.
    """

    # Setup
    sense = hat
    sense.clear()

    # Color definitions
    ON_COLOR = (0, 0, 255)       # Blue
    OFF_COLOR = (20, 20, 20)     # Grey
    PRESS_COLOR = (255, 0, 0)    # Red

    # Grid layout mapping to center 3x3 on Sense HAT
    index_map = [
        (2, 2), (2, 3), (2, 4),
        (3, 2), (3, 3), (3, 4),
        (4, 2), (4, 3), (4, 4)
    ]

    # Copy grid
    grid = initial_grid.copy()

    # Helper to display current state
    def display_grid(active_index=None):
        for i, val in enumerate(grid):
            x, y = index_map[i]
            if i == active_index:
                color = PRESS_COLOR
            else:
                color = ON_COLOR if val == 1 else OFF_COLOR
            sense.set_pixel(x, y, color)

    # Helper to toggle value
    def switch(val): return 0 if val == 1 else 1

    # Initial display
    display_grid()
    time.sleep(delay)

    # Execute each press step
    for i, bit in enumerate(bitstring_solution):
        if bit == '1':
            # Highlight the press
            display_grid(active_index=i)
            time.sleep(delay)

            # Toggle self and neighbors
            grid[i] = switch(grid[i])
            neighbors = []

            if i - 3 >= 0: neighbors.append(i - 3)   # above
            if i + 3 < 9:  neighbors.append(i + 3)   # below
            if i % 3 != 0: neighbors.append(i - 1)   # left
            if i % 3 != 2: neighbors.append(i + 1)   # right

            for j in neighbors:
                grid[j] = switch(grid[j])

            # Display updated grid
            display_grid()
            time.sleep(delay)

    # Final state
    display_grid()
