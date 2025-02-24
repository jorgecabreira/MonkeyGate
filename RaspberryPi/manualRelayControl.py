from gpiozero import OutputDevice

# Define the GPIO pin number
relay_pin = 4  # GPIO 4

# Create an OutputDevice object for the relay
relay = OutputDevice(relay_pin)

try:
    while True:
        # Prompt the user for a command
        command = input("Enter 'on' or 'off': ").strip().lower()

        if command == "on":
            relay.on()
            print("Relay turned ON")
        elif command == "off":
            relay.off()
            print("Relay turned OFF")
        else:
            print("Invalid command. Please enter 'on' or 'off'.")

except KeyboardInterrupt:
    pass  # Exit on Ctrl+C
