#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 12:30:45 2024

@author: J. Cabrera-Moreno
Postdoctoral fellow
Evolutionary Cognition Group
Institute of Evolutionary Anthropology
University of Zürich

Explanation:
    The code is in control of constantly monitoring two IR sensors placed in 
    the entrance of the comfortbox challenge. Depending on the sequence of 
    interruption the code will output whether an animal got inside the box
    or outside.
"""

from gpiozero import Button
import time

class IRDirectionDetector:
    def __init__(self, sensor_1_pin, sensor_2_pin):
        """
        Initialize the IRDirectionDetector with two IR sensors.
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
        :param sensor_1_pin: GPIO pin for the first IR sensor (outer sensor).
        :param sensor_2_pin: GPIO pin for the second IR sensor (inner sensor).
        """
        self.sensor_1 = Button(sensor_1_pin)
        self.sensor_2 = Button(sensor_2_pin)
        self.last_event = None

    def detect_movement(self):
        """
        Detect movement and determine if an animal is entering or exiting the tunnel.
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
        :return: Tuple ("In" or "Out", timestamp) or None if no movement detected.
        """
        if self.sensor_1.is_pressed:
            if self.last_event == 'sensor_2':
                self.last_event = None
                return "OUT", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            else:
                self.last_event = 'sensor_1'

        elif self.sensor_2.is_pressed:
            if self.last_event == 'sensor_1':
                self.last_event = None
                return "IN", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            else:
                self.last_event = 'sensor_2'

        return None
<<<<<<< Updated upstream
    
    def log_beam_break(self):
        """
        Detect when a specific beam is broken and log the event with a timestamp.
        Only return a value on a transition from non-broken to broken.

        :return: Tuple ("Sensor 1 Broken" or "Sensor 2 Broken", timestamp) or None
                 if no state change detected.
        """
        sensor_1_current_state = self.sensor_1.is_pressed
        sensor_2_current_state = self.sensor_2.is_pressed

        if sensor_1_current_state and not self.sensor_1_prev_state:
            # Transition from non-broken to broken for Sensor 1
            self.sensor_1_prev_state = True  # Update the previous state
            return "OUTER", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        if sensor_2_current_state and not self.sensor_2_prev_state:
            # Transition from non-broken to broken for Sensor 2
            self.sensor_2_prev_state = True  # Update the previous state
            return "INNER", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        # Reset previous state when sensors are not pressed
        self.sensor_1_prev_state = sensor_1_current_state
        self.sensor_2_prev_state = sensor_2_current_state

        return None
=======
>>>>>>> Stashed changes

if __name__ == "__main__":

    # Define GPIO pins for the sensors
    SENSOR_1_PIN = 17  # Replace with your actual GPIO pin for the outer sensor
    SENSOR_2_PIN = 27  # Replace with your actual GPIO pin for the inner sensor

    # Initialize the TunnelDirectionDetector
    detector = IRDirectionDetector(SENSOR_1_PIN, SENSOR_2_PIN)

    print("Starting Tunnel Direction Detector. Press Ctrl+C to exit.")

    try:
        while True:
            result = detector.detect_movement()
            if result:  # If a movement event is detected
                direction, timestamp = result
                print(f"Animal moved {direction} at {timestamp}")
<<<<<<< Updated upstream
                
            beam_break = detector.log_beam_break()
            if beam_break:  # If a beam break is detected
                sensor, timestamp = beam_break
                print(f"{sensor} at {timestamp}")
                
=======
>>>>>>> Stashed changes
            time.sleep(0.1)  # Small delay to reduce CPU usage
    except KeyboardInterrupt:
        print("Exiting Tunnel Direction Detector.")
