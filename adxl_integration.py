import time
import math
import requests
import json
import board
import busio
import adafruit_adxl34x

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)  # D0 for SCL, D1 for SDA
accelerometer = adafruit_adxl34x.ADXL345(i2c)

# Parameters
last_time = time.time()       # To track time between samples
last_peak_time = 0            # Time of the last detected peak
previous_acceleration = 0     # For peak detection
threshold = 1.0               # A threshold to detect significant changes in magnitude
sampling_frequency = 500.0    # Sampling frequency in Hz

# Flask Server Information
flask_url = "http://localhost:5000/"
user_id = 1  # The user ID should be dynamic, for now, hardcoded as 1

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

# Function to check if the user has started a simulation
import requests

def get_simulation_status(user_id):
    url = f"http://localhost:5000/api/simulation-status/{user_id}"
    response = requests.get(url)

    # Check if the response status code is 200 (OK)
    if response.status_code == 200:
        try:
            data = response.json()
            return data['simulation_id'], True
        except ValueError:
            print("Error: Response content is not valid JSON.")
            return None, False
    else:
        print(f"Error: Received status code {response.status_code} from the server.")
        return None, False


# Function to send data to Flask app
def send_data_to_flask(frequency, intensity, duration, data_points, simulation_id, user_id, vibration_level):
    url = f"{flask_url}/api/vibration"  # Flask API URL

    # Prepare the data to send
    data = {
        "simulation_id": simulation_id,
        "user_id": user_id,
        "frequency": frequency,
        "intensity": intensity,
        "duration": duration,
        "vibration_level": vibration_level,
        "data_points": data_points  # Ensure this is a dictionary, e.g., {"x": 1, "y": 2, "z": 3}
    }

    try:
        # Send the POST request
        response = requests.post(url, json=data)

        # Check if response is successful (status code 200)
        if response.status_code == 200:
            print("Data saved successfully!")
        else:
            print(f"Failed to save data: {response.status_code}")
            try:
                # Try to print the error message returned by Flask
                print(response.json())
            except ValueError:
                # If the response is not JSON, print the raw text
                print("Error response is not in JSON format:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
# Start real-time data collection
while True:
    # Check if the user has an active simulation
    simulation_id, simulation_active = get_simulation_status(user_id)

    if not simulation_active:
        print("Simulation not active. Waiting for simulation to start.")
        time.sleep(5)
        continue  # Skip data collection if no simulation is active

    # Read the accelerometer's X, Y, Z acceleration values in m/s²
    x, y, z = accelerometer.acceleration
    
    # Calculate the magnitude of the acceleration
    magnitude = calculate_magnitude(x, y, z)
    
    # Get the current time
    current_time = time.time()
    
    # Calculate the frequency based on peak detection
    vibration_frequency = calculate_frequency(magnitude, current_time)

    # Prepare additional data for sending
    intensity = magnitude  # This can be adjusted as needed
    duration = current_time - last_time  # Time since the last sample
    data_points = {"x": x, "y": y, "z": z}  # Store acceleration data for reference
    vibration_level = "High" if magnitude > 20 else "Low"  # Example condition for vibration level
    
    # Send the data to the Flask app
    send_data_to_flask(vibration_frequency, intensity, duration, data_points, simulation_id, user_id, vibration_level)

    # Print the magnitude and vibration frequency
    print(f"Acceleration Magnitude: {magnitude:.2f} m/s², Vibration Frequency: {vibration_frequency:.2f} Hz")
    
    # Sleep to achieve the desired sampling frequency
    time.sleep(1 / sampling_frequency)  # Adjust sleep time based on desired frequency
