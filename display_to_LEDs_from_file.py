# Standard
import json
import argparse

# Imports for LED array
import board
import neopixel_spi as neopixel

# # Neopixel constants
NUM_PIXELS = 192
PIXEL_ORDER = neopixel.RGB


def display_to_LEDs(array_data, args):
    """
    This function takes the RGB values and index position for each pixel in the LED array and
    displays it to the LED array. The display can be adjusted with the following args.

    Args:
        array_data (dict): Data to be displayed to the LED array. In the format of
                           {index #: [R, G, B]} for each pixel.
        console (bool): Determines whether the image is also printed to the console.
        brightness (float): The brightness of the LED pixels.
    Returns:
        None
    """

    # Set all command line args
    console = args.console
    brightness = args.brightness

    # Neopixel initialization
    spi = board.SPI()

    pixels = neopixel.NeoPixel_SPI(
        spi,
        NUM_PIXELS,
        pixel_order=PIXEL_ORDER,
        brightness=brightness,
        auto_write=False,
    )

    # Display to LED array
    for index, color in array_data.items():
        # Get RGB data from pixel list, notice that the LED array is actually in GRB
        green, red, blue = color[0], color[1], color[2]

        # Set the appropriate pixel to the RGB value
        pixels[int(index)] = (red, green, blue)

    pixels.show()

    if console:
        print("LED Array Data:")
        print(array_data)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="The file path of the LED array pixel values",
        required=False,
        type=str,
        default=None,
    )
    parser.add_argument(
        "-c",
        "--console",
        help="Displays the LED array values to the console",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-b",
        "--brightness",
        help="Sets the brightness of LEDs, between 0.0 and 1.0",
        required=False,
        type=float,
        default=1.0,
    )
    return parser.parse_args()


def main(**kwargs):
    args = parse_arguments()

    # Loading from file
    if args.file:
        array_data_file = args.file
    else:
        array_data_file = input(
            "Please drag and drop the file containing the LED color values (txt or json file): "
        )

    try:
        with open(array_data_file) as file:
            array_data = json.load(file)
        print(array_data)
    except Exception as e:
        print("An error occured while loading the file: ", e)
        quit()

    # Displaying to LEDs
    try:
        print("Displaying to LEDs...")
        display_to_LEDs(array_data, args)
        print("Done")
    except Exception as e:
        print("An error occured while displaying to the LEDs: ", e)
        quit()


if __name__ == "__main__":
    main()
