#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 15:22:45 2024

@author: J. Cabrera-Moreno
Evolutionary Cognition Group
Institute of Evolutionary Anthropology
University of Zürich

Description:
    Test the feasibility of the IR Beams
"""

from gpiozero import Button

# Define the GPIO pin connected to the receiver's blue wire
RECEIVER_GPIO_PIN = 17  # Replace with your chosen GPIO pin

# Set up the receiver as a button input
beam = Button(RECEIVER_GPIO_PIN)

def beam_broken():
    print("Beam is broken!")

def beam_restored():
    print("Beam is restored!")

# Attach event handlers
beam.when_pressed = beam_broken  # Triggered when the beam is interrupted
beam.when_released = beam_restored  # Triggered when the beam is restored

print("Monitoring IR beam. Press Ctrl+C to exit.")
try:
    while True:
        pass  # Keeps the program running
except KeyboardInterrupt:
    print("Exiting.")