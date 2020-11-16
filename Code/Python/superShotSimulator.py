# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 21:13:39 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This code runs a series of different simulations based on shooting statistics 
from the Super Shot period of the Super Netball 2020 season. The main aim of this
analysis is to understand where optimality may lie for the proportion of a teams
total shots should be Super Shots.

TODO:
    
    > Add some summary statistics (mean, range, IQR's etc.) printed out to table
      Essentially the box plot data in tabular form
    
"""

# %% Import packages

#Python packages
import pandas as pd
pd.options.mode.chained_assignment = None #turn off pandas chained warnings
import numpy as np
import scipy.stats as stats
import random
# import seaborn as sns
import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle 
import os
import math
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

#Custom packages
import ssn2020DataHelper as dataHelper
import ssn2020FigHelper as figHelper

# %% Settings

#Set matplotlib parameters
from matplotlib import rcParams
# rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.weight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 16
rcParams['axes.linewidth'] = 1.5
rcParams['axes.labelweight'] = 'bold'
rcParams['legend.fontsize'] = 10
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.width'] = 1.5
rcParams['legend.framealpha'] = 0.0
rcParams['savefig.dpi'] = 300
rcParams['savefig.format'] = 'pdf'

#Colour settings for teams
colourDict = {'Fever': '#00953b',
              'Firebirds': '#4b2c69',
              'GIANTS': '#f57921',
              'Lightning': '#fdb61c',
              'Magpies': '#494b4a',
              'Swifts': '#0082cd',
              'Thunderbirds': '#e54078',
              'Vixens': '#00a68e'}

# %% Load in match data

#Navigate to data directory
os.chdir('..\\..\\Data\\SuperNetball2020_CD')

#Identify list of .json files
jsonFileList = list()
for file in os.listdir(os.getcwd()):
    if file.endswith('.json'):
        jsonFileList.append(file)
        
#Read in total squad lists as dataframe
df_squadLists = pd.read_csv('..\\squadLists.csv')

#Create a variable for starting positions
starterPositions = ['GS','GA','WA','C','WD','GD','GK']

#Import data using helper function
dataImport = dataHelper.getMatchData(jsonFileList = jsonFileList,
                                     df_squadLists = df_squadLists,
                                     exportDict = True, exportDf = True,
                                     exportTeamData = True, exportPlayerData = True,
                                     exportMatchData = True, exportScoreData = True,
                                     exportLineUpData = True)

#Unpack the imported data
teamInfo = dataImport['teamInfo']
matchInfo = dataImport['matchInfo']
playerInfo = dataImport['playerInfo']
scoreFlowData = dataImport['scoreFlowData']
lineUpData = dataImport['lineUpData']
individualLineUpData = dataImport['individualLineUpData']
df_teamInfo = dataImport['df_teamInfo']
df_matchInfo = dataImport['df_matchInfo']
df_playerInfo = dataImport['df_playerInfo']
df_scoreFlow = dataImport['df_scoreFlow']
df_lineUp = dataImport['df_lineUp']
df_individualLineUp = dataImport['df_individualLineUp']

# %% 'Standard' super shot simulations

# This section takes the shooting statistics of each team for the season, and
# simulates 1,000 5 minute super shot periods with varying super shot proportion
# strategies (i.e., from 0-10% up to 90-100%). 

# %% Run 'standard' sims

#Set a list of proportions to examine across simulations
superShotProps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5,
                  0.6, 0.7, 0.8, 0.9, 1.0]
    
#Set number of simulations
nSims = 1000

#Set numpy seed for consistency
np.random.seed(123)

#Set random seed for consistency
random.seed(123)

#Create dictionary to store data in
superSimResults = {'squadId': [], 'squadNickname': [],
                   'nShots': [], 'nStandard': [], 'nSuper': [],
                   'superProp': [], 'superPropCat': [], 'totalPts': []}

#Set list to store actual team super shot proportions in
teamSuperProps = list()

#Get alphabetically ordered teams to loop through
teamList = list(colourDict.keys())

#Loop through teams
for tt in range(0,len(teamList)):
    
    #Set current squad labels
    currSquadId = teamInfo['squadId'][teamInfo['squadNickname'].index(teamList[tt])]
    currSquadName = teamInfo['squadNickname'][teamInfo['squadId'].index(currSquadId)]

    #Extract a dataframe of shots for the current team during super shot period
    df_currSquadShots = df_scoreFlow.loc[(df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['periodCategory'] == 'twoPoint'),]
    
    #Loop through rounds, extract frequencies for different shots
    #Get number of rounds
    nRounds = max(df_currSquadShots['roundNo'])
    #Set lists to store data in
    madeStandard = list()
    missedStandard = list()
    madeSuper = list()
    missedSuper = list()
    totalShots = list()
    #Get data from each round
    for rr in range(0,nRounds):
        #Loop through quarters within rounds too
        for qq in range(0,4):
            #Made standard shots
            madeStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                      (df_currSquadShots['period'] == qq+1) & 
                                                      (df_currSquadShots['scoreName'] == 'goal'),
                                                      ['roundNo']].count()[0])
            #Missed standard shots
            missedStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                        (df_currSquadShots['period'] == qq+1) & 
                                                        (df_currSquadShots['scoreName'] == 'miss'),
                                                        ['roundNo']].count()[0])
            #Made super shots
            madeSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                   (df_currSquadShots['period'] == qq+1) & 
                                                   (df_currSquadShots['scoreName'] == '2pt Goal'),
                                                   ['roundNo']].count()[0])
            #Missed standard shots
            missedSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                     (df_currSquadShots['period'] == qq+1) & 
                                                     (df_currSquadShots['scoreName'] == '2pt Miss'),
                                                     ['roundNo']].count()[0])
            #Total shots
            totalShots.append(madeStandard[rr]+missedStandard[rr]+madeSuper[rr]+missedSuper[rr])
    
    #Calculate mean and standard deviation for total shots per quarter
    totalShotsM = np.mean(totalShots)
    totalShotsSD = np.std(totalShots)
    
    #Calculate the current teams actual super shot proportions
    teamSuperProps.append((np.sum(madeSuper)+np.sum(missedSuper)) / np.sum(totalShots))  
    
    #Create a truncated normal distribution of the total shots mean/SD
    #Truncate it at 0 so that a team can't get less than no shots
    #Randomly sample values from the distribution to use in simulations
    
    #Sample from truncated normal distribution with mean/SD parameters
    #We choose to sample between the 95% CI of the mean here. This might
    #mean shots sometimes go below zero, but we have a check in place to not
    #analyse these later (although this is unlikely to happen...)
    lowLim = totalShotsM - (1.96 * (totalShotsSD / math.sqrt(len(totalShots))))
    uppLim = totalShotsM + (1.96 * (totalShotsSD / math.sqrt(len(totalShots))))
    nShotVals = stats.truncnorm((lowLim - totalShotsM) / totalShotsSD,
                                (uppLim - totalShotsM) / totalShotsSD,
                                loc = totalShotsM, scale = totalShotsSD).rvs(nSims)
    #Round shot values to nearest whole number
    nShotVals = np.around(nShotVals)
    
    #Calculate made and missed shots from the different zones for beta distributions
    totalMadeStandard = np.sum(madeStandard)
    totalMissedStandard = np.sum(missedStandard)
    totalMadeSuper = np.sum(madeSuper)
    totalMissedSuper = np.sum(missedSuper)
    
    #Loop through the different super shot proportions
    for pp in range(0,len(superShotProps)):
        
        #Loop through the simulations
        for nn in range(0,nSims):
            
            #Get the current number of shots for the quarter
            nShots = int(nShotVals[nn])
            
            #Put a check in place to see if any shots are given to the team
            #Simply don't run the analysis if there aren't any shots
            if nShots > 0:
            
                #Set total points counter for current iteration
                totalPts = 0
                
                #Get the standard and super shot attempts based on proportion
                nSuper = nShots * superShotProps[pp]
                #Round to ensure a whole number
                nSuper = int(np.around(nSuper))
                #Get standard based on difference
                nStandard = int(nShots - nSuper)
            
                #Calculate the actual proportion of the current super shot number
                actualProp = nSuper / nShots
                
                #Set super shot category bin
                if actualProp <= 0.1:
                    propCat = '0%-10%'
                elif actualProp > 0.1 and actualProp <= 0.2:
                    propCat = '10%-20%'
                elif actualProp > 0.2 and actualProp <= 0.3:
                    propCat = '20%-30%'
                elif actualProp > 0.3 and actualProp <= 0.4:
                    propCat = '30%-40%'
                elif actualProp > 0.4 and actualProp <= 0.5:
                    propCat = '40%-50%'
                elif actualProp > 0.5 and actualProp <= 0.6:
                    propCat = '50%-60%'
                elif actualProp > 0.6 and actualProp <= 0.7:
                    propCat = '60%-70%'
                elif actualProp > 0.7 and actualProp <= 0.8:
                    propCat = '70%-80%'
                elif actualProp > 0.8 and actualProp <= 0.9:
                    propCat = '80%-90%'
                elif actualProp > 0.9:
                    propCat = '90%-100%'
                
                #Loop through standard shots and determine score
                if nStandard > 0:
                    #Sample shot success probability for the shots from beta distribution
                    shotProb = np.random.beta(totalMadeStandard, totalMissedStandard,
                                              size = nStandard)
                    #Loop through shots            
                    for ss in range(0,nStandard):
                        #Get random number to determine shot success
                        r = random.random()
                        #Check shot success and add to total points if successful
                        if r < shotProb[ss]:
                            totalPts = totalPts + 1
                    
                #Loop through super shots and determine score
                if nSuper > 0:
                    #Sample shot success probability for the shots from beta distribution
                    shotProb = np.random.beta(totalMadeSuper, totalMissedSuper,
                                              size = nSuper)
                    #Loop through shots            
                    for ss in range(0,nSuper):
                        #Get random number to determine shot success
                        r = random.random()
                        #Check shot success and add to total points if successful
                        if r < shotProb[ss]:
                            totalPts = totalPts + 2
                            
                #Store values in dictionary
                superSimResults['squadId'].append(currSquadId)
                superSimResults['squadNickname'].append(currSquadName)
                superSimResults['nShots'].append(nShots)
                superSimResults['nStandard'].append(nStandard)
                superSimResults['nSuper'].append(nSuper)
                superSimResults['superProp'].append(actualProp)
                superSimResults['superPropCat'].append(propCat)
                superSimResults['totalPts'].append(totalPts)

#Convert sim dictionary to dataframe
df_superSimResults = pd.DataFrame.from_dict(superSimResults)

# %% Get 'standard' sims summaries

#Get max and min scores with different proportions

#Get the proportion category names as a list
propCats = df_superSimResults['superPropCat'].unique()

#Calculate proportion of results that maximise and minimise score in each 10% bin

#Set data dictionary to store max results in to
maxSuperSimResults = {'squadNickname': [], 
                      'score': [], 'nShots': [],
                      'actualProp': [], 'superPropCat': []}

#Set data dictionary to store min results in to
minSuperSimResults = {'squadNickname': [], 
                      'score': [], 'nShots': [],
                      'actualProp': [], 'superPropCat': []}

#Loop through teams
for tt in range(0,len(teamList)):
    
    #Extract current teams data
    df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
    
    #Get the number of simulations ran for the current teams shots
    nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
    
    #Loop through sims and extract the values for each to compare
    for nn in range(0,nTeamSims):
        
        #Get the results for each super shot proportion
        currShotResults = list()
        currShotProp = list()
        currShotNo = list()
        for pp in range(0,len(superShotProps)):
            currShotResults.append(df_currTeamSims.iloc[pp*nTeamSims+nn]['totalPts'])
            currShotProp.append(df_currTeamSims.iloc[pp*nTeamSims+nn]['superProp'])
            currShotNo.append(df_currTeamSims.iloc[pp*nTeamSims+nn]['nShots'])
        
        #Find the index of the maximum and minimum score
        mx = max(currShotResults)
        mn = min(currShotResults)
        mxInd = [ii for ii, jj in enumerate(currShotResults) if jj == mx]
        mnInd = [ii for ii, jj in enumerate(currShotResults) if jj == mn]
        #Check and see if there are more than one max, and take the smaller 
        #super shot proportion --- this assumes 'less risk'
        if len(mxInd) > 1:
            #Grab smaller super shot proportion value index
            for mm in range(0,len(mxInd)):
                if mm == 0:
                    #Just grab the first proportion to compare to the next
                    currSmallestProp = currShotProp[mxInd[mm]]
                else:
                    #Check to see if the next one is a smaller proportion
                    if currShotProp[mxInd[mm]] < currSmallestProp:
                        currSmallestProp = currShotProp[mxInd[mm]]
                        
            #Reset the mxInd value
            mxInd = currShotProp.index(currSmallestProp)
            
        else:
            
            #Set mxInd to int
            mxInd = int(mxInd[0])

        #Check and see if there are more than one min, and take the higher 
        #super shot proportion --- this assumes 'less risk'
        if len(mnInd) > 1:
            #Grab smaller super shot proportion value index
            for mm in range(0,len(mnInd)):
                if mm == 0:
                    #Just grab the first proportion to compare to the next
                    currSmallestProp = currShotProp[mnInd[mm]]
                else:
                    #Check to see if the next one is a greater proportion
                    if currShotProp[mnInd[mm]] > currSmallestProp:
                        currSmallestProp = currShotProp[mnInd[mm]]
                        
            #Reset the mxInd value
            mnInd = currShotProp.index(currSmallestProp)
            
        else:
            
            #Set mxInd to int
            mnInd = int(mnInd[0])         
        
        #Set values in data dictionary
        #Max value
        maxSuperSimResults['squadNickname'].append(teamList[tt])
        maxSuperSimResults['score'].append(currShotResults[mxInd])
        maxSuperSimResults['nShots'].append(currShotNo[mxInd])
        maxSuperSimResults['actualProp'].append(currShotProp[mxInd])
        #Min value
        minSuperSimResults['squadNickname'].append(teamList[tt])
        minSuperSimResults['score'].append(currShotResults[mnInd])
        minSuperSimResults['nShots'].append(currShotNo[mnInd])
        minSuperSimResults['actualProp'].append(currShotProp[mnInd])
        
        #Identify which bin the max and min super shot result falls in to, and append
        #Max value
        if currShotProp[mxInd] <= 0.1:
            maxSuperSimResults['superPropCat'].append('0%-10%')
        elif currShotProp[mxInd] > 0.1 and currShotProp[mxInd] <= 0.2:
            maxSuperSimResults['superPropCat'].append('10%-20%')
        elif currShotProp[mxInd] > 0.2 and currShotProp[mxInd] <= 0.3:
            maxSuperSimResults['superPropCat'].append('20%-30%')
        elif currShotProp[mxInd] > 0.3 and currShotProp[mxInd] <= 0.4:
            maxSuperSimResults['superPropCat'].append('30%-40%')
        elif currShotProp[mxInd] > 0.4 and currShotProp[mxInd] <= 0.5:
            maxSuperSimResults['superPropCat'].append('40%-50%')
        elif currShotProp[mxInd] > 0.5 and currShotProp[mxInd] <= 0.6:
            maxSuperSimResults['superPropCat'].append('50%-60%')
        elif currShotProp[mxInd] > 0.6 and currShotProp[mxInd] <= 0.7:
            maxSuperSimResults['superPropCat'].append('60%-70%')
        elif currShotProp[mxInd] > 0.7 and currShotProp[mxInd] <= 0.8:
            maxSuperSimResults['superPropCat'].append('70%-80%')
        elif currShotProp[mxInd] > 0.8 and currShotProp[mxInd] <= 0.9:
            maxSuperSimResults['superPropCat'].append('80%-90%')
        elif currShotProp[mxInd] > 0.9:
            maxSuperSimResults['superPropCat'].append('90%-100%')
        #Min value
        if currShotProp[mnInd] <= 0.1:
            minSuperSimResults['superPropCat'].append('0%-10%')
        elif currShotProp[mnInd] > 0.1 and currShotProp[mnInd] <= 0.2:
            minSuperSimResults['superPropCat'].append('10%-20%')
        elif currShotProp[mnInd] > 0.2 and currShotProp[mnInd] <= 0.3:
            minSuperSimResults['superPropCat'].append('20%-30%')
        elif currShotProp[mnInd] > 0.3 and currShotProp[mnInd] <= 0.4:
            minSuperSimResults['superPropCat'].append('30%-40%')
        elif currShotProp[mnInd] > 0.4 and currShotProp[mnInd] <= 0.5:
            minSuperSimResults['superPropCat'].append('40%-50%')
        elif currShotProp[mnInd] > 0.5 and currShotProp[mnInd] <= 0.6:
            minSuperSimResults['superPropCat'].append('50%-60%')
        elif currShotProp[mnInd] > 0.6 and currShotProp[mnInd] <= 0.7:
            minSuperSimResults['superPropCat'].append('60%-70%')
        elif currShotProp[mnInd] > 0.7 and currShotProp[mnInd] <= 0.8:
            minSuperSimResults['superPropCat'].append('70%-80%')
        elif currShotProp[mnInd] > 0.8 and currShotProp[mnInd] <= 0.9:
            minSuperSimResults['superPropCat'].append('80%-90%')
        elif currShotProp[mnInd] > 0.9:
            minSuperSimResults['superPropCat'].append('90%-100%')

#Convert max sim dictionary to dataframe
df_maxSuperSimResults = pd.DataFrame.from_dict(maxSuperSimResults)
df_minSuperSimResults = pd.DataFrame.from_dict(minSuperSimResults)

#Get counts in each 10% bin for each team and normalise these to the total 
#number of sims the team went through

#Set list to work through of % bins
perBins = ['0%-10%', '10%-20%', '20%-30%', '30%-40%', '40%-50%',
           '50%-60%', '60%-70%', '70%-80%', '80%-90%', '90%-100%']

#Set dictionary to store data into
summaryMaxSimResults = {'squadNickname': [], '0%-10%': [], '10%-20%': [],
                        '20%-30%': [], '30%-40%': [], '40%-50%': [],
                        '50%-60%': [], '60%-70%': [], '70%-80%': [],
                        '80%-90%': [], '90%-100%': [],
                        'meanShots': [], 'minShots': [], 'maxShots': []}
summaryMinSimResults = {'squadNickname': [], '0%-10%': [], '10%-20%': [],
                        '20%-30%': [], '30%-40%': [], '40%-50%': [],
                        '50%-60%': [], '60%-70%': [], '70%-80%': [],
                        '80%-90%': [], '90%-100%': [],
                        'meanShots': [], 'minShots': [], 'maxShots': []}

#Loop through teams
for tt in range(0,len(teamList)):
    
    #Extract current teams data
    df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
    
    #Get the number of simulations ran for the current teams shots
    nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
    
    #Append squadname to dictionary
    summaryMaxSimResults['squadNickname'].append(teamList[tt])
    summaryMinSimResults['squadNickname'].append(teamList[tt])
    
    #Get current team results for each proportion and set in each dictionary list
    for pp in range(0,len(perBins)):
        #Max results
        summaryMaxSimResults[perBins[pp]].append(len(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                               (df_maxSuperSimResults['superPropCat'] == perBins[pp]),]) / nTeamSims)
        #Min results
        summaryMinSimResults[perBins[pp]].append(len(df_maxSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                               (df_minSuperSimResults['superPropCat'] == perBins[pp]),]) / nTeamSims)
    
    #Get the summary of shot statistics for current team
    #Max results
    summaryMaxSimResults['meanShots'].append(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].mean())
    summaryMaxSimResults['minShots'].append(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].min())
    summaryMaxSimResults['maxShots'].append(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].max())
    #Min results
    summaryMinSimResults['meanShots'].append(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].mean())
    summaryMinSimResults['minShots'].append(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].min())
    summaryMinSimResults['maxShots'].append(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].max())
    
#Convert summary dictionary to dataframe
df_summaryMaxSimResults = pd.DataFrame.from_dict(summaryMaxSimResults)  
df_summaryMinSimResults = pd.DataFrame.from_dict(summaryMinSimResults)  

#Export summary table to CSV
#Note that these tables compare the maximum and minimum score for each simulation
#for each team, and demonstrates the percentage of time the max vs. min score falls
#within the different proportion bins
os.chdir('..\\..\\Results\\standardSims\\tables')
df_summaryMaxSimResults.to_csv('standardSuperSimProportionMaxSummary.csv',
                               index = False)
df_summaryMinSimResults.to_csv('standardSuperSimProportionMinSummary.csv',
                               index = False)

#Export each teams proportion they actually use
os.chdir('..\\..\\general')
df_teamSuperProps = pd.DataFrame()
df_teamSuperProps['squadNickname'] = teamList
df_teamSuperProps['actualProp'] = teamSuperProps
df_teamSuperProps.to_csv('actualSuperShotProportions.csv',
                         index = False)

# %% Visualise 'standard' sims

#Create all teams heatmap using fighelper functions
figHelper.allTeamsHeatmap(df_superSimResults, teamList, superShotProps,
                          propCats, teamSuperProps,
                          plotNorm = True, plotAbs = True,
                          saveDir = '..\\standardSims\\figures')

#Create individual team heatmaps with boxplot

#Loop through teams and plot heat grid of their points
for tt in range(0,len(teamList)):
    
    #Plot current team
    figHelper.singleTeamHeatmap(df_superSimResults, superShotProps,
                                propCats, teamSuperProps[tt],
                                teamName = teamList[tt],
                                teamColour = colourDict[teamList[tt]],
                                saveDir = '..\\standardSims\\figures')
    
# %% 'Turnover' super shot simulations

##### TODO: can add an element of turnover risk to super shot attempts (i.e. the
##### likelihood a turnover might arise from setting up a super shot) and remove
##### this shot attempt if a 'turnover' occurs. This element of risk might be 
##### best informed by our other work identifying what level of risk is involved...

# %% 'Competitive' super shot simulations

# This section of code aims to simulate super shot period scenarios between teams
# to compare how teams taking variable proportions of super shots stack up against
# one another. The idea here is that each team within a simulation will get a 
# number of shots that is prportional to the league average during that period,
# take a proportion of super shots associated with this, and compare the simulated
# score margin between the two.

# %% Run 'competitive' sims


##### TODO: currently loop is only doing like for like super shot comparisons,
##### rather than looping through the various iterations


#Set nSims variable for this, in case one wants to change it
nSims = 1000

#Generate values for the number of shpts in power 5 periods across the league
#This also grabs the proportions of these shots performed by the 'home' team as
#a means to later allocate the proportion of the total shots to a team in the sims
leagueShots = list()
homeShots = list()
#Get data from each round
for rr in range(0,nRounds):
    #Loop through match number
    for mm in range(0,4):
        
        #Get home squad ID for identification
        homeSquadId = matchInfo['homeSquadId'][(mm+1)+(rr*4)-1]
        
        #Loop through quarters within rounds too
        for qq in range(0,4):
            #Shot attempt count for current quarter and round
            leagueShots.append(df_scoreFlow.loc[(df_scoreFlow['roundNo'] == rr+1) & 
                                                (df_scoreFlow['matchNo'] == mm+1) &
                                                (df_scoreFlow['period'] == qq+1) & 
                                                (df_scoreFlow['periodCategory'] == 'twoPoint'),
                                                ['roundNo']].count()[0])
            #Home team proportion of these shots
            homeShots.append(df_scoreFlow.loc[(df_scoreFlow['roundNo'] == rr+1) & 
                                                (df_scoreFlow['matchNo'] == mm+1) &
                                                (df_scoreFlow['period'] == qq+1) & 
                                                (df_scoreFlow['squadId'] == homeSquadId) & 
                                                (df_scoreFlow['periodCategory'] == 'twoPoint'),
                                                ['roundNo']].count()[0])
            
#Calculate home team props
leagueProps = np.array(homeShots) / np.array(leagueShots)

#Calculate mean and standard deviation for league shots per power 5
leagueShotsM = np.mean(leagueShots)
leagueShotsSD = np.std(leagueShots)

#Calculate mean and standard deviation for league props per power 5
leaguePropsM = np.mean(leagueProps)
leaguePropsSD = np.std(leagueProps)

#Set numpy seeds for consistent sampling from league distribution
np.random.seed(111)

#Draw samples from a normal distribution of the league shot values
leagueShotVals = np.random.normal(leagueShotsM, leagueShotsSD, nSims)
leagueShotVals = np.around(leagueShotVals) #round values

#Set numpy seeds for consistent sampling from league distribution
np.random.seed(222)

#Draw samples from a normal distribution of the league shot proportions
leaguePropVals = np.random.normal(leaguePropsM, leaguePropsSD, nSims)

#Calculate the two team values to allocate team shots in the sims
teamShotsA = np.around(leagueShotVals * leaguePropVals)
teamShotsB = np.around(leagueShotVals * (1-leaguePropVals))

#Set a dictionary to store simulation results in
compSimResults = {'teamName': [], 'teamSuperProp': [],
                  'teamShots': [], 'teamSuperShots': [], 'teamStandardShots': [],
                  'opponentName': [], 'opponentSuperProp': [],
                  'opponentShots': [], 'opponentSuperShots': [], 'opponentStandardShots': [],
                  'teamScore': [], 'opponentScore': [], 'margin': []}

#Set proportions to compare teams against. In these sims we'll go with 0%, 25%,
#50%, 75% and 100% to separate with a bit more distinction
compProps = np.array([0.0,0.25,0.50,0.75,1.0])

#Loop through teams and run 'competitive' power 5 period sims
for tt in range(0,len(teamList)):
    
    #Set seed to same for each team
    np.random.seed(999)
    random.seed(999)
    
    #Set current squad labels
    currSquadId = teamInfo['squadId'][teamInfo['squadNickname'].index(teamList[tt])]
    
    #Calculate standard and super shot statistics for the current team
    
    #Extract a dataframe of shots for the current team during super shot period
    df_currSquadShots = df_scoreFlow.loc[(df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['periodCategory'] == 'twoPoint'),]
    
    #Loop through rounds, extract frequencies for different shots
    #Set lists to store data in
    madeStandard = list()
    missedStandard = list()
    madeSuper = list()
    missedSuper = list()
    #Get data from each round
    for rr in range(0,nRounds):
        #Loop through quarters within rounds too
        for qq in range(0,4):
            #Made standard shots
            madeStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                      (df_currSquadShots['period'] == qq+1) & 
                                                      (df_currSquadShots['scoreName'] == 'goal'),
                                                      ['roundNo']].count()[0])
            #Missed standard shots
            missedStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                        (df_currSquadShots['period'] == qq+1) & 
                                                        (df_currSquadShots['scoreName'] == 'miss'),
                                                        ['roundNo']].count()[0])
            #Made super shots
            madeSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                   (df_currSquadShots['period'] == qq+1) & 
                                                   (df_currSquadShots['scoreName'] == '2pt Goal'),
                                                   ['roundNo']].count()[0])
            #Missed standard shots
            missedSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                     (df_currSquadShots['period'] == qq+1) & 
                                                     (df_currSquadShots['scoreName'] == '2pt Miss'),
                                                     ['roundNo']].count()[0])

    
    #Calculate made and missed shots from the different zones for beta distributions
    totalMadeStandard = np.sum(madeStandard)
    totalMissedStandard = np.sum(missedStandard)
    totalMadeSuper = np.sum(madeSuper)
    totalMissedSuper = np.sum(missedSuper)
    
    #Calculate the current teams score for different super shot proportions
    #using the team A number of shots
    
    #Set variable for total score and shots
    teamScore = list()
    teamShots = list()
    teamSuperShots = list()
    teamStandardShots = list()
    teamSuperProp = list()    
    
    #Loop through the proportions
    for pp in range(0,len(compProps)):
        
        #Loop through the number of simulations
        for nn in range(0,nSims):
            
            #Set standard and super shot proportions
            superProp = compProps[pp]
            standardProp = 1 - superProp
            
            #Calculate number of standard and super shots to 'take'
            superShots = np.around(teamShotsA[nn] * superProp)
            standardShots = teamShotsA[nn] - superShots
            
            #Set variable to tally current score
            currTeamScore = 0
            
            #Loop through standard shots and add to total
            if standardShots > 0:
                #Sample shot success probability from teams data
                shotProb = np.random.beta(totalMadeStandard, totalMissedStandard,
                                          size = int(standardShots))
                #Loop through shots
                for ss in range(0,int(standardShots)):
                    #Get random number to determine shot success
                    r = random.random()
                    #Check shot success and add to total points if successful
                    if r < shotProb[ss]:
                        currTeamScore = currTeamScore + 1
                        
            #Loop through super shots and add to total
            if superShots > 0:
                #Sample shot success probability from teams data
                shotProb = np.random.beta(totalMadeSuper, totalMissedSuper,
                                          size = int(superShots))
                #Loop through shots
                for ss in range(0,int(superShots)):
                    #Get random number to determine shot success
                    r = random.random()
                    #Check shot success and add to total points if successful
                    if r < shotProb[ss]:
                        currTeamScore = currTeamScore + 2
                        
            #Append data to team list
            teamScore.append(currTeamScore)
            teamShots.append(teamShotsA[nn])
            teamSuperShots.append(superShots)
            teamStandardShots.append(standardShots)
            teamSuperProp.append(compProps[pp])
                    
    #Loop through opponents
    for cc in range(tt+1,len(teamList)):
        
        #Set seed to same for each opponent
        np.random.seed(12345)
        random.seed(12345)
        
        #Set current squad labels
        currSquadId = teamInfo['squadId'][teamInfo['squadNickname'].index(teamList[cc])]
        
        #Calculate standard and super shot statistics for the current opponent
        
        #Extract a dataframe of shots for the current team during super shot period
        df_currSquadShots = df_scoreFlow.loc[(df_scoreFlow['squadId'] == currSquadId) &
                                             (df_scoreFlow['periodCategory'] == 'twoPoint'),]
        
        #Loop through rounds, extract frequencies for different shots
        #Set lists to store data in
        madeStandard = list()
        missedStandard = list()
        madeSuper = list()
        missedSuper = list()
        #Get data from each round
        for rr in range(0,nRounds):
            #Loop through quarters within rounds too
            for qq in range(0,4):
                #Made standard shots
                madeStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                          (df_currSquadShots['period'] == qq+1) & 
                                                          (df_currSquadShots['scoreName'] == 'goal'),
                                                          ['roundNo']].count()[0])
                #Missed standard shots
                missedStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                            (df_currSquadShots['period'] == qq+1) & 
                                                            (df_currSquadShots['scoreName'] == 'miss'),
                                                            ['roundNo']].count()[0])
                #Made super shots
                madeSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                       (df_currSquadShots['period'] == qq+1) & 
                                                       (df_currSquadShots['scoreName'] == '2pt Goal'),
                                                       ['roundNo']].count()[0])
                #Missed standard shots
                missedSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                         (df_currSquadShots['period'] == qq+1) & 
                                                         (df_currSquadShots['scoreName'] == '2pt Miss'),
                                                         ['roundNo']].count()[0])
    
        
        #Calculate made and missed shots from the different zones for beta distributions
        totalMadeStandard = np.sum(madeStandard)
        totalMissedStandard = np.sum(missedStandard)
        totalMadeSuper = np.sum(madeSuper)
        totalMissedSuper = np.sum(missedSuper)
        
        #Calculate the opponents score for different super shot proportions
        #using the team B number of shots
        
        #Loop through the proportions
        for pp in range(0,len(compProps)):
            
            #Set variable for total score and shots
            oppScore = list()
            oppShots = list()
            oppSuperShots = list()
            oppStandardShots = list()
            oppSuperProp = list() 
            
            #Loop through the number of simulations
            for nn in range(0,nSims):
                
                #Set standard and super shot proportions
                superProp = compProps[pp]
                standardProp = 1 - superProp
                
                #Calculate number of standard and super shots to 'take'
                superShots = np.around(teamShotsB[nn] * superProp)
                standardShots = teamShotsB[nn] - superShots
                
                #Set variable to tally current score
                currOppScore = 0
                
                #Loop through standard shots and add to total
                if standardShots > 0:
                    #Sample shot success probability from teams data
                    shotProb = np.random.beta(totalMadeStandard, totalMissedStandard,
                                              size = int(standardShots))
                    #Loop through shots
                    for ss in range(0,int(standardShots)):
                        #Get random number to determine shot success
                        r = random.random()
                        #Check shot success and add to total points if successful
                        if r < shotProb[ss]:
                            currOppScore = currOppScore + 1
                            
                #Loop through super shots and add to total
                if superShots > 0:
                    #Sample shot success probability from teams data
                    shotProb = np.random.beta(totalMadeSuper, totalMissedSuper,
                                              size = int(superShots))
                    #Loop through shots
                    for ss in range(0,int(superShots)):
                        #Get random number to determine shot success
                        r = random.random()
                        #Check shot success and add to total points if successful
                        if r < shotProb[ss]:
                            currOppScore = currOppScore + 2
                            
                #Append data to team list
                oppScore.append(currOppScore)
                oppShots.append(teamShotsB[nn])
                oppSuperShots.append(superShots)
                oppStandardShots.append(standardShots)
                oppSuperProp.append(compProps[pp])
                
            #Within each proportion we duplicate the opposition results
            #so that they can be compared to each of the other teams
            #simulated proportions
            oppScore = oppScore * len(compProps)
            oppShots = oppShots * len(compProps)
            oppSuperShots = oppSuperShots * len(compProps)
            oppStandardShots = oppStandardShots * len(compProps)
            oppSuperProp = oppSuperProp * len(compProps)
                
            #Calculate margin between current opponent proportion and all team scores
            #Append to the data dictionary
            for kk in range(0,len(teamScore)):

                #Main team
                compSimResults['teamName'].append(teamList[tt])
                compSimResults['teamSuperProp'].append(teamSuperProp[kk])
                compSimResults['teamShots'].append(teamShots[kk])
                compSimResults['teamSuperShots'].append(teamSuperShots[kk])
                compSimResults['teamStandardShots'].append(teamStandardShots[kk])
                #Opponent team
                compSimResults['opponentName'].append(teamList[cc])
                compSimResults['opponentSuperProp'].append(oppSuperProp[kk])
                compSimResults['opponentShots'].append(oppShots[kk])
                compSimResults['opponentSuperShots'].append(oppSuperShots[kk])
                compSimResults['opponentStandardShots'].append(oppStandardShots[kk])
                #Scoring
                compSimResults['teamScore'].append(teamScore[kk])
                compSimResults['opponentScore'].append(oppScore[kk])
                compSimResults['margin'].append(teamScore[kk] - oppScore[kk])

#Convert 'competitive' sim results to dataframe
df_compSimResults = pd.DataFrame.from_dict(compSimResults)

# %% Visualise 'competitive' sims

##### TODO: add over to fig helper function

#Identify the max and min margin for axes purposes
minMargin = np.min(df_compSimResults['margin'])
maxMargin = np.max(df_compSimResults['margin'])

#Compare over each iteration of 'match-ups'
for tt in range(0,len(teamList)):
    for cc in range(tt+1,len(teamList)):
        
        #Get each teams colour
        teamCol1 = colourDict[teamList[tt]]
        teamCol2 = colourDict[teamList[cc]]
        
        #Set the subplot figure to plot on
        fig, ax = plt.subplots(figsize=(10, 10), nrows = 5, ncols = 5)
        
        #Loop through the simulated proportions for each team
        for p1 in range(0,len(compProps)):
            for p2 in range(0,len(compProps)):
                
                ####### SOMETHING ODD GOING ON WITH BINS/LABELS?????
                
                #Extract current match up
                df_currComp = df_compSimResults.loc[(df_compSimResults['teamName'] == teamList[tt]) &
                                                    (df_compSimResults['opponentName'] == teamList[cc]) &
                                                    (df_compSimResults['teamSuperProp'] == compProps[p2]) &
                                                    (df_compSimResults['opponentSuperProp'] == compProps[p1]),]
        
                #Calculate number of bins necessary to allocate one margin point to each bin
                nBins = np.max(df_currComp['margin']) - np.min(df_currComp['margin']) + 1
                
                #Plot the current histogram
                hx = sns.distplot(df_currComp['margin'], kde = False,
                                  bins = nBins, color = 'grey',
                                  ax = ax[p1,p2],
                                  hist_kws = {'alpha': 0.75})
                
                #Set x-axes limits to min and max margin overall
                ax[p1,p2].set_xlim([minMargin,maxMargin])
                
                ##### TODO: set x-labels
                        
                #Set colours of each bars depending on bin value
                #Get the unique values of bins in a sorted list
                sortedBinVals = np.sort(df_currComp['margin'].unique())
                for pp in range(0,len(sortedBinVals)):
                    #Check patch value and plot colour accordingly
                    if sortedBinVals[pp] < 0:
                        hx.patches[pp].set_facecolor(teamCol2)
                    elif sortedBinVals[pp] > 0:
                        hx.patches[pp].set_facecolor(teamCol1)
                
                #Add vertical y-line at zero
                ax[p1,p2].axvline(0, color = 'k',
                                  linestyle = '--', linewidth = 1)
            
##### TODO: normalise Y-axes to highest counts, labels etc.
##### TODO: add titles with team proportions
##### TODO: add in-graph notations -- % each teams won; M +/- SD margins?


        
# %%








