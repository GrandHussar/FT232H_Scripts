import time
import math
import requests
import board
import busio
import adafruit_adxl34x
from datetime import datetime  # Import datetime for timestamps

# Initialize I2C bus for FT232H
i2c = busio.I2C(board.SCL, board.SDA)  # Assuming D0 for SCL, D1 for SDA
accelerometer = adafruit_adxl34x.ADXL345(i2c)

# Parameters
last_time = time.time()       # To track time between samples
last_peak_time = 0            # Time of the last detected peak
previous_acceleration = 0     # For peak detection
threshold = 1.0               # A threshold to detect significant changes in magnitude
sampling_interval = 0.5       # Sampling interval set to 0.5 seconds

# Flask Server Information
flask_url = "http://localhost:5000/"

# Function to calculate magnitude of acceleration
def calculate_magnitude(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)

# Function to calculate frequency using peak detection
def calculate_frequency(current_acceleration, current_time):
    global last_peak_time, previous_acceleration
    frequency = 0

    # Detect peak: when acceleration is increasing and exceeds a threshold
    if current_acceleration > previous_acceleration and current_acceleration > threshold:
        if last_peak_time != 0:
            # Calculate the time between peaks (period)
            time_between_peaks = current_time - last_peak_time
            frequency = 1 / time_between_peaks  # Frequency is the inverse of the time interval (Hz)

        # Update the last peak time
        last_peak_time = current_time

    previous_acceleration = current_acceleration  # Update previous acceleration
    return frequency

# Function to send data to Flask app
def send_data_to_flask(frequency, intensity, timestamp):
    url = f"{flask_url}api/vibration"  # Flask API URL

    # Prepare the data to send
    data = {
        "frequency": frequency,
        "intensity": intensity,
        "timestamp": timestamp  # Send with the timestamp included
    }

    try:
        # Send the POST request
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

# Start real-time data collection with reduced frequency
while True:
    # Read the accelerometer's X, Y, Z acceleration values in m/s²
    x, y, z = accelerometer.acceleration

    # Calculate the magnitude of the acceleration
    magnitude = calculate_magnitude(x, y, z)

    # Get the current time
    current_time = time.time()

    # Calculate the frequency based on peak detection
    vibration_frequency = calculate_frequency(magnitude, current_time)

    # Prepare additional data for sending
    intensity = magnitude  # Adjust as needed
    timestamp = datetime.utcnow().isoformat()  # Generate timestamp in ISO 8601 format

    # Send the data to the Flask app
    send_data_to_flask(vibration_frequency, intensity, timestamp)

    # Print the magnitude and vibration frequency
    print(f"Acceleration Magnitude: {magnitude:.2f} m/s², Vibration Frequency: {vibration_frequency:.2f} Hz")

    # Update last_time
    last_time = current_time

    # Sleep to achieve the desired sampling interval (0.5 seconds)
    time.sleep(sampling_interval)
