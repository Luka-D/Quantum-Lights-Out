## Load Custom Grid
def load_custom_grid():
    with open('custom_grid.txt', 'r') as file:
        data = file.read()

    # Split by commas, strip whitespace, and convert to int
    array = [int(x.strip()) for x in data.split(',') if x.strip().isdigit()]
    print(array)
