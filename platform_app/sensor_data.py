import time
import math
import requests
from datetime import datetime
import adafruit_adxl34x

class SensorDataHandler:
    def __init__(self, i2c, flask_url, threshold=1.0, sampling_interval=0.1):
        self.accelerometer = adafruit_adxl34x.ADXL345(i2c)
        self.flask_url = flask_url
        self.threshold = threshold
        self.sampling_interval = sampling_interval
        self.last_peak_time = 0
        self.previous_acceleration = 0

    def calculate_magnitude(self, x, y, z):
        return math.sqrt(x**2 + y**2 + z**2)

    def calculate_frequency(self, current_acceleration, current_time):
        frequency = 0
        if current_acceleration > self.previous_acceleration and current_acceleration > self.threshold:
            if self.last_peak_time != 0:
                time_between_peaks = current_time - self.last_peak_time
                frequency = 1 / time_between_peaks
            self.last_peak_time = current_time
        self.previous_acceleration = current_acceleration
        return frequency

    def send_data_to_flask(self, frequency, intensity, timestamp):
        url = f"{self.flask_url}api/vibration"
        data = {
            "frequency": frequency,
            "intensity": intensity,
            "timestamp": timestamp
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print("Data saved successfully!")
            else:
                print(f"Failed to save data: {response.status_code}")
                try:
                    print(response.json())
                except ValueError:
                    print("Error response is not in JSON format:", response.text)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def collect_data(self):
        x, y, z = self.accelerometer.acceleration
        magnitude = self.calculate_magnitude(x, y, z)
        current_time = time.time()
        vibration_frequency = self.calculate_frequency(magnitude, current_time)
        timestamp = datetime.utcnow().isoformat()
        self.send_data_to_flask(vibration_frequency, magnitude, timestamp)
        print(f"Acceleration Magnitude: {magnitude:.2f} m/s², Vibration Frequency: {vibration_frequency:.2f} Hz")
        time.sleep(self.sampling_interval)