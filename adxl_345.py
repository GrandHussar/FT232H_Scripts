import time
import math
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
threshold = 10.0              # A threshold to detect significant changes in magnitude (adjust as needed)
sampling_frequency = 500.0    # Sampling frequency in Hz (e.g., 500 Hz)

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

# Start real-time data collection
while True:
    # Read the accelerometer's X, Y, Z acceleration values in m/s^2
    x, y, z = accelerometer.acceleration
    
    # Calculate the magnitude of the acceleration
    magnitude = calculate_magnitude(x, y, z)
    
    # Get the current time
    current_time = time.time()
    
    # Calculate the frequency based on peak detection
    vibration_frequency = calculate_frequency(magnitude, current_time)
    
    # Print the magnitude and vibration frequency
    print(f"Acceleration Magnitude: {magnitude:.2f} m/s², Vibration Frequency: {vibration_frequency:.2f} Hz")
    
    # Sleep to achieve the desired sampling frequency
    time.sleep(1 / sampling_frequency)  # Adjust sleep time based on desired frequency
