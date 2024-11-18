import time
import board
import digitalio
from pyonewire import OneWire

# Set up GPIO for 1-Wire data
gpio_pin = digitalio.DigitalInOut(board.C1)
gpio_pin.direction = digitalio.Direction.INPUT

# Initialize OneWire bus on GPIO pin D2
ow = OneWire(gpio_pin)

# Initialize the DS18B20 sensor
sensor = ow.scan()[0]  # Assuming there's only one sensor connected

def read_temperature():
    # Request temperature measurement
    sensor.convert_temp()
    time.sleep(1)  # Wait for the conversion to complete

    # Read temperature
    temperature = sensor.temperature()
    print(f"Temperature: {temperature}°C")
    return temperature

# Main loop to keep reading temperature
while True:
    temp = read_temperature()
    time.sleep(2)  # Delay to read again after 2 seconds
