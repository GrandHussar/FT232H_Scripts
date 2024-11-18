import time
import board
import busio
import adafruit_pca9685

# Initialize I2C using FT232H (D0 for SCL, D1 for SDA)
i2c = busio.I2C(board.SCL, board.SDA)

# Create the PCA9685 object for PWM control
pca = adafruit_pca9685.PCA9685(i2c)

# Set PWM frequency (e.g., 1000 Hz for motor control)
pca.frequency = 1000  # Global frequency for all PWM channels (1000 Hz)

# Select the channel for the motor (e.g., channel 0 for PWM control)
motor_channel = 0

# Main loop to control motor speed and frequency
while True:
    # Set motor speed using PWM duty cycle (0 to 65535) for 50% speed
    motor_speed = 65535  # 50% duty cycle (adjust as needed)
    pca.channels[motor_channel].duty_cycle = motor_speed
    
    print(f"Motor Speed: {motor_speed}, Duty Cycle: 50%")

    pca.frequency = 1500  # Change the global frequency for PWM



    time.sleep(2)  # Run for 2 seconds
