# True Random Number Generator (TRNG) Data Collector

This Python application is designed for a Raspberry Pi with a TRNG device (TrueRNG, TrueRNGpro, or TrueRNGoroV2). It reads in a number of bits from the TRNG at a user-specified interval and counts the number of 'ones'. The datetime and count are then stored in a .csv file and the bits collected are appended to a .bin file for control.


## Requirements

- Raspberry Pi with Python3 installed (https://www.tomshardware.com/reviews/raspberry-pi-headless-setup-how-to,6028.html - Refer to this guide if you want to setup a headless Raspberry Pi)
- A TRNG device (TrueRNG)
- Python 3.x
- lxterminal package installed (default in most Raspberry Pi distributions)
- The following Python packages: **bitstring**, **python-dotenv**, **pyserial**.

## Setup

1. Clone the repository in your Desktop folder:
> 
    git clone https://github.com/Thiagojm/rasp_rng.git

2. Install the required packages if they are not already installed: 
>
    pip install bitstring python-dotenv pyserial

3. In the root folder edit the `variables.env` to specify the sample size (in bits), the interval between samples, the duration for each data collection cycle, and the paths for the temporary folder. 

4. Give execute permissions to the scripts:

>
    chmod +x /path/to/rasp_rng.py  

5. Create an autostart entry:

> 
    sudo nano /home/pi/.config/autostart/rasp_rng.desktop

6. Insert the following content into the .desktop file, changing the path to the path of your script, save and exit the file:

>
    [Desktop Entry]
    Type=Application
    Name=RaspRNG
    Exec=/usr/bin/lxterminal -e "python3 /path/to/rasp_rng.py; bash"

 
7. Make the .desktop file executable:

>
    sudo chmod +x /home/pi/.config/autostart/rasp_rng.desktop


## Real Time Clock (RTC)

I recommend using a RTC to keep files with correct name and not overwriting old ones.
Check: https://pimylifeup.com/raspberry-pi-rtc/

## Usage

The scripts will run automatically on startup.

## Support

If you encounter any problems or have any suggestions, please open an issue or a pull request.

## License

This project is open source, under the MIT license.