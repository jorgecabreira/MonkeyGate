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

"""
Crossing Frequency
Count how many times each animal passes through the gate per unit time 
(hourly, daily, etc.). This gives an insight into overall activity levels 
and peak usage periods.

For instance,it might be observed increased activity during certain hours of 
the day or specific days of the week.
"""


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

