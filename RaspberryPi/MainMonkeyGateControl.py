#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 16:07:42 2024

@author: J. Cabrera-Moreno
Postdoctoral fellow
Evolutionary Cognition Group
Institute of Evolutionary Anthropology
University of Zürich

Description:
    Main code control for the ComfortBox experiment. takes into account
    the IR beam breaks, the RFID readings and based on that switches ON/OFF
    the IR light. All events are logged to a file with timestamp.
"""
from gpiozero import OutputDevice
from threading import Thread, Event
import os
import time
import binascii
import re

# Local libraries
from IRDirectionDetector import IRDirectionDetector
from DorsetRFID650_Interface import DorsetRFID650_Interface
from FileManager import FileManager

# Define the GPIO pins
# RELAY_PIN = 21     # GPIO pin for the relay
IR_SENSOR_1 = 16  # GPIO pin for the outer sensor
IR_SENSOR_2 = 20  # GPIO pin for the inner sensor

# Initialize devices
# relay = OutputDevice(RELAY_PIN)                          # Initialize relay
detector = IRDirectionDetector(IR_SENSOR_1, IR_SENSOR_2) # Initialize IRDirectionDetector
RFID = DorsetRFID650_Interface(baudrate = 57600)         # Initialize RFID reader

# Initialize file manager
directory =  "~/Documents/Data"  # Replace with pertinent directory
file_logger = FileManager(directory)
column_names = "date,object,state\n"
log_file_path = file_logger.create_file(column_names)
print(f"File created: {log_file_path}")

script_dir = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the currently running script
animalsID_file = "animalsID.csv"
animalID_searcher = FileManager(script_dir)

# Event storage
events_vector = []
events_timestamp_vector = []
end_task = Event()
end_task.set()
experimental_condition = 1 # 0 = I-, 1 = I+. I- = No interdependance, I+ = Interdependace
animals_in_box = []

# Helper functions
def detect_pattern():
    """
    Finds the right pattern of events in the event_vector for determining IN or 
    OUT of the box. Matches patterns where the first and last items are fixed 
    ("OUTER"/"INNER") and the middle is any lowercase string (name of the animal).
    """
    print(f"Events list {events_vector}")
    
    if len(events_vector) >= 3:
        last_three = events_vector[-3:]
        
        # Animal got in
        if last_three[0] == "OUTER" and last_three[2] == "INNER" and re.fullmatch(r"[a-z]+", last_three[1]):
            # animal_amount_logic(last_three[1],"in")
            file_logger.log_to_file(log_file_path,f"{events_timestamp_vector[-1]},{last_three[1]},in")
        # Animal got out
        elif last_three[0] == "INNER" and last_three[2] == "OUTER" and re.fullmatch(r"[a-z]+", last_three[1]):
            # animal_amount_logic(last_three[1],"out")
            file_logger.log_to_file(log_file_path,f"{events_timestamp_vector[-1]},{last_three[1]},out")
    
    if len(events_vector) == 6:
        del events_vector[0]
        del events_timestamp_vector[0]

# IR Detection Loop
def ir_loop():
    print("Starting IR Direction Detector. Press Ctrl+C to exit.")
    try:
        while end_task.is_set():
            beam_break = detector.log_beam_break()
            if beam_break:
                sensorID, timestampIR = beam_break
                events_vector.append(sensorID)
                events_timestamp_vector.append(timestampIR)
                # print(f"{sensorID} sensor broken at {timestampIR}")
                
                # Detect pattern
                detect_pattern()
                
            time.sleep(0.1)  # Small delay to reduce CPU usage
    except Exception as e:
        print(f"Error in IR loop: {e}")
    finally:
        print("Exiting IR Direction Detector.")

# RFID Loop
def rfid_loop():
    print("Starting RFID")
    try:
        while end_task.is_set():
            time.sleep(0.1)      
            datWaiting = RFID.ser.inWaiting()
            if datWaiting > 0:
                returnedData = RFID.processFrame()
                monkey_tag = binascii.b2a_hex(returnedData[3]).decode("utf-8")
                print(f"MonkeyTag: {monkey_tag}")
                timestampRFID = returnedData[-1].isoformat()
                animal_name = animalID_searcher.get_animal_name_from_file(animalsID_file, monkey_tag)
                if animal_name:
                    print(f'Animal {animal_name} detected')
                    if not events_vector or events_vector[-1] != animal_name:
                        events_vector.append(animal_name)
                        events_timestamp_vector.append(timestampRFID)
                        
                        # Detect pattern
                        detect_pattern()

                    # print('Message timestamp: ' + timestampRFID)
                    # print('Transponder type: ' + binascii.b2a_hex(returnedData[2]).decode("utf-8"))
                    # print('Tag: ' + monkey_tag)
                
    except Exception as e:
        print(f"Error in RFID loop: {e}")
    finally:
        print("Exiting RFID.")

# Main execution
if __name__ == "__main__":
    ir_thread = Thread(target=ir_loop)
    rfid_thread = Thread(target=rfid_loop)

    ir_thread.start()
    rfid_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program...")
        end_task.clear()

    ir_thread.join()
    rfid_thread.join()

