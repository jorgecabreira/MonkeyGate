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
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns

from FileManipulation import FilesToDataframe


def formatDate(df):
    # Convert the int64 datetime to string, then to datetime
    df['datetime'] = pd.to_datetime(df['date'].astype(str).str[:17], format='%Y%m%d%H%M%S%f')

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
    machinesOfInterest = ['Lima']

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
    # Remove non-sensor events (e.g., rows where object equals 'session')
    criDF = curDF[curDF['object'] != 'session'].reset_index(drop=True)
    
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
    # chatGTP and Jorge 
    # movement_records = []
    # timestamps = curDF['datetime']
    # window = timedelta(seconds=2)
    
    # curDF['event_id'] = np.nan   # New column: rows not grouped will remain NaN
    # event_counter = 1            # Initialize a cumulative event Counter
    
    # i = 0
    # while i < len(curDF):
    #     row = curDF.iloc[i]
    
    #     if row['object'] in ['innerIR', 'outerIR']:
    #         ir1_time = row['datetime']
    #         ir1_type = row['object']
    #         machine = row['machineID']
    
    #         # Limit search window using index
    #         window_end_time = ir1_time + window
    #         start_idx = i + 1
    #         end_idx = timestamps.searchsorted(window_end_time, side='right')
    
    #         lookahead_df = curDF.iloc[start_idx:end_idx]
    #         lookahead_df = lookahead_df[lookahead_df['machineID'] == machine]
    
    #         # Get other IR and RFID
    #         ir2_df = lookahead_df[(lookahead_df['object'].isin(['innerIR', 'outerIR'])) & (lookahead_df['object'] != ir1_type)]
    #         rfid_df = lookahead_df[lookahead_df['object'] == 'rfid']
    
    #         # --- If we have enough data, build an event ---
    #         if not ir2_df.empty and not rfid_df.empty:
    #             ir2_row = ir2_df.iloc[0]
    #             ir2_type = ir2_row['object']
    #             ir_order = [ir1_type, ir2_type]
    
    #             # Determine direction
    #             if ir_order == ['outerIR', 'innerIR']:
    #                 direction = 'entered'
    #                 confidence = 1.0 if len(rfid_df) == 1 else 0.8
    #             elif ir_order == ['innerIR', 'outerIR']:
    #                 direction = 'exited'
    #                 confidence = 1.0 if len(rfid_df) == 1 else 0.8
    #             else:
    #                 direction = 'unknown'
    #                 confidence = 0.5
    
    #             # --- Grouping rows into a single event ---
    #             # Get original indices for current IR row, complementary IR row, and RFID events.
    #             current_index = curDF.index[i]
    #             ir2_index = ir2_df.index[0]
    #             rfid_indices = rfid_df.index.tolist()
    
    #            # Combine these indices and mark them with the current event details.
    #             event_indices = {current_index, ir2_index}.union(rfid_indices)
    #             curDF.loc[list(event_indices), 'event_id'] = event_counter
    #             curDF.loc[list(event_indices), 'event'] = direction
    #             curDF.loc[list(event_indices), 'confidence'] = confidence
            
    #             # Record each RFID tag involved
    #             for _, r in rfid_df.drop_duplicates('monkey').iterrows():
    #                 movement_records.append({
    #                     'time': ir1_time,
    #                     'monkey': r['monkey'],
    #                     'rfid': r['state'],
    #                     'event': direction,
    #                     'confidence': confidence,
    #                 })
                    
    #             event_counter += 1
    
    #             # Skip to next unread event after the last row we just used
    #             last_used_time = max(ir2_row['datetime'], rfid_df['datetime'].max())
    #             i = timestamps.searchsorted(last_used_time, side='right')
    #             continue  # go to next event
    
    #     # If not a matched event, just advance normally
    #     i += 1
    
    # # Create result DataFrame
    # result_df = pd.DataFrame(movement_records)
    

    # chatGPT-------
    # # -------------------------
    # # Define the event classification function.
    # # This function inspects a block of sensor events (grouped by a dynamic window)
    # # and determines whether the block represents a fast/slow entry, exit, or dwell event.
    # # -------------------------
    # def classify_event(event_df):
    #     """
    #     Classify a block of sensor events into a movement event.
    
    #     Parameters:
    #       event_df (pd.DataFrame): A block of sensor events with columns:
    #                                'object', 'animal', and 'datetime'.
    
    #     Returns:
    #       dict: A dictionary with keys:
    #          - start_time: Timestamp of the first event.
    #          - end_time: Timestamp of the last event.
    #          - duration: Block duration in seconds.
    #          - animal: Animal identifier (from RFID row if available).
    #          - event: 'entered', 'exited', or 'dwell' (None if not classifiable).
    #          - confidence: Score from 0.0 to 1.0 reflecting reliability.
    #          - inferred_from_previous: 0 (can be updated later if needed).
    #     """
    #     # Get the list of sensor types in this block
    #     sensors = event_df['object'].tolist()
        
    #     # Check for presence of specific sensor types
    #     has_inner = 'innerIR' in sensors
    #     has_outer = 'outerIR' in sensors
    #     has_rfid  = 'rfid' in sensors
    
    #     times = event_df['datetime']
    #     duration = (times.max() - times.min()).total_seconds()
        
    #     # Initialize default values
    #     direction = None
    #     confidence = 0.0
    
    #     # Determine the order of IR sensor triggers (if any)
    #     ir_events = event_df[event_df['object'].isin(['innerIR', 'outerIR'])].sort_values('datetime')
    #     ir_order = ir_events['object'].tolist()
    
    #     # Event classification based on sensor presence and duration:
    #     if has_inner and has_outer and has_rfid:
    #         if ir_order == ['outerIR', 'innerIR']:
    #             direction = 'entered'
    #         elif ir_order == ['innerIR', 'outerIR']:
    #             direction = 'exited'
    #         else:
    #             direction = 'dwell'
            
    #         # Use duration to distinguish fast from slow passage.
    #         if duration < 3:
    #             confidence = 1.0  # fast, clear event
    #         elif duration <= 8:
    #             confidence = 0.8  # slower passage
    #         else:
    #             # Very long duration likely indicates a dwell.
    #             direction = 'dwell'
    #             confidence = 0.5
    
    #     elif (has_inner or has_outer) and has_rfid:
    #         # One IR sensor with RFID suggests the animal just looked in (dwell)
    #         direction = 'dwell'
    #         confidence = 0.5
    
    #     elif has_inner or has_outer:
    #         # Only IR sensor(s) without RFID; treat as noise/incomplete.
    #         direction = None
    #         confidence = 0.0
    
    #     # Determine the animal identifier: use RFID rows if available.
    #     rfid_rows = event_df[event_df['object'] == 'rfid']
    #     animals = rfid_rows['monkey'].unique()
    #     animal = animals[0] if len(animals) == 1 else None
    
    #     return {
    #         'start_time': times.min(),
    #         'end_time': times.max(),
    #         'duration': duration,
    #         'monkey': animal,
    #         'event': direction,
    #         'confidence': confidence,
    #         'inferred_from_previous': 0
    #     }
    
    # # -------------------------
    # # Extract movement events from the DataFrame.
    # # The extraction uses a dynamic window (up to max_event_duration seconds) to group events.
    # # For each event, the indices of the rows used in that event are stored.
    # # -------------------------
    # def extract_movement_events(df, max_event_duration=8):
    #     """
    #     Extracts movement events from sensor data and attaches the indices of the rows
    #     that contributed to each event.
    
    #     Parameters:
    #       df (pd.DataFrame): Sensor events DataFrame with 'object', 'animal', 'datetime'.
    #       max_event_duration (int): Maximum allowed duration (in seconds) for a single event.
    
    #     Returns:
    #       pd.DataFrame: A DataFrame with one row per movement event, including a field
    #                     'indices' (list of row indices in df that are part of this event).
    #     """
    #     movement_records = []
    #     i = 0
    #     n = len(df)
        
    #     while i < n:
    #         row = df.iloc[i]
    #         current_time = row['datetime']
    #         window_end = current_time + timedelta(seconds=max_event_duration)
            
    #         # Identify rows within the current event block.
    #         block = df[(df['datetime'] >= current_time) & (df['datetime'] <= window_end)].copy()
    #         block_indices = block.index.tolist()
            
    #         # Classify the block.
    #         result = classify_event(block)
    #         if result['event'] is not None:
    #             result['indices'] = block_indices  # Store indices of rows in this event.
    #             movement_records.append(result)
    #             # Skip ahead: find the next row after the current event block.
    #             next_index = df[df['datetime'] > result['end_time']].index
    #             i = next_index.min() if not next_index.empty else n
    #         else:
    #             i += 1
                
    #     # Create a DataFrame from the list of events and add an events counter.
    #     events_df = pd.DataFrame(movement_records)
    #     events_df = events_df.sort_values('start_time').reset_index(drop=True)
    #     events_df['events_counter'] = events_df.index + 1  # Sequential event numbering.
    #     return events_df
    
    # # -------------------------
    # # Merge event details back into the original DataFrame.
    # # For rows that were used in an event, new columns are added with event details.
    # # Rows not used in any event get NaN in these new columns.
    # # -------------------------
    # def merge_events_with_data(df, events_df):
    #     """
    #     Merges the movement event details with the original DataFrame.
        
    #     Parameters:
    #       df (pd.DataFrame): Original sensor events DataFrame.
    #       events_df (pd.DataFrame): DataFrame with extracted events, including 'indices'
    #                                 (list of row indices from df), event metadata, and
    #                                 'events_counter'.
        
    #     Returns:
    #       pd.DataFrame: A new DataFrame with additional columns:
    #                     - event_start_time
    #                     - event_end_time
    #                     - event_duration
    #                     - movement_event
    #                     - event_confidence
    #                     - event_inferred
    #                     - events_counter
    #                     These columns are filled for rows that are part of an event,
    #                     and NaN for rows that are not.
    #     """
    #     # Create a copy of df and initialize new columns.
    #     merged_df = df.copy()
    #     merged_df['event_start_time'] = pd.NaT
    #     merged_df['event_end_time'] = pd.NaT
    #     merged_df['event_duration'] = pd.NA
    #     merged_df['movement_event'] = pd.NA
    #     merged_df['event_confidence'] = pd.NA
    #     merged_df['event_inferred'] = pd.NA
    #     merged_df['events_counter'] = pd.NA
    
    #     # Iterate over each extracted event and assign its details to corresponding rows.
    #     for _, event in events_df.iterrows():
    #         idxs = event['indices']
    #         merged_df.loc[idxs, 'event_start_time'] = event['start_time']
    #         merged_df.loc[idxs, 'event_end_time'] = event['end_time']
    #         merged_df.loc[idxs, 'event_duration'] = event['duration']
    #         merged_df.loc[idxs, 'movement_event'] = event['event']
    #         merged_df.loc[idxs, 'event_confidence'] = event['confidence']
    #         merged_df.loc[idxs, 'event_inferred'] = event['inferred_from_previous']
    #         merged_df.loc[idxs, 'events_counter'] = event['events_counter']
            
    #     return merged_df
    
    # # -------------------------
    # # Main script:
    # # 1. Extract movement events.
    # # 2. Merge the event details back into the original DataFrame.
    # # 3. Display the merged DataFrame using your display tool.
    # # -------------------------
    # events_df = extract_movement_events(curDF, max_event_duration=8)
    # merged_df = merge_events_with_data(curDF, events_df)
    
   
    # Jorge
    df = curDF.copy()
    # Create a boolean column identifying 'rfid' rows
    df['is_rfid'] = df['object'] == 'rfid'
    # Identify the start of a new 'rfid' event: a row is True and the previous row was not 'rfid'
    df['event_id'] = (df['is_rfid'] & ~df['is_rfid'].shift(fill_value=False)).cumsum()
    # Set event_id to NaN for rows that are not 'rfid'
    df.loc[~df['is_rfid'], 'event_id'] = pd.NA
    
    # Remove the temporary boolean column if desired
    df.drop(columns=['is_rfid'], inplace=True)
    
    # Take the easliest and latest rfid log per event and save the time difference in 
    # a column called 'idling_time'
    # Additionally, use the earliest and latest timestamp for each rfid event to look for 
    # the next IR event happening before and after ecery rfid event. Store the time difference
    # of the before and after IR event in two new columns: 'beforeIR' and 'afterIR'. Then
    # plot the distribution of IR events happening before and after each rfid event.  
    
    # Group RFID rows by event_id to get the earliest (start) and latest (end) timestamp per event
    rfid_events = df[df['object'] == 'rfid'].groupby('event_id').agg(start=('datetime', 'min'), end=('datetime', 'max')).reset_index()
    # Calculate idling_time (in seconds) for each RFID event
    rfid_events['idling_time'] = (rfid_events['end'] - rfid_events['start']).dt.total_seconds()
    # Merge the idling_time back into the main dataframe based on event_id
    df = df.merge(rfid_events[['event_id', 'idling_time']], on='event_id', how='left')
    
    # ----
    # To know the distribution of IR events before and after of each RFID event
    # ----
    # # Create a DataFrame with IR events
    # ir_events = df[df['object'].isin(['innerIR', 'outerIR'])].copy().sort_values('datetime')
    
    # # Find the IR event immediately BEFORE the start of each RFID event using merge_asof
    # rfid_before = pd.merge_asof(
    #     rfid_events.sort_values('start'),
    #     ir_events[['datetime']].rename(columns={'datetime': 'ir_before'}),
    #     left_on='start', right_on='ir_before',
    #     direction='backward')
    # rfid_events['beforeIR'] = (rfid_events['start'] - rfid_before['ir_before']).dt.total_seconds()
    
    # # Find the IR event immediately AFTER the end of each RFID event using merge_asof
    # rfid_after = pd.merge_asof(
    #     rfid_events.sort_values('end'),
    #     ir_events[['datetime']].rename(columns={'datetime': 'ir_after'}),
    #     left_on='end', right_on='ir_after',
    #     direction='forward')
    # rfid_events['afterIR'] = (rfid_after['ir_after'] - rfid_events['end']).dt.total_seconds()

    # # Plot the distribution of the IR events before and after each RFID event
    # plt.figure(figsize=(12, 5))
    
    # plt.subplot(1, 2, 1)
    # plt.hist(rfid_events['beforeIR'].dropna(), bins=30, edgecolor='black')
    # plt.xlabel('Time Difference (seconds)')
    # plt.ylabel('Frequency')
    # plt.title('Distribution of IR Events Before RFID Event')
    
    # plt.subplot(1, 2, 2)
    # plt.hist(rfid_events['afterIR'].dropna(), bins=30000, edgecolor='black')
    # plt.xlim(-1, 100)  # Limit the x-axis to the first 30 minutes (1800 seconds)
    # plt.xlabel('Time Difference (seconds)')
    # plt.ylabel('Frequency')
    # plt.title('Distribution of IR Events After RFID Event')
    # plt.tight_layout()
    # plt.show()    
    

    # ----- 
    # Parse RFID and IR events 
    # ----- 
    # Sort the events by start time to ensure earlier events get precedence when assigning IR logs.
    rfid_events.sort_values('start', inplace=True)
    # Keep track of IR rows that have already been assigned
    assigned_ir_indices = set()
    
   # Iterate over each RFID event to extend it with nearby IR logs.
    for _, event in rfid_events.iterrows():
        current_event = event['event_id']
        t_first = event['start']
        t_last = event['end']
        
        # Define the 2-second windows for before and after.
        before_start = t_first - pd.Timedelta(seconds=2)
        before_end = t_first
        after_start = t_last
        after_end = t_last + pd.Timedelta(seconds=2)
        
        # --- BEFORE window ---
        candidates_before = df[(df['datetime'] >= before_start) & (df['datetime'] < before_end)]
        candidates_before = candidates_before[~candidates_before.index.isin(assigned_ir_indices)]
        
        if 'rfid' in candidates_before['object'].values:
            matches = candidates_before[candidates_before['object'] == 'rfid']
            last_idx = matches.index[-1]
            rfid_pos = candidates_before.index.get_loc(last_idx)
            # Exclude the RFID row and everything before it
            candidates_before = candidates_before.iloc[rfid_pos + 1:]
        
        df.loc[candidates_before.index, 'event_id'] = current_event
        assigned_ir_indices.update(candidates_before.index)
        
        # --- AFTER window ---
        candidates_after = df[(df['datetime'] > after_start) & (df['datetime'] <= after_end)]
        candidates_after = candidates_after[~candidates_after.index.isin(assigned_ir_indices)]
        
        if 'rfid' in candidates_after['object'].values:
            idx = (candidates_after['object'] == 'rfid').idxmax()
            # Get the positional index of that label
            rfid_pos = candidates_after.index.get_loc(idx)
            # Exclude the RFID row and everything after it
            candidates_after = candidates_after.iloc[:rfid_pos]
        
        df.loc[candidates_after.index, 'event_id'] = current_event
        assigned_ir_indices.update(candidates_after.index)
        
    # -----
    # Asign movement behavior
    # ----
    # If single innerIR and outerIR confidence = 1.0 ENTER | EXIT
    # If just innerIR or outerIR confidence = 1.0 SNIFF
    # Temporary storage
    movement_map = {}
    confidence_map = {}
    # Iterate over each RFID reading event to asign movement behavior
    for event_id, event_df in df.groupby('event_id'):
        
        # Determine the order of IR sensor triggers (if any)
        ir_events = event_df[event_df['object'].isin(['innerIR', 'outerIR'])].sort_values('datetime')
        ir_order = ir_events['object'].tolist()
        
        # If all IR events are either only innerIR or outerIR. confidence = 1.0, movement = SNIFF
        animal_movement = None
        confidence      = None
        if len(ir_events['object'].unique()) == 1:
            if ir_order[0] == 'innerIR':
                animal_movement = 'inSniff' 
            else: 'outSniff'
            confidence = 1.0
        
        # Count inner and outer
        elif len(ir_events['object'].unique()) == 2 and len(ir_events) == 2:
            # Determine direction
            if ir_order == ['outerIR', 'innerIR']:
                animal_movement = 'entered'
            else: animal_movement = 'exited'
            confidence = 1.0 
            
        # For those events that hold multiple innerIR and outerIR intertwined over time
        # Based on the fact the most of the correct IR detected logs happen before
        # the RFID logs. Priority will be given to IR logs happening before the RFID log
        
        # Which behaviors can be found?
        # in -> out -> rfid -> in = animal exited and tail might have trigger the innerIR
        
        
        # Given the problem that the combination of IR events can be big it is safer
        # to plot the most common patterns across the data frame and based on that decide
        # what to do with the movement asignation
        
        elif len(ir_events) > 2:
            # First work on IR that happen before the RFID logs
            matches = event_df[event_df['object'] == 'rfid']
            first_idx = matches.index[0]
            rfid_pos = event_df.index.get_loc(first_idx)
            # Exclude the RFID row and everything after it
            multiEvent_df = event_df.iloc[:rfid_pos]

            # Now work with the upper part of the IR logs
            if len(multiEvent_df['object'].unique()) == 2 and len(ir_events) == 2:
                # Determine direction
                if ir_order == ['outerIR', 'innerIR']:
                    animal_movement = 'entered'
                else: animal_movement = 'exited'
                confidence = 1.0 
                
        
        # # Store the results for this event
        # movement_map[event_id] = animal_movement
        # confidence_map[event_id] = confidence
        
        # Manual inspection: show candidates and pause before continuing.
        input(
            f"Processed event {event_id}.\n\n"
            f"Processed group {event_df}.\n\n"
            f"Processed ir events {ir_events}.\n\n"
            f"Processed ir order {ir_order}.\n\n"
            f"Animal movement: {animal_movement}.\n\n"
            f"Confidence: {confidence}.\n\n"
            "=============================="
            "Press Enter to continue to the next event..."
            )
    # # Assign back to df using map
    # df['movement'] = df['event_id'].map(movement_map)
    # df['confidence'] = df['event_id'].map(confidence_map)
    
        # # # --- BEFORE window ---
        # # # Check for conflicting RFID logs (from a different event) in the before window.
        # # conflict_before = df[
        # #     (df['datetime'] >= before_start) &
        # #     (df['datetime'] < before_end) &
        # #     (df['object'] == 'rfid') &
        # #     (df['event_id'] != current_event)
        # # ]
        
        # # if not conflict_before.empty:
        # #     # If a conflicting RFID log is found in the before window,
        # #     # drop (unset) any RFID logs from the current event in that window.
        # #     df.loc[
        # #         (df['datetime'] >= before_start) &
        # #         (df['datetime'] < before_end) &
        # #         (df['object'] == 'rfid') &
        # #         (df['event_id'] == current_event),
        # #         'event_id'] = pd.NA
        # candidates_before = df[(df['datetime'] >= before_start) & (df['datetime'] < before_end)]
        # if 'rfid' in candidates_before['object'].values:
        #     matches = candidates_before[candidates_before['object'] == 'rfid']
        #     last_idx = matches.index[-1]
        #     rfid_pos = candidates_before.index.get_loc(last_idx)
        #     # Exclude the RFID row and everything before it
        #     candidates_before = candidates_before.iloc[rfid_pos + 1:]
                
        # # # In any case, assign IR logs in the before window to the current event.
        # # candidate_before = df[
        # #     (df['datetime'] >= before_start) &
        # #     (df['datetime'] < before_end) &
        # #     (df['object'].isin(['inerIR', 'outerIR']))
        # # ]
        # df.loc[candidates_before.index, 'event_id'] = current_event
    
        # # # --- AFTER window ---
        # # # Check for conflicting RFID logs (from a different event) in the after window.
        # # conflict_after = df[
        # #     (df['datetime'] > after_start) &
        # #     (df['datetime'] <= after_end) &
        # #     (df['object'] == 'rfid') &
        # #     (df['event_id'] != current_event)
        # # ]
        # # if not conflict_after.empty:
        # #     # If a conflicting RFID log is found in the after window,
        # #     # drop (unset) any RFID logs from the current event in that window.
        # #     df.loc[
        # #         (df['datetime'] > after_start) &
        # #         (df['datetime'] <= after_end) &
        # #         (df['object'] == 'rfid') &
        # #         (df['event_id'] == current_event),
        # #         'event_id'] = pd.NA
        # candidates_after = df[(df['datetime'] > after_start) & (df['datetime'] <= after_end)]
        # if 'rfid' in candidates_after['object'].values:
        #     idx = (candidates_after['object'] == 'rfid').idxmax()
        #     # Get the positional index of that label
        #     rfid_pos = candidates_after.index.get_loc(idx)
        #     # Exclude the RFID row and everything after it
        #     candidates_after = candidates_after.iloc[:rfid_pos]
            
        # # # In any case, assign IR logs in the after window to the current event.
        # # candidate_after = df[
        # #     (df['datetime'] > after_start) &
        # #     (df['datetime'] <= after_end) &
        # #     (df['object'].isin(['inerIR', 'outerIR']))
        # # ]
        # df.loc[candidates_after.index, 'event_id'] = current_event
        
        
        # # Manual inspection: show candidates and pause before continuing.
        # input(
        #     f"Processed event_id {current_event}.\n\n"
        #     f"BEFORE window candidates (from {before_start} to {before_end}):\n{candidates_before}\n\n"
        #     f"AFTER window candidates (from {after_start} to {after_end}):\n{candidates_after}\n\n"
        #     "Press Enter to continue to the next event..."
        # )
           



    """
    Temporal Trends by Direction
    Break down counts over time (hourly, daily, etc.) for each direction. This can 
    help to understand if the directionality shifts at certain times—perhaps 
    reflecting behavioral patterns or environmental influences.
    """
    # # Convert "entered" to 1, "exited" to -1
    # result_df['movement_code'] = result_df['event'].map({'entered': 1, 'exited': -1})
    
    # # Plot timeline
    # plt.figure(figsize=(12, 6))
    # for monkey, subdf in result_df.groupby('monkey'):
    #     plt.step(subdf['time'], subdf['movement_code'].cumsum(), where='post', label=monkey)
    
    # plt.xlabel('Time')
    # plt.ylabel('Net Entries (cumulative)')
    # plt.title('Cumulative Movements per Monkey Over Time')
    # plt.legend()
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()
    
    # result_df['hour'] = result_df['time'].dt.hour
    # sns.countplot(data=result_df, x='hour', hue='event')
    # plt.title("Entries and Exits by Hour")
    # plt.xlabel("Hour of Day")
    # plt.ylabel("Count")
    # plt.show()
    
    # activity_summary = result_df.groupby(['monkey', 'event']).size().unstack(fill_value=0)
    # activity_summary.plot(kind='bar', stacked=True, figsize=(10, 5))
    # plt.title("Total Entries and Exits per Monkey")
    # plt.xlabel("Monkey")
    # plt.ylabel("Number of Movements")
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.show()
    
    # sns.scatterplot(data=result_df, x='time', y='monkey', hue='confidence', style='inferred_from_previous', palette='coolwarm')
    # plt.title("Movement Confidence Over Time")
    # plt.show()
    
    # # Sample logic:
    # result_df['chamber'] = result_df['event'].map({'entered': 1, 'exited': 2})
    
    # # Heatmap of monkey presence in chambers over time
    # # Pivot table: rows = monkeys, columns = timestamps, values = chamber
    # location_timeline = result_df.pivot(index='monkey', columns='time', values='chamber')
    
    # # Plot heatmap of chamber presence
    # plt.figure(figsize=(12, 4))
    # sns.heatmap(location_timeline.fillna(0), cmap='coolwarm', cbar_kws={'label': 'Chamber'})
    # plt.title('Monkey Chamber Timeline')
    # plt.xlabel('Time')
    # plt.ylabel('Monkey')
    # plt.tight_layout()
    
    
    # # Create a transition matrix: from-chamber to to-chamber
    # result_df['prev_chamber'] = result_df.groupby('monkey')['chamber'].shift(1)
    # transitions = result_df.dropna(subset=['prev_chamber'])
    # transition_matrix = pd.crosstab(transitions['prev_chamber'], transitions['chamber'])
    
    # # Plot heatmap
    # plt.figure(figsize=(5, 4))
    # sns.heatmap(transition_matrix, annot=True, fmt='d', cmap='Blues')
    # plt.title('Chamber Transition Matrix')
    # plt.xlabel('To Chamber')
    # plt.ylabel('From Chamber')
    # plt.tight_layout()
    
    
    # # Calculate time spent in each chamber before switching
    # residence_times = []
    
    # for monkey, group in result_df.groupby('monkey'):
    #     group = group.sort_values('time')
    #     for i in range(1, len(group)):
    #         prev = group.iloc[i - 1]
    #         curr = group.iloc[i]
    #         if prev['chamber'] != curr['chamber']:
    #             duration = (curr['time'] - prev['time']).total_seconds()
    #             residence_times.append({
    #                 'monkey': monkey,
    #                 'chamber': prev['chamber'],
    #                 'duration_seconds': duration
    #             })
    
    # residence_df = pd.DataFrame(residence_times)
    
    # # Plot boxplot of residence time
    # plt.figure(figsize=(8, 5))
    # sns.boxplot(data=residence_df, x='chamber', y='duration_seconds', hue='monkey')
    # plt.title('Residence Time per Chamber')
    # plt.ylabel('Time (seconds)')
    # plt.xlabel('Chamber')
    # plt.grid(True)
    # plt.tight_layout()
    
    
    # from collections import defaultdict

    # # Detect monkey pairs that move together into the same chamber within a time window
    # time_threshold = pd.Timedelta(seconds=10)
    # group_movements = []
    
    # for i in range(len(result_df)):
    #     curr = result_df.iloc[i]
    #     monkey = curr['monkey']
    #     chamber = curr['chamber']
    #     event = curr['event']
    #     t_start = curr['time']
    
    #     # Find others who made same move to same chamber within threshold
    #     window = result_df[(result_df['time'] > t_start) &
    #                        (result_df['time'] <= t_start + time_threshold) &
    #                        (result_df['event'] == event) &
    #                        (result_df['chamber'] == chamber)]
    
    #     for _, other in window.iterrows():
    #         if other['monkey'] != monkey:
    #             pair = tuple(sorted([monkey, other['monkey']]))
    #             group_movements.append(pair)
    
    # # Count how many times each pair moved together
    # from collections import Counter
    # pair_counts = Counter(group_movements)
    
    # pair_df = pd.DataFrame([{'monkey1': k[0], 'monkey2': k[1], 'count': v} for k, v in pair_counts.items()])
    
    # # Plot pairwise co-movements
    # plt.figure(figsize=(8, 5))
    # sns.barplot(data=pair_df, x='monkey1', y='count', hue='monkey2')
    # plt.title('Co-movement Frequencies')
    # plt.ylabel('Times Moved Together')
    # plt.xlabel('Monkey')
    # plt.grid(True)
    # plt.tight_layout()

    # # Count how often each monkey initiated a group movement
    # leader_counts = defaultdict(int)
    
    # for i in range(len(result_df)):
    #     curr = result_df.iloc[i]
    #     monkey = curr['monkey']
    #     chamber = curr['chamber']
    #     event = curr['event']
    #     time = curr['time']
    
    #     # Who follows this monkey within 10s doing same thing
    #     group_window = result_df[(result_df['time'] > time) &
    #                              (result_df['time'] <= time + time_threshold) &
    #                              (result_df['event'] == event) &
    #                              (result_df['chamber'] == chamber)]
    
    #     if not group_window.empty:
    #         leader_counts[monkey] += 1
    
    # leader_df = pd.DataFrame(list(leader_counts.items()), columns=['monkey', 'lead_count'])
    
    # # Plot leaders
    # plt.figure(figsize=(8, 5))
    # sns.barplot(data=leader_df.sort_values('lead_count', ascending=False), x='monkey', y='lead_count')
    # plt.title('Movement Leader Counts')
    # plt.ylabel('Times Moved First in Group')
    # plt.xlabel('Monkey')
    # plt.grid(True)
    # plt.tight_layout()

    
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

