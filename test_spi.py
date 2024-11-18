import board
import digitalio
import time

# Initialize CS pin
cs = digitalio.DigitalInOut(board.D4)  # Chip Select pin
cs.direction = digitalio.Direction.OUTPUT
cs.value = True  # Start with CS inactive

# Toggle CS pin
print("Toggling CS pin...")
for i in range(10):
    cs.value = False  # Activate CS
    print(f"CS Pin (Active): {cs.value}")  # Should print False
    time.sleep(0.5)  # Delay for observation

    cs.value = True  # Deactivate CS
    print(f"CS Pin (Inactive): {cs.value}")  # Should print True
    time.sleep(0.5)  # Delay for observation
