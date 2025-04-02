#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 22:07:44 2025

@author: J. Cabrera-Moreno
        Postdoctoral Fellow
        Evolutionary Cognition Group
        Institute of Evolutionary Anthropology
        University of Zurich
        
        Description: Data files meta hanlding
"""

import glob
import pandas as pd


class FilesToDataframe: 
    
    def __init__(self, mainPath):    
        self.mainPathFolder = mainPath
    
    def createSingleDf(self):
        # List of all file's path
        pathFiles = glob.glob(f"{self.mainPathFolder}/*")
        
        # Build a single df
        dfs = []
        for idx, file in enumerate(pathFiles):
            # find if the file has header or footer
            with open (file) as doc:
                firstLine = doc.readline().strip()
                if ':' in firstLine:
                    # has a header
                    df = pd.read_csv(file,skiprows=1, engine='c', on_bad_lines='skip')

            dfs.append(df)
        
        allDataframes = pd.concat(dfs, ignore_index=False).reset_index()
        
        return allDataframes


if __name__ == '__main__':
    FTDF = FilesToDataframe('/Volumes/G_IEA_PRS$/PS/2_ERC/AutomatedChallenges/eSeesaw/piz-ecg2')
    df = FTDF.createSingleDf()