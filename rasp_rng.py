import csv
import serial
import time
from serial.tools import list_ports
from bitstring import BitArray
from datetime import datetime
import os
from dotenv import load_dotenv

# change to script directory
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

def find_rng():
    rng_com_port = None

    # Call list_ports to get com port info
    ports_avaiable = list_ports.comports()

    print("Searching for RNG device...\n")
    for temp in ports_avaiable:
        if '04D8:F5FE' in temp[2]:
            print(f'Found TrueRNG on {temp[0]} \n')
            if rng_com_port == None:        # always chooses the 1st TrueRNG found
                rng_com_port=temp[0]
        if '16D0:0AA0' in temp[2]:
            print(f'Found TrueRNGPro on {temp[0]} \n')
            if rng_com_port == None:        # always chooses the 1st TrueRNG found
                rng_com_port=temp[0]
        if '04D8:EBB5' in temp[2]:
            print(f'Found TrueRNGoroV2 on {temp[0]} \n')
            if rng_com_port == None:        # always chooses the 1st TrueRNG found
                rng_com_port=temp[0]
    if rng_com_port == None:
        print(f'No TrueRNG found.\n')
        
    return rng_com_port

def setup_serial(rng_com_port):
    # Try to setup and open the comport
    ser = serial.Serial(port=rng_com_port, timeout=10)  # timeout set at 10 seconds in case the read fails
            
    # Open the serial port if it isn't open
    if(ser.isOpen() == False):
        ser.open()

    # Set Data Terminal Ready to start flow
    ser.setDTR(True)

    # This clears the receive buffer so we aren't using buffered data
    ser.flushInput()

    return ser

def read_bits(num_bytes, rng):
    # Read the specified number of bytes
    bits = rng.read(num_bytes)

    return bits

def count_ones(bits):
    bit_array = BitArray(bytes=bits)
    return bit_array.count('0b1')

def write_to_csv(count, filename):
    now = datetime.now()

    # Format datetime to look like "2023-07-12T16:35:12"
    formatted_now = now.strftime("%Y%m%dT%H:%M:%S")

    # Open the CSV file in append mode
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        # Write the current datetime and the count of ones
        writer.writerow([formatted_now, count])

def write_to_bin(bits, filename):
    # Open the binary file in append mode
    with open(filename, 'ab') as file:
        file.write(bits)


def load_environment_variables():
    load_dotenv('variables.env')
    num_bits = int(os.getenv('SAMPLE_VALUE'))  # in bits
    interval = int(os.getenv('INTERVAL_VALUE'))  # interval in seconds
    sample_duration = int(os.getenv('SAMPLE_DURATION'))  # duration in seconds
    temp_folder = os.getenv('TEMP_FOLDER')
    return num_bits, interval, sample_duration, temp_folder


def check_and_create_folders(temp_folder):
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)


def get_rng_and_filename(num_bits, interval):
    rng_com_port = find_rng()
    if rng_com_port is None:
        print('No RNG device found. Exiting.')
        return None, None

    rng = setup_serial(rng_com_port)

    # Get current datetime and format it
    now = datetime.now()
    formatted_now = now.strftime("%Y%m%dT%H%M%S")

    # Create base filename with pi serial and current datetime
    filename_base = f'{formatted_now}_trng_s{num_bits}_i{interval}'  # 'pi_serial_2023-07-12T16:35:12_trng_s1000000_i0.1

    return rng, filename_base


def update_filename(num_bits, interval):
    now = datetime.now()
    formatted_now = now.strftime("%Y%m%dT%H%M%S")
    filename_base = f'{formatted_now}_trng_s{num_bits}_i{interval}'
    return filename_base


def main():
    num_bits, interval, sample_duration, temp_folder = load_environment_variables()
    check_and_create_folders(temp_folder)

    rng, filename_base = get_rng_and_filename(num_bits, interval)

    if rng is None:
        return

    start_time = time.time()
    num_loop = 1
    total_bytes = 0
    while True:
        current_time = time.time()
        if current_time - start_time >= sample_duration:
            num_loop = 1
            total_bytes = 0
            filename_base = update_filename( num_bits, interval)
            print(f"Starting new capture...\n")
            print(f"Saving data to file {filename_base}...\n")
            start_time = current_time  # reset the start time
        
        rng.flushInput()
        bits = read_bits(num_bits // 8, rng)
        count = count_ones(bits)
        
        # Write data to files in TEMP_FOLDER
        write_to_csv(count, os.path.join(temp_folder, filename_base + '.csv'))
        write_to_bin(bits, os.path.join(temp_folder, filename_base + '.bin'))

        # Sleep for the remaining time
        total_bytes += num_bits / 8    
        print(f"Collecting data - Loop: {num_loop} - Total bytes collected: {int(total_bytes)}")
        num_loop += 1
        time.sleep(max(interval - (time.time() - current_time), 0))



# Run the main function
if __name__ == '__main__':
    main()

