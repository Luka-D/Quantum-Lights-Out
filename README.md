# Quantum-Lights-Out

<p align='center'><img src="https://github.com/user-attachments/assets/5fd8765f-530d-41ba-826f-dc68ef659b17" width="75%" height="75%"/></p>

This is a demo for the [RasQberry Two Platform](https://rasqberry.org/). It is an implementation of the [Lights Out](<https://en.wikipedia.org/wiki/Lights_Out_(game)>) puzzle game that is solved using a quantum algorithm and then displays every step of the solution process on the RasQberry Two's LED panel. The LED panel is required for this script to run, although you can also have the solution steps printed to the console by adding the `--console` argument.

The git repo for the RasQberry Two Project can be found [here](https://github.com/JanLahmann/RasQberry-Two).

## Acknowledgements

Thank you to the IBM Quantum Challenge 2020 for providing most of the code for the quantum algorithm. More info and tutorials can be found [here](https://github.com/qiskit-community/IBMQuantumChallenge2020/tree/main).

## Command Line Arguments

| Argument         | Default | Description                                                                                |
| ---------------- | ------- | ------------------------------------------------------------------------------------------ |
| -h, --help       | None    | Displays the help message and then exits.                                                  |
| -c, --console    | False   | Displays the lights out grid in the console. (bool)                                        |
| --delay          | 1.0     | Sets the delay (in seconds) between iteration steps for the LED array and console. (float) |
| -b, --brightness | 1.0     | Sets the brightness of the LEDs. Accepts ranges between 0.0 and 1.0. (float)               |

## Installation

Install all the necessary dependencies using pip:

```python
pip install -r requirements.txt
```

## How to Run

Run the script using:

```python
python3 lights_out.py
```

To run the script with console printing of every step, use:

```python
python3 lights_out.py --console
```

Additionally, to turn off all of the LEDs, you can run this script:

```python
python3 turn_off_LEDs.py
```

**! Note:** To run this script on a Raspberry Pi 5, you need to have SPI set up and use the proper wiring configuration. Instructions for wiring and setting up SPI can be found [here](https://rasqberry.org/3d-model/hardware-assembly-guide).
