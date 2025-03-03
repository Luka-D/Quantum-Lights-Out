# https://raspberrypi.stackexchange.com/questions/85109/run-rpi-ws281x-without-sudo
# https://github.com/joosteto/ws2812-spi

# start with python3 RasQ-LED.py

# Basic imports
import subprocess, time, math
from dotenv import dotenv_values

# Import Qiskit classes
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.providers.basic_provider import BasicSimulator
from qiskit_aer import AerSimulator

# Imports for LED array
import board
import neopixel_spi as neopixel

# Constants
config = dotenv_values("/home/pi/RasQberry/rasqberry_environment.env")
N_QUBIT = 16  # int(config["N_QUBIT"])
NUM_PIXELS = 192
PIXEL_ORDER = neopixel.RGB
OFF_COLOR = 0x111111  # Grey
ON_COLOR = 0x0000FF  # Blue

indices = {
    "0": 32,
    "1": 39,
    "2": 40,
    "3": 47,
    "4": 48,
    "5": 55,
    "6": 56,
    "7": 63,
    "8": 33,
    "9": 38,
    "10": 41,
    "11": 46,
    "12": 49,
    "13": 54,
    "14": 57,
    "15": 62,
    "16": 34,
    "17": 37,
    "18": 42,
    "19": 45,
    "20": 50,
    "21": 53,
    "22": 58,
    "23": 61,
    "24": 35,
    "25": 36,
    "26": 43,
    "27": 44,
    "28": 51,
    "29": 52,
    "30": 59,
    "31": 60,
    "32": 156,
    "33": 155,
    "34": 148,
    "35": 147,
    "36": 140,
    "37": 139,
    "38": 132,
    "39": 131,
    "40": 157,
    "41": 154,
    "42": 149,
    "43": 146,
    "44": 141,
    "45": 138,
    "46": 133,
    "47": 130,
    "48": 158,
    "49": 153,
    "50": 150,
    "51": 145,
    "52": 142,
    "53": 137,
    "54": 134,
    "55": 129,
    "56": 159,
    "57": 152,
    "58": 151,
    "59": 144,
    "60": 143,
    "61": 136,
    "62": 135,
    "63": 128,
}


def get_factors(number):
    factor_list = []

    # search for factors, including factor 1 and N_QUBIT itself
    for i in range(1, math.ceil(number / 2) + 1):
        if number % i == 0:
            factor_list.append(i)

    factor_list.append(N_QUBIT)
    return factor_list


# n is the size of the entangled blocks
def simulate_circuit(n):
    # Init Quantum Circuit

    # Create a Quantum Register with n qubits
    qr = QuantumRegister(N_QUBIT)
    # Create a Classical Register with n bits
    cr = ClassicalRegister(N_QUBIT)
    # Create a Quantum Circuit acting on the qr and cr register
    circuit = QuantumCircuit(qr, cr)

    # Setup circuit

    if n == 1:
        print("build circuit without entanglement")
        factor = 1
    elif n == 0 or n == N_QUBIT:
        print("build circuit with complete entanglement")
        factor = N_QUBIT
    else:
        print("build circuit with entangled blocks of size " + str(n))
        factor = n

    # relevant qubits are the first qubits in each subgroup
    relevant_qbit = 0

    for i in range(0, N_QUBIT):
        if (i % factor) == 0:
            circuit.h(qr[i])
            relevant_qbit = i
        else:
            circuit.cx(qr[relevant_qbit], qr[i])

    circuit.measure(qr, cr)

    # Execute Circuit

    # Set the backend
    backend = AerSimulator()

    # Set number of shots
    shots = 1

    # execute the circuit
    transpiled_qc = transpile(circuit, backend=backend)
    job = backend.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts(circuit)
    print(counts)
    measurement = list(counts.items())[0][0]
    print("measurement: ", measurement)

    # Display to LEDs
    display_to_LEDs(measurement)


# alternative with statevector_simulator
# simulator = Aer.get_backend('statevector_simulator')
# result = execute(circuit, simulator).result()
# statevector = result.get_statevector(circuit)
# bin(statevector.tolist().index(1.+0.j))[2:]


def display_to_LEDs(measurement):
    for index, value in enumerate(measurement):
        if value:
            LED_Array_index = indices[str(index)]
            pixels[LED_Array_index] = ON_COLOR
        else:
            LED_Array_index = indices[str(index)]
            pixels[LED_Array_index] = OFF_COLOR
    pixels.show()


def loop(duration):
    print()
    print(
        "RasQ-LED creates groups of entangled Qubits and displays the measurment result using colors of the LEDs."
    )
    print(
        "A H(adamard) gate is applied to the first Qubit of each group; then CNOT gates to create entanglement of the whole group."
    )
    print("The size of the groups starts with 1, then in steps up to all Qubits.")
    print()
    for i in range(duration):
        factors = get_factors(N_QUBIT)
        for factor in factors:
            run_circ(factor)
            time.sleep(3)
    subprocess.call(
        [
            "sudo",
            "python3",
            "/home/pi/RasQberry/demos/bin/RasQ-LED-display.py",
            "0",
            "-c",
        ]
    )


def main():
    try:
        # Neopixel initialization
        spi = board.SPI()

        pixels = neopixel.NeoPixel_SPI(
            spi,
            NUM_PIXELS,
            pixel_order=PIXEL_ORDER,
            brightness=1.0,
            auto_write=False,
        )
        while True:
            player_action = input("select circuit to execute (1/2/3/q) ")
            if player_action == "1":
                simulate_circuit(1)
            elif player_action == "2":
                simulate_circuit(N_QUBIT)
            elif player_action == "3":
                factors = get_factors(N_QUBIT)
                print(factors)
                for factor in factors:
                    simulate_circuit(factor)
                    time.sleep(3)
            elif player_action == "q":
                subprocess.call(
                    [
                        "sudo",
                        "python3",
                        "/home/pi/RasQberry/demos/bin/RasQ-LED-display.py",
                        "0",
                        "-c",
                    ]
                )
                quit()
            else:
                print("Please type '1', '2', '3' or 'q'")

    except Exception as e:
        print("An error occured: ", e)


if __name__ == "__main__":
    main()
