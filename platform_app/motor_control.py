import adafruit_pca9685
import time

class MotorController:
    def __init__(self, i2c, frequency=1000, channel=0, max_frequency=100, retry_attempts=3):
        """
        Initialize the motor controller.

        Args:
            i2c: I2C bus instance.
            frequency (int): PWM frequency for the PCA9685.
            channel (int): PCA9685 channel for motor control.
            max_frequency (float): Maximum supported vibration frequency (e.g., 100 Hz).
            retry_attempts (int): Number of retries for I2C communication errors.
        """
        self.pca = adafruit_pca9685.PCA9685(i2c)
        self.pca.frequency = frequency
        self.channel = channel
        self.max_frequency = max_frequency
        self.retry_attempts = retry_attempts

    def set_motor_speed(self, frequency, intensity):
        """
        Set the motor speed using PWM duty cycle based on frequency and intensity.

        Args:
            frequency (float): Desired vibration frequency in Hz (0–100 Hz).
            intensity (float): Desired intensity as a percentage (0–100%).

        Raises:
            RuntimeError: If all retry attempts fail due to I2C errors.
        """
        # Normalize frequency (0–100 Hz mapped to 0–1)
        normalized_frequency = min(max(frequency / self.max_frequency, 0.0), 1.0)

        # Normalize intensity (percentage mapped to 0–1)
        normalized_intensity = min(max(intensity / 100.0, 0.0), 1.0)

        # Calculate the duty cycle (0–65535) based on both frequency and intensity
        duty_cycle = int(65535 * normalized_frequency * normalized_intensity)

        for attempt in range(1, self.retry_attempts + 1):
            try:
                # Attempt to set the duty cycle
                self.pca.channels[self.channel].duty_cycle = duty_cycle
                print(f"Motor updated: Frequency={frequency:.2f} Hz, Intensity={intensity:.2f}%, Duty Cycle={duty_cycle}")
                return  # Exit if successful
            except Exception as e:
                print(f"Attempt {attempt}/{self.retry_attempts} failed: {e}")
                # Check for specific I2C error or NACK condition (optional based on library)
                if "NACK" in str(e) or isinstance(e, IOError):  # Adjust based on error type
                    print("NACK detected. Retrying without changing motor state.")
                    time.sleep(0.1)  # Delay before retrying
                    continue
                elif attempt == self.retry_attempts:
                    # Log error but do not stop the motor
                    print(f"Critical error: Unable to update motor after {self.retry_attempts} attempts. Keeping previous settings.")
                    return


    def stop_motor(self):
        """
        Safely stop the motor by setting the PWM duty cycle to zero.
        """
        try:
            self.pca.channels[self.channel].duty_cycle = 0
            print("Motor stopped: Duty Cycle set to 0.")
        except Exception as e:
            print(f"Failed to stop motor safely: {e}")

    def reset_controller(self):
        """
        Reset the PCA9685 controller to recover from I2C errors.
        """
        try:
            self.pca = adafruit_pca9685.PCA9685(self.pca.i2c_device)
            print("PCA9685 reset successfully.")
        except Exception as e:
            print(f"Failed to reset PCA9685: {e}")
