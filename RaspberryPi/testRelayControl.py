from gpiozero import OutputDevice
from time import sleep

# Define the GPIO pin number
relay_pin = 4  # GPIO 4

# Create an OutputDevice object for the relay
relay = OutputDevice(relay_pin)

try:
    while True:
        # Turn the relay ON
        relay.on()
        print("Relay ON")
        sleep(5)  # Keep the relay on for 5 seconds

        # Turn the relay OFF
        relay.off()
        print("Relay OFF")
        sleep(5)  # Keep the relay off for 5 seconds

except KeyboardInterrupt:
    pass  # Exit on Ctrl+C