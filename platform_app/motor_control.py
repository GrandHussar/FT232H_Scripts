import adafruit_pca9685

class MotorController:
    def __init__(self, i2c, frequency=1000, channel=0, max_frequency=100):
        """
        Initialize the motor controller.
        
        Args:
            i2c: I2C bus instance.
            frequency (int): PWM frequency for the PCA9685.
            channel (int): PCA9685 channel for motor control.
            max_frequency (float): Maximum supported vibration frequency (e.g., 100 Hz).
        """
        self.pca = adafruit_pca9685.PCA9685(i2c)
        self.pca.frequency = frequency
        self.channel = channel
        self.max_frequency = max_frequency  # Maximum frequency in Hz

    def set_motor_speed(self, frequency, acceleration):
        """
        Set the motor speed using PWM duty cycle based on frequency and acceleration.

        Args:
            frequency (float): Desired vibration frequency in Hz (0–100 Hz).
            acceleration (float): Desired acceleration as a percentage (0–100%).
        """
        # Normalize frequency (0–100 Hz mapped to 0–1)
        normalized_frequency = min(frequency / self.max_frequency, 1.0)

        # Normalize acceleration (percentage mapped to 0–1)
        normalized_acceleration = min(acceleration / 100.0, 1.0)

        # Calculate the duty cycle (0–65535) based on both frequency and acceleration
        duty_cycle = int(65535 * normalized_frequency * normalized_acceleration)

        # Apply the duty cycle to the motor
        self.pca.channels[self.channel].duty_cycle = duty_cycle

        print(f"Motor Control: Frequency={frequency:.2f} Hz, Acceleration={acceleration:.2f}%, Duty Cycle={duty_cycle}")
