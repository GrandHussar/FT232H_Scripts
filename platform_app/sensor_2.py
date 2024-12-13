import time
import math
import requests
from datetime import datetime
import sys
import adafruit_adxl34x

class SensorDataHandler:
    def __init__(self, i2c, flask_url, threshold=1.0, sampling_interval=0.001, noise_threshold=0.05):
        """
        Initialize the SensorDataHandler with necessary parameters.
        
        :param i2c: I2C bus for the ADXL345 accelerometer.
        :param flask_url: URL of the Flask API to send data.
        :param threshold: Acceleration threshold for peak detection.
        :param sampling_interval: Time interval between data collection in seconds.
        :param noise_threshold: Threshold to ignore minor noise in acceleration.
        """
        self.accelerometer = adafruit_adxl34x.ADXL345(i2c)
        self.flask_url = flask_url
        self.threshold = threshold
        self.sampling_interval = sampling_interval
        self.noise_threshold = noise_threshold
        self.last_peak_time = 0
        self.previous_z_acceleration = 0
        self.previous_frequency = 0

        # Calibration offsets
        self.x_offset = 0
        self.y_offset = 0
        self.z_offset = 0

        # Calibrate the accelerometer
        self.calibrate_sensor()

    def calibrate_sensor(self):
        """
        Calibrate the accelerometer to determine offsets.
        """
        samples = 100
        x_offset = 0
        y_offset = 0
        z_offset = 0
        print("Calibrating sensor... Please keep it stationary.")
        for _ in range(samples):
            x, y, z = self.accelerometer.acceleration
            x_offset += x
            y_offset += y
            z_offset += z
            time.sleep(0.01)  # Small delay between samples
        self.x_offset = x_offset / samples
        self.y_offset = y_offset / samples
        self.z_offset = z_offset / samples
        print(f"Calibration complete. Offsets: x={self.x_offset:.2f}, y={self.y_offset:.2f}, z={self.z_offset:.2f}")

    def calculate_magnitude(self, x, y, z):
        """
        Calculate the magnitude of the 3D acceleration vector, with calibration applied.

        :param x: Acceleration in the x-axis.
        :param y: Acceleration in the y-axis.
        :param z: Acceleration in the z-axis.
        :return: Magnitude of acceleration.
        """
        # Apply calibration offsets
        x -= self.x_offset
        y -= self.y_offset
        z -= self.z_offset

        # Ignore minor noise
        if abs(x) < self.noise_threshold:
            x = 0
        if abs(y) < self.noise_threshold:
            y = 0
        if abs(z) < self.noise_threshold:
            z = 0

        return math.sqrt(x**2 + y**2 + z**2)

    def calculate_frequency(self, current_z_acceleration, current_time):
        """
        Calculate the vibration frequency based on Z-axis acceleration data.

        :param current_z_acceleration: Current Z-axis acceleration magnitude.
        :param current_time: Current time in seconds.
        :return: Calculated vibration frequency in Hz.
        """
        frequency = self.previous_frequency  # Default to last frequency if no new peak is detected

        # Ignore minor noise in Z-axis acceleration
        if abs(current_z_acceleration) < self.noise_threshold:
            return frequency

        # Detect peaks and calculate frequency
        if current_z_acceleration > self.previous_z_acceleration and current_z_acceleration > self.threshold:
            if self.last_peak_time != 0:
                time_between_peaks = current_time - self.last_peak_time
                frequency = 1 / time_between_peaks if time_between_peaks > 0 else 0
            self.last_peak_time = current_time

        self.previous_z_acceleration = current_z_acceleration
        self.previous_frequency = frequency  # Store the frequency for stability
        return frequency

    def send_data_to_flask(self, frequency, intensity, timestamp):
        """
        Send vibration data to the Flask API.

        :param frequency: Vibration frequency in Hz.
        :param intensity: Acceleration magnitude in m/s².
        :param timestamp: ISO 8601 timestamp.
        """
        url = f"{self.flask_url}api/vibration"
        data = {
            "frequency": frequency,
            "intensity": intensity,
            "timestamp": timestamp
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                sys.stdout.write("\nData saved successfully!")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"\nFailed to save data: {response.status_code}")
                sys.stdout.flush()
                try:
                    print(response.json())
                except ValueError:
                    print("Error response is not in JSON format:", response.text)
        except requests.exceptions.RequestException as e:
            sys.stdout.write(f"\nRequest failed: {e}")
            sys.stdout.flush()


    def collect_data(self):
        """
        Collect acceleration data, calculate frequency and magnitude,
        and update the console output in real-time.
        """
        x, y, z = self.accelerometer.acceleration
        magnitude = self.calculate_magnitude(x, y, z)
        current_time = time.time()
        vibration_frequency = self.calculate_frequency(z, current_time)

        # Update the console output in one line with formatted frequency and time
        sys.stdout.write(
            f"\rAcceleration Magnitude: {magnitude:.2f} m/s², Z-Axis Frequency: {vibration_frequency:.2f} Hz, Time: {current_time:.2f} s"
        )
        sys.stdout.flush()
        time.sleep(self.sampling_interval)


# Example usage
if __name__ == "__main__":
    from board import I2C  # Adjust based on your hardware setup
    i2c = I2C()  # Create I2C instance
    flask_url = "http://127.0.0.1:5000/"  # Replace with your Flask API URL

    sensor_handler = SensorDataHandler(i2c, flask_url)
    try:
        while True:
            sensor_handler.collect_data()
    except KeyboardInterrupt:
        print("\nExiting program.")
