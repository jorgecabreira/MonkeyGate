#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 10:35:08 2025

@author: Jorge Cabrera-Moreno
    Postdoctoral Fellow
    Evolutionary Cogntiion Group
    Institute of Evolutionary Anthropology
    University of Zurich
    
    Description: MONKEY GATE DATA
                Analyize date coming from the mokey gate setup in which a tunel
                equipped with an RFID antenna and two IR beams log timestamp
                and direction of movement across two home enclosures.
"""
import os
import pandas as pd
from datetime import timedelta

from FileManipulation import FilesToDataframe


def formatDate(df):
    # Convert the int64 datetime to string, then to datetime
    df['datetime'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    # Extract the date part
    df['date'] = df['datetime'].dt.date

    # Sort by date (important for accurate session assignment)
    df = df.sort_values(by='date')
    
    return df

def createSession(df):
    df = df.sort_values('date').copy()
    df['session'] = (df['date'].diff().dt.days.fillna(0) > 0).cumsum() + 1
    return df

if __name__ == '__main__':
    
    # Main folder that contains all data regarding the eSeesaw task
    mainPath = '/Volumes/G_IEA_PRS$/PS/2_ERC/AutomatedChallenges/MonkeyGate/pilotSessions'
    
    # Folder per machine of interest that contained data
    machinesOfInterest = ['Nikita']

    # List dataframes that incluse all sessions from all machines of interest
    machineDataframes = []
    
    for machine in machinesOfInterest:
        # Create full path
        curPath = os.path.join(mainPath, machine)
        # Start helper libraries
        FTDF = FilesToDataframe(curPath)
        # Merge files to a single dataframe
        machineDF = FTDF.createSingleDf()
        # Add Machine name
        machineDF['machineID'] = machine
        # Format Date column to datetime object
        machineDF = formatDate(machineDF)
        # Count the number of sessions per machine and append it to a new column
        machineDF = createSession(machineDF)
        
        machineDataframes.append(machineDF)
    
    # Merges all dataframes from all machines in a single dataframe
    curDF = pd.concat(machineDataframes, ignore_index=True)
    curDF = curDF.sort_values('datetime').reset_index(drop=True)
    
    # Adds sessions across all machines based in days
    curDF['global_session'] = (curDF['date'].diff().dt.days.fillna(0) > 0).cumsum() + 1
    
    
    
    """
    Crossing Frequency
    Count how many times each animal passes through the gate per unit time 
    (hourly, daily, etc.). This gives an insight into overall activity levels 
    and peak usage periods.
    
    For instance,it might be observed increased activity during certain hours of 
    the day or specific days of the week.
    """
    
    # # # Assuming df is your DataFrame
    # # # Columns: datetime, object, state, monkey
    # # df = df.sort_values('datetime').reset_index(drop=True)
    
    # Group events that happen within a 2-second window
    grouped_events = []
    window_size = timedelta(seconds=2)
    buffer = []
    
    for idx, row in curDF.iterrows():
        if not buffer:
            buffer.append(row)
        else:
            if row['datetime'] - buffer[-1]['datetime'] <= window_size:
                buffer.append(row)
            else:
                grouped_events.append(pd.DataFrame(buffer))
                buffer = [row]
    # Append last buffer
    if buffer:
        grouped_events.append(pd.DataFrame(buffer))
    
    # Process grouped events to infer movement
    movement_records = []
    last_movement = {}
    
    for group in grouped_events:
        sensors = group[group['object'].isin(['innerIR', 'outerIR'])]
        rfid_tags = group[group['object'] == 'rfid'][['state', 'monkey']].drop_duplicates()
        sensor_count = len(sensors)
        group_time = group['datetime'].min()
        session = group['session'].unique()[0]
        
    
        inferred_flag = 0
        ir_order = []
        confidence = 0.0
        direction = "unknown"
    
        if sensor_count >= 2:
            sensors_sorted = sensors.sort_values('datetime')
            ir_order = sensors_sorted['object'].tolist()
     
                
            if ir_order[0] == 'outerIR' and ir_order[1] == 'innerIR':
                direction = 'entered'
                confidence = 1.0 if len(rfid_tags) == 1 else 0.8
            elif ir_order[0] == 'innerIR' and ir_order[1] == 'outerIR':
                # print('direction exited')
                # break
                direction = 'exited'
                confidence = 1.0 if len(rfid_tags) == 1 else 0.8
            else:
                direction = 'unknown'
                confidence = 0.5
        elif sensor_count == 1:
            direction = 'unknown'
            confidence = 0.3
    
        for _, (tag, monkey) in rfid_tags.iterrows():
            # Fix here: Check if same IR order has occurred before
            if monkey in last_movement:
                last_dir, last_ir_order = last_movement[monkey]
    
                if direction == last_dir and ir_order == last_ir_order:
                    # Flip direction to avoid repeating same pattern twice
                    direction = 'exited' if last_dir == 'entered' else 'entered'
                    inferred_flag = 1
                    confidence = 0.7  # set medium-high confidence for inferred flip
    
            if direction in ['entered', 'exited']:
                last_movement[monkey] = (direction, ir_order)
    
            movement_records.append({
                'time': group_time,
                'monkey': monkey,
                'rfid': tag,
                'event': direction,
                'confidence': confidence,
                'inferred_from_previous': inferred_flag,
                'session': session
            })
    

    # Create result DataFrame
    result_df = pd.DataFrame(movement_records)

"""
Temporal Trends by Direction
Break down counts over time (hourly, daily, etc.) for each direction. This can 
help to understand if the directionality shifts at certain times—perhaps 
reflecting behavioral patterns or environmental influences.
"""

"""
Net Movement
Compute the difference between the two directions over time. A positive or negative 
net movement might indicate trends in territorial behavior or preferential access.
"""

"""
Co-occurrence Analysis
Pairwise Co-occurrence Counts: Iterate over your data and for every event, 
check if another animal’s event falls within the defined time window.

Co-occurrence Matrix: Build a matrix where each cell (i, j) represents the 
frequency with which animal i and animal j have passed through together.
"""

