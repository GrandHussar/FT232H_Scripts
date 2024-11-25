import time
import redis
import json
import threading
import board
import busio
from motor_control import MotorController
from sensor_data import SensorDataHandler
from adafruit_bus_device.i2c_device import I2CDevice
from pyftdi.ftdi import FtdiError  # Import for FTDI-specific errors

# Redis setup
redis_client = redis.Redis()

def subscribe_to_control_updates():
    """
    Subscribe to the Redis channel for control updates.
    """
    pubsub = redis_client.pubsub()
    pubsub.subscribe("control_updates")  # Subscribe to the channel

    print("Subscribed to Redis channel. Waiting for updates...")
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                print(f"Received control update: {data}")
                frequency = data.get("frequency", 0)
                intensity = data.get("intensity", 0)

                # Update motor speed based on control data
                print(f"Updating motor with Frequency={frequency} Hz, Intensity={intensity}%")
                motor.set_motor_speed(frequency, intensity)

            except json.JSONDecodeError:
                print("Failed to decode JSON message.")
            except Exception as e:
                print(f"Error processing control update: {e}")

def collect_sensor_data():
    """
    Collect sensor data and send it to Flask.
    """
    try:
        # Initialize I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)

        # Initialize sensor data handler
        sensor = SensorDataHandler(i2c, flask_url="http://localhost:5000/")

        while True:
            try:
                # Collect sensor data and send to Flask
                sensor.collect_data()
            except (OSError, FtdiError) as e:
                print(f"Error collecting sensor data: {e}")
                print("Reinitializing I2C bus...")
                # Attempt to restart I2C bus
                i2c = busio.I2C(board.SCL, board.SDA)  # Re-initialize the I2C bus
                sensor = SensorDataHandler(i2c, flask_url="http://localhost:5000/")
                time.sleep(1)  # Delay before retrying the data collection
            time.sleep(0.5)

    except Exception as e:
        print(f"Error collecting sensor data: {e}")

def main():
    # Initialize I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Initialize motor controller
    global motor
    motor = MotorController(i2c=i2c)

    # Start threads for sensor data collection and Redis subscription
    sensor_thread = threading.Thread(target=collect_sensor_data)
    control_thread = threading.Thread(target=subscribe_to_control_updates)

    # Start both threads
    sensor_thread.daemon = True  # Allow thread to exit when the main program exits
    control_thread.daemon = True  # Allow thread to exit when the main program exits

    sensor_thread.start()
    control_thread.start()

    # Keep the main thread alive to let other threads run
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting program.")
