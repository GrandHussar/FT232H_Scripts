import board
import busio

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Scan for I2C devices
while not i2c.try_lock():
    pass

try:
    devices = i2c.scan()
    if devices:
        print("I2C devices found at addresses:", [hex(device) for device in devices])
    else:
        print("No I2C devices found. Check connections!")
finally:
    i2c.unlock()
