# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 21:13:39 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This code initially runs identical analysis to our original PLoS One paper,
    but just using 2020 statistics instead of 2018 data. The major difference here
    is that the super shot was in play, and theoretically would effect the long
    range shooting statistics.
    
    After this a series of different simulations are run based on shooting statistics 
    from the Super Shot period of the Super Netball 2020 season. The main aim of this
    analysis is to understand where optimality may lie for the proportion of a teams
    total shots should be Super Shots.
    
    TODO: Potentially add regression notes...
    
"""

# %% Import packages

#Python packages
import pandas as pd
pd.options.mode.chained_assignment = None #turn off pandas chained warnings
import numpy as np
import scipy.stats as stats
import random
# import seaborn as sns
# import matplotlib.pyplot as plt
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

##### TODO: For public repo of this data --- run this and generate a de-identified
##### database, then just import this database

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

# %% Relative odds of missing from inner vs. outer circle

# This section looks at the probability statistics from shots in the inner circle
# vs. shots in the outer circle and re-evaluates the assessment of whether a 2
# point value is appropriate for the super shot considering the elevated risk of
# taking a shot from this distance.

# The analysis here also takes into account the shot statistics firstly from
# the entire match, but then also looks at just those from the super shot and non-
# super shot perios. This provides a relative risk for missing from the outer 
# circle across various aspects of the match.

#Set the number of trials for random sampling
nTrials = 100000

#Set a check in place for whether to run this analysis or load in existing results
runRelOdds = False ##### change to True to re-run analysis

if runRelOdds:

    #Set dictionary to store values in
    relOddsDict = {'team': [], 'period': [], 'mean': [], 'lower95': [], 'upper95': []}
    relOddsDefDict = {'team': [], 'period': [], 'mean': [], 'lower95': [], 'upper95': []}
    
    # Overall statistics across all teams
    
    #Calculate shot statistics, distributions and random sampling
    
    #Inner circle - all match
    madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                     (df_scoreFlow['shotOutcome'] == True),'shotCircle'])
    missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                       (df_scoreFlow['shotOutcome'] == False),'shotCircle'])
    betaInnerAll = stats.beta(missedShots,madeShots)
    valsInnerAll = np.random.beta(missedShots, madeShots, size = nTrials)
    
    #Outer circle - all match
    madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                     (df_scoreFlow['shotOutcome'] == True),'shotCircle'])
    missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                       (df_scoreFlow['shotOutcome'] == False),'shotCircle'])
    betaOuterAll = stats.beta(missedShots,madeShots)
    valsOuterAll = np.random.beta(missedShots, madeShots, size = nTrials)
    
    #Inner circle - standard period
    madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                     (df_scoreFlow['shotOutcome'] == True) &
                                     (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
    missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                       (df_scoreFlow['shotOutcome'] == False) &
                                       (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
    betaInnerStandard = stats.beta(missedShots,madeShots)
    valsInnerStandard = np.random.beta(missedShots, madeShots, size = nTrials)
    
    #Outer circle - standard period
    madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                     (df_scoreFlow['shotOutcome'] == True) &
                                     (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
    missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                       (df_scoreFlow['shotOutcome'] == False) &
                                       (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
    betaOuterStandard = stats.beta(missedShots,madeShots)
    valsOuterStandard = np.random.beta(missedShots, madeShots, size = nTrials)
    
    #Inner circle - super period
    madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                     (df_scoreFlow['shotOutcome'] == True) &
                                     (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
    missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                       (df_scoreFlow['shotOutcome'] == False) &
                                       (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
    betaInnerSuper = stats.beta(missedShots,madeShots)
    valsInnerSuper = np.random.beta(missedShots, madeShots, size = nTrials)
    
    #Outer circle - super period
    madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                     (df_scoreFlow['shotOutcome'] == True) &
                                     (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
    missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                       (df_scoreFlow['shotOutcome'] == False) &
                                       (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
    betaOuterSuper = stats.beta(missedShots,madeShots)
    valsOuterSuper = np.random.beta(missedShots, madeShots, size = nTrials)
    
    # #Visualise the two distributions as probability density functions over the periods
    # #Set the subplot figure to plot on
    # fig, ax = plt.subplots(figsize=(9, 3), nrows = 1, ncols = 3)
    # x = np.linspace(0,1,1000002)[1:-1] #probability values to plot over
    # #All match
    # ax[0].plot(x, betaInnerAll.pdf(x), ls = '-', c='blue', label = 'Inner Circle')
    # ax[0].plot(x, betaOuterAll.pdf(x), ls = '-', c='red', label = 'Outer Circle')
    # ax[0].set_title(r'$\beta$'' Distributions for Missed Shots: All Match',
    #                 fontweight = 'bold', fontsize = 8)
    # ax[0].set_xlabel('$x$') #x label
    # ax[0].set_ylabel(r'$p(x|\alpha,\beta)$') #y label
    # ax[0].legend() #add legend
    # ax[0].set_xlim(0.0,0.6) #Adjust x-limit for better viewing
    # #Standard period
    # ax[1].plot(x, betaInnerStandard.pdf(x), ls = '-', c='blue', label = 'Inner Circle')
    # ax[1].plot(x, betaOuterStandard.pdf(x), ls = '-', c='red', label = 'Outer Circle')
    # ax[1].set_title(r'$\beta$'' Distributions for Missed Shots: Standard Period',
    #                 fontweight = 'bold', fontsize = 8)
    # ax[1].set_xlabel('$x$') #x label
    # ax[1].set_ylabel(r'$p(x|\alpha,\beta)$') #y label
    # ax[1].legend() #add legend
    # ax[1].set_xlim(0.0,0.6) #Adjust x-limit for better viewing
    # #Super period
    # ax[2].plot(x, betaInnerSuper.pdf(x), ls = '-', c='blue', label = 'Inner Circle')
    # ax[2].plot(x, betaOuterSuper.pdf(x), ls = '-', c='red', label = 'Outer Circle')
    # ax[2].set_title(r'$\beta$'' Distributions for Missed Shots: Power 5 Period',
    #                 fontweight = 'bold', fontsize = 8)
    # ax[2].set_xlabel('$x$') #x label
    # ax[2].set_ylabel(r'$p(x|\alpha,\beta)$') #y label
    # ax[2].legend() #add legend
    # ax[2].set_xlim(0.0,0.6) #Adjust x-limit for better viewing
    # #Tight plot layout
    # plt.tight_layout()
    
    #Determine how much relatively higher odds of missing from outer circle are to
    #the inner circle
    sampleRatiosAll = valsOuterAll/valsInnerAll
    sampleRatiosStandard = valsOuterStandard/valsInnerStandard
    sampleRatiosSuper = valsOuterSuper/valsInnerSuper
    
    # #Visualise the relative sample ratios on a histogram
    # fig, ax = plt.subplots(figsize=(9, 3), nrows = 1, ncols = 3)
    # ax[0].hist(sampleRatiosAll, bins = 'auto')
    # ax[0].set_title('Ratios for Missed Shots in Outer vs. Inner Circle: All Match',
    #                 fontweight = 'bold', fontsize = 6)
    # ax[1].hist(sampleRatiosStandard, bins = 'auto')
    # ax[1].set_title('Ratios for Missed Shots in Outer vs. Inner Circle: Standard Period',
    #                 fontweight = 'bold', fontsize = 6)
    # ax[2].hist(sampleRatiosSuper, bins = 'auto')
    # ax[2].set_title('Ratios for Missed Shots in Outer vs. Inner Circle: Power 5 Period',
    #                 fontweight = 'bold', fontsize = 6)
    # plt.tight_layout()
    
    #Create values for empirical cumulative distribution function
    cdfSplitAll_x = np.sort(sampleRatiosAll)
    cdfSplitStandard_x = np.sort(sampleRatiosStandard)
    cdfSplitSuper_x = np.sort(sampleRatiosSuper)
    cdfSplit_y = np.arange(1, nTrials+1) / nTrials
    
    #Calculate confidence intervals of the cumulative distribution function
    #Find where the CDF y-values equal 0.05/0.95, or the closest index to this,
    #and grab that index of the x-values
    lower95ind = np.where(cdfSplit_y == 0.05)[0][0]
    upper95ind = np.where(cdfSplit_y == 0.95)[0][0]
    ci95_lowerAll = cdfSplitAll_x[lower95ind]
    ci95_upperAll = cdfSplitAll_x[upper95ind]
    ci95_lowerStandard = cdfSplitStandard_x[lower95ind]
    ci95_upperStandard = cdfSplitStandard_x[upper95ind]
    ci95_lowerSuper = cdfSplitSuper_x[lower95ind]
    ci95_upperSuper = cdfSplitSuper_x[upper95ind]
    
    #Store values
    #All match
    relOddsDict['team'].append('all')
    relOddsDict['period'].append('all')
    relOddsDict['mean'].append(sampleRatiosAll.mean())
    relOddsDict['lower95'].append(ci95_lowerAll)
    relOddsDict['upper95'].append(ci95_upperAll)
    #Standard period
    relOddsDict['team'].append('all')
    relOddsDict['period'].append('standard')
    relOddsDict['mean'].append(sampleRatiosStandard.mean())
    relOddsDict['lower95'].append(ci95_lowerStandard)
    relOddsDict['upper95'].append(ci95_upperStandard)
    #Super period
    relOddsDict['team'].append('all')
    relOddsDict['period'].append('super')
    relOddsDict['mean'].append(sampleRatiosSuper.mean())
    relOddsDict['lower95'].append(ci95_lowerSuper)
    relOddsDict['upper95'].append(ci95_upperSuper)
    
    #Create a string that puts these values together and prints
    print('Relative odds [95% CIs] of missing from outer to inner circle all match: '+str(round(sampleRatiosAll.mean(),2)) + ' [' + str(round(ci95_lowerAll,2)) + ',' + str(round(ci95_upperAll,2)) + ']')
    print('Relative odds [95% CIs] of missing from outer to inner circle in standard periods: '+str(round(sampleRatiosStandard.mean(),2)) + ' [' + str(round(ci95_lowerStandard,2)) + ',' + str(round(ci95_upperStandard,2)) + ']')
    print('Relative odds [95% CIs] of missing from outer to inner circle Power 5 periods: '+str(round(sampleRatiosSuper.mean(),2)) + ' [' + str(round(ci95_lowerSuper,2)) + ',' + str(round(ci95_upperSuper,2)) + ']')
    
    #Repeat for each team
    for tt in range(len(df_teamInfo['squadId'])):
        
        #Set current squad ID and name
        currSquadId = df_teamInfo['squadId'][tt]
        currSquadName = df_teamInfo['squadNickname'][tt]
        
        #Calculate shot statistics, distributions and random sampling
        
        #Inner circle - all match
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                         (df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                           (df_scoreFlow['squadId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False),'shotCircle'])
        betaInnerAll = stats.beta(missedShots,madeShots)
        valsInnerAll = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Outer circle - all match
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                         (df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                           (df_scoreFlow['squadId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False),'shotCircle'])
        betaOuterAll = stats.beta(missedShots,madeShots)
        valsOuterAll = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Inner circle - standard period
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                         (df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True) &
                                         (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                           (df_scoreFlow['squadId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False) &
                                           (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
        betaInnerStandard = stats.beta(missedShots,madeShots)
        valsInnerStandard = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Outer circle - standard period
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                         (df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True) &
                                         (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                           (df_scoreFlow['squadId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False) &
                                           (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
        betaOuterStandard = stats.beta(missedShots,madeShots)
        valsOuterStandard = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Inner circle - super period
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                         (df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True) &
                                         (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                           (df_scoreFlow['squadId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False) &
                                           (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
        betaInnerSuper = stats.beta(missedShots,madeShots)
        valsInnerSuper = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Outer circle - super period
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                         (df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True) &
                                         (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                           (df_scoreFlow['squadId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False) &
                                           (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
        betaOuterSuper = stats.beta(missedShots,madeShots)
        valsOuterSuper = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Determine how much relatively higher odds of missing from outer circle are to
        #the inner circle
        sampleRatiosAll = valsOuterAll/valsInnerAll
        sampleRatiosStandard = valsOuterStandard/valsInnerStandard
        sampleRatiosSuper = valsOuterSuper/valsInnerSuper
        
        #Create values for empirical cumulative distribution function
        cdfSplitAll_x = np.sort(sampleRatiosAll)
        cdfSplitStandard_x = np.sort(sampleRatiosStandard)
        cdfSplitSuper_x = np.sort(sampleRatiosSuper)
        cdfSplit_y = np.arange(1, nTrials+1) / nTrials
        
        #Calculate confidence intervals of the cumulative distribution function
        #Find where the CDF y-values equal 0.05/0.95, or the closest index to this,
        #and grab that index of the x-values
        lower95ind = np.where(cdfSplit_y == 0.05)[0][0]
        upper95ind = np.where(cdfSplit_y == 0.95)[0][0]
        ci95_lowerAll = cdfSplitAll_x[lower95ind]
        ci95_upperAll = cdfSplitAll_x[upper95ind]
        ci95_lowerStandard = cdfSplitStandard_x[lower95ind]
        ci95_upperStandard = cdfSplitStandard_x[upper95ind]
        ci95_lowerSuper = cdfSplitSuper_x[lower95ind]
        ci95_upperSuper = cdfSplitSuper_x[upper95ind]
        
        #Store values
        #All match
        relOddsDict['team'].append(currSquadName)
        relOddsDict['period'].append('all')
        relOddsDict['mean'].append(sampleRatiosAll.mean())
        relOddsDict['lower95'].append(ci95_lowerAll)
        relOddsDict['upper95'].append(ci95_upperAll)
        #Standard period
        relOddsDict['team'].append(currSquadName)
        relOddsDict['period'].append('standard')
        relOddsDict['mean'].append(sampleRatiosStandard.mean())
        relOddsDict['lower95'].append(ci95_lowerStandard)
        relOddsDict['upper95'].append(ci95_upperStandard)
        #Super period
        relOddsDict['team'].append(currSquadName)
        relOddsDict['period'].append('super')
        relOddsDict['mean'].append(sampleRatiosSuper.mean())
        relOddsDict['lower95'].append(ci95_lowerSuper)
        relOddsDict['upper95'].append(ci95_upperSuper)
        
        #Create a string that puts these values together and prints
        print('Relative odds [95% CIs] of '+currSquadName+' missing from outer to inner circle all match: '+str(round(sampleRatiosAll.mean(),2)) + ' [' + str(round(ci95_lowerAll,2)) + ',' + str(round(ci95_upperAll,2)) + ']')
        print('Relative odds [95% CIs] of '+currSquadName+' missing from outer to inner circle in standard periods: '+str(round(sampleRatiosStandard.mean(),2)) + ' [' + str(round(ci95_lowerStandard,2)) + ',' + str(round(ci95_upperStandard,2)) + ']')
        print('Relative odds [95% CIs] of '+currSquadName+' missing from outer to inner circle Power 5 periods: '+str(round(sampleRatiosSuper.mean(),2)) + ' [' + str(round(ci95_lowerSuper,2)) + ',' + str(round(ci95_upperSuper,2)) + ']')
    
    #Convert to dataframe
    df_relOdds = pd.DataFrame.from_dict(relOddsDict)
    
    #Visualise and save relative odds data
    figHelper.relOddsVis(df_relOdds, df_teamInfo, colourDict,
                         saveDir = '..\\..\\Results\\relativeOdds\\figures')
    
    #Export tabulated version for text presentation (where needed)
    df_relOdds.to_csv('..\\..\\Results\\relativeOdds\\tables\\RelativeOdds_OuterInner_AllTeams.csv',
                      index = False)
    
    #We repeat a similar analysis here, but instead of the shots being taken we
    #look at shots being taken against a team
    
    #This first requires us to look through the match info and add an opposition id
    #to the score flow data
    oppId = []
    for ss in range(len(df_scoreFlow)):
        #Grab the relevant row data
        currMatch = df_scoreFlow['matchNo'][ss]
        currRound = df_scoreFlow['roundNo'][ss]
        currSquadId = df_scoreFlow['squadId'][ss]
        #Match this up to the match info data and figure out which squad to add
        #to the opposition id list
        currSquads = df_matchInfo.loc[(df_matchInfo['roundNo'] == currRound) &
                                      (df_matchInfo['matchNo'] == currMatch),
                                      ['homeSquadId','awaySquadId']].values.flatten()
        oppId.append(currSquads[np.where(currSquads != currSquadId)[0][0]])
    #Append the new list to the dataframe
    df_scoreFlow['oppId'] = oppId
    
    #Loop through teams and extract their defensive shot statistics
    for tt in range(len(df_teamInfo['squadId'])):
        
        #Set current squad ID and name
        currSquadId = df_teamInfo['squadId'][tt]
        currSquadName = df_teamInfo['squadNickname'][tt]
        
        #Calculate shot statistics, distributions and random sampling
        
        #Inner circle - all match
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                         (df_scoreFlow['oppId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                           (df_scoreFlow['oppId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False),'shotCircle'])
        betaInnerAll = stats.beta(missedShots,madeShots)
        valsInnerAll = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Outer circle - all match
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                         (df_scoreFlow['oppId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                           (df_scoreFlow['oppId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False),'shotCircle'])
        betaOuterAll = stats.beta(missedShots,madeShots)
        valsOuterAll = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Inner circle - standard period
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                         (df_scoreFlow['oppId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True) &
                                         (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                           (df_scoreFlow['oppId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False) &
                                           (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
        betaInnerStandard = stats.beta(missedShots,madeShots)
        valsInnerStandard = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Outer circle - standard period
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                         (df_scoreFlow['oppId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True) &
                                         (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                           (df_scoreFlow['oppId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False) &
                                           (df_scoreFlow['periodCategory'] == 'standard'),'shotCircle'])
        betaOuterStandard = stats.beta(missedShots,madeShots)
        valsOuterStandard = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Inner circle - super period
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                         (df_scoreFlow['oppId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True) &
                                         (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'innerCircle') &
                                           (df_scoreFlow['oppId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False) &
                                           (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
        betaInnerSuper = stats.beta(missedShots,madeShots)
        valsInnerSuper = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Outer circle - super period
        madeShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                         (df_scoreFlow['oppId'] == currSquadId) &
                                         (df_scoreFlow['shotOutcome'] == True) &
                                         (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
        missedShots = len(df_scoreFlow.loc[(df_scoreFlow['shotCircle'] == 'outerCircle') &
                                           (df_scoreFlow['oppId'] == currSquadId) &
                                           (df_scoreFlow['shotOutcome'] == False) &
                                           (df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle'])
        betaOuterSuper = stats.beta(missedShots,madeShots)
        valsOuterSuper = np.random.beta(missedShots, madeShots, size = nTrials)
        
        #Determine how much relatively higher odds of missing from outer circle are to
        #the inner circle
        sampleRatiosAll = valsOuterAll/valsInnerAll
        sampleRatiosStandard = valsOuterStandard/valsInnerStandard
        sampleRatiosSuper = valsOuterSuper/valsInnerSuper
        
        #Create values for empirical cumulative distribution function
        cdfSplitAll_x = np.sort(sampleRatiosAll)
        cdfSplitStandard_x = np.sort(sampleRatiosStandard)
        cdfSplitSuper_x = np.sort(sampleRatiosSuper)
        cdfSplit_y = np.arange(1, nTrials+1) / nTrials
        
        #Calculate confidence intervals of the cumulative distribution function
        #Find where the CDF y-values equal 0.05/0.95, or the closest index to this,
        #and grab that index of the x-values
        lower95ind = np.where(cdfSplit_y == 0.05)[0][0]
        upper95ind = np.where(cdfSplit_y == 0.95)[0][0]
        ci95_lowerAll = cdfSplitAll_x[lower95ind]
        ci95_upperAll = cdfSplitAll_x[upper95ind]
        ci95_lowerStandard = cdfSplitStandard_x[lower95ind]
        ci95_upperStandard = cdfSplitStandard_x[upper95ind]
        ci95_lowerSuper = cdfSplitSuper_x[lower95ind]
        ci95_upperSuper = cdfSplitSuper_x[upper95ind]
        
        #Store values
        #All match
        relOddsDefDict['team'].append(currSquadName)
        relOddsDefDict['period'].append('all')
        relOddsDefDict['mean'].append(sampleRatiosAll.mean())
        relOddsDefDict['lower95'].append(ci95_lowerAll)
        relOddsDefDict['upper95'].append(ci95_upperAll)
        #Standard period
        relOddsDefDict['team'].append(currSquadName)
        relOddsDefDict['period'].append('standard')
        relOddsDefDict['mean'].append(sampleRatiosStandard.mean())
        relOddsDefDict['lower95'].append(ci95_lowerStandard)
        relOddsDefDict['upper95'].append(ci95_upperStandard)
        #Super period
        relOddsDefDict['team'].append(currSquadName)
        relOddsDefDict['period'].append('super')
        relOddsDefDict['mean'].append(sampleRatiosSuper.mean())
        relOddsDefDict['lower95'].append(ci95_lowerSuper)
        relOddsDefDict['upper95'].append(ci95_upperSuper)
        
        #Create a string that puts these values together and prints
        print('Relative odds [95% CIs] of '+currSquadName+' opponents missing from outer to inner circle all match: '+str(round(sampleRatiosAll.mean(),2)) + ' [' + str(round(ci95_lowerAll,2)) + ',' + str(round(ci95_upperAll,2)) + ']')
        print('Relative odds [95% CIs] of '+currSquadName+' opponents missing from outer to inner circle in standard periods: '+str(round(sampleRatiosStandard.mean(),2)) + ' [' + str(round(ci95_lowerStandard,2)) + ',' + str(round(ci95_upperStandard,2)) + ']')
        print('Relative odds [95% CIs] of '+currSquadName+' opponents missing from outer to inner circle Power 5 periods: '+str(round(sampleRatiosSuper.mean(),2)) + ' [' + str(round(ci95_lowerSuper,2)) + ',' + str(round(ci95_upperSuper,2)) + ']')
    
    #Convert to dataframe
    df_relOddsDef = pd.DataFrame.from_dict(relOddsDefDict)
    
    #Visualise and save relative odds data
    figHelper.relOddsDefVis(df_relOddsDef, df_teamInfo, colourDict,
                            saveDir = '..\\..\\Results\\relativeOdds\\figures')
    
    #Export tabulated version for text presentation (where needed)
    df_relOddsDef.to_csv('..\\..\\Results\\relativeOdds\\tables\\RelativeOddsDef_OuterInner_AllTeams.csv',
                         index = False)
    
else:
    
    #Load in the existing dataframes
    df_relOdds = pd.read_csv('..\\..\\Results\\relativeOdds\\tables\\RelativeOdds_OuterInner_AllTeams.csv')
    df_relOddsDef = pd.read_csv('..\\..\\Results\\relativeOdds\\tables\\RelativeOddsDef_OuterInner_AllTeams.csv')

# %% REPEAT ANALYSIS: Tactics (i.e. shot proportions) & scoring with new rules

# #Create a list to test for proportions of shots taken inside vs outside
# insideProportions = np.linspace(1.0,0.0,11)
# insideProportionsStr = list(map(str,np.round(insideProportions,1)))

# #Create a dataframe to store the goals scored values in
# df_goalsScoredSplit = pd.DataFrame([],columns = insideProportionsStr,
#                                    index = range(0,nTrials))
# df_goalsScoredSplit_2pt = pd.DataFrame([],columns = insideProportionsStr,
#                                        index = range(0,nTrials))

# #Calculate average rate of shots each team gets in the Power 5 period
# nMatches = len(df_matchInfo)
# nShotsPer5 = len(df_scoreFlow.loc[(df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle']) / nMatches / 4 / 2 #divided across 4 quarters and 2 teams

# #Loop through the different proportions and calculate goals scored under the two
# #different scoring rules, considering that missed sampling values for the inside
# #and outside shooting are stored in 'valsInnerSuper' and 'valsOuterSuper'. Note 
# #that this means we're considering shot success probability from the actual 
# #Power 5 periods, which is probably the most accurate assumption.

# #Get inside and outside success rates
# insideRates = 1 - valsInnerSuper
# outsideRates = 1 - valsOuterSuper

# #Loop through the different proportions
# for pp in range(0,len(insideProportions)):

#     #Calculate goals scored for current proportion of inside shots
#     #Add the inside and outside rates together
#     #Standard scoring
#     currGoals = (insideRates * nShotsPer5 * insideProportions[pp]) + (outsideRates * nShotsPer5 * (1-insideProportions[pp]))
#     #2pt scoring
#     currGoals_2pt = (insideRates * nShotsPer5 * insideProportions[pp]) + (outsideRates * nShotsPer5 * (1-insideProportions[pp]) * 2)
    
#     #Append to relevant column of dataframe
#     df_goalsScoredSplit[insideProportionsStr[pp]] = currGoals
#     df_goalsScoredSplit_2pt[insideProportionsStr[pp]] = currGoals_2pt

# #Convert the two different results to a manageable dataframe to visualise with seaborn

# #Create a string for the outside shot proportion
# outsideProportion = ['0%','10%','20%','30%','40%','50%','60%','70%','80%','90%','100%']

# #Create an empty dataframe with relevant columns
# df_goalsScoredSplit_comparison = pd.DataFrame(columns = ['Goals Scored','Rule System','Outside Shot Proportion'])

# #Loop through the standard scoring dataframe
# for pp in range(0,len(insideProportions)):
#     #Create temporary matching dataframe to append to main one
#     df_append = pd.DataFrame(columns = ['Goals Scored','Rule System','Outside Shot Proportion'])
#     #Add the goals scored values
#     df_append['Goals Scored'] = df_goalsScoredSplit[insideProportionsStr[pp]]
#     #Set the labelling variables
#     df_append['Rule System'] = 'Standard'
#     df_append['Outside Shot Proportion'] = outsideProportion[pp]
#     #Append to main dataframe
#     df_goalsScoredSplit_comparison = df_goalsScoredSplit_comparison.append(df_append,ignore_index=True)

# #Loop through the new scoring dataframe
# for pp in range(0,len(insideProportions)):
#     #Create temporary matching dataframe to append to main one
#     df_append = pd.DataFrame(columns = ['Goals Scored','Rule System','Outside Shot Proportion'])
#     #Add the goals scored values
#     df_append['Goals Scored'] = df_goalsScoredSplit_2pt[insideProportionsStr[pp]]
#     #Set the labelling variables
#     df_append['Rule System'] = 'Two-Point'
#     df_append['Outside Shot Proportion'] = outsideProportion[pp]
#     #Append to main dataframe
#     df_goalsScoredSplit_comparison = df_goalsScoredSplit_comparison.append(df_append,ignore_index=True)

# #Create bar plot
# fig, ax = plt.subplots(figsize=(6,5))
# gx = sns.barplot(x = 'Outside Shot Proportion',
#                  y = 'Goals Scored',
#                  hue = 'Rule System',   
#                  ci = 'sd',
#                  errcolor= '0.0',
#                  errwidth = 2.0,
#                  capsize = 0.0,
#                  zorder = 5,
#                  palette = ['black','darkgray'],
#                  data = df_goalsScoredSplit_comparison)

# #Set x and y labels
# gx.set(xlabel = 'Proportion of Shots in Outer Circle',
#        ylabel = 'Points Scored')

# #Set y ticks to go from 0-9
# ax.set(ylim = (0.0,7.0))
# ax.yaxis.set_ticks(np.arange(0, 8, step = 1))

# #Outline bars with black
# for patch in ax.patches:
#     patch.set_edgecolor('k')

# #Set legend details
# #Remove legend title
# handles, labels = ax.get_legend_handles_labels()
# ax.legend(handles=handles[0:], labels=labels[0:])
# # plt.setp(ax.get_legend().get_title(), fontweight ='bold')
# plt.setp(ax.get_legend().get_texts(), fontweight = 'bold')

# # NOTE: this approach slightly differs to the simulation approach below, in that
# # it allocates an overall success rate to the scoring (i.e. you get 50% of the
# # score if that's what the overall sucess rate is). This contrasts to below in
# # that each individual shot is given an X% chance of going in, and played against
# # the random probability generator. Due to this, there is basically no chance of
# # the first approach resulting in a score of zero - whereas this can quite readily
# # happen with lower success rates as can be seen in the simulations below.

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

#Set a check in place for whether to run the sims or load in existing results
#Note that the results generated should be the same given the seeds being set
#throughout. If you wish to generate 'new' results then you can alter the seed
#values throughout
runStandardSims = False ##### change to True to re-run sims

if runStandardSims:

    #Set numpy seed for consistency
    np.random.seed(123)
    
    #Set random seed for consistency
    random.seed(123)
    
    #Create dictionary to store data in
    superSimResults = {'squadId': [], 'squadNickname': [],
                       'nShots': [], 'nStandard': [], 'nSuper': [],
                       'shotOutcomeStandard': [], 'shotOutcomeSuper': [],
                       'superProp': [], 'superPropCat': [], 'totalPts': []}
    
    #Set list to store actual team super shot proportions in
    teamSuperProps = list()
    
    #Get alphabetically ordered teams to loop through
    teamList = list(colourDict.keys())
    
    #Loop through teams
    for tt in range(len(teamList)):
        
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
        for rr in range(nRounds):
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
        for pp in range(len(superShotProps)):
            
            #Loop through the simulations
            for nn in range(nSims):
                
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
                    
                    #Set list for storing standard shot outcomes
                    standardOutcome = []                    
                    #Loop through standard shots and determine score
                    if nStandard > 0:
                        #Sample shot success probability for the shots from beta distribution
                        shotProb = np.random.beta(totalMadeStandard, totalMissedStandard,
                                                  size = nStandard)
                        #Loop through shots            
                        for ss in range(nStandard):
                            #Get random number to determine shot success
                            r = random.random()
                            #Check shot success and add to total points if successful
                            if r < shotProb[ss]:
                                #Add to total points
                                totalPts = totalPts + 1
                                #Append shot outcome
                                standardOutcome.append('made')
                            else:
                                #Append shot outcome
                                standardOutcome.append('miss')
                    
                    #Set list for storing super shot outcomes
                    superOutcome = []
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
                                #Add to total points
                                totalPts = totalPts + 2
                                #Append shot outcome
                                superOutcome.append('made')
                            else:
                                #Append shot outcome
                                superOutcome.append('miss')
                                
                    #Store values in dictionary
                    superSimResults['squadId'].append(currSquadId)
                    superSimResults['squadNickname'].append(currSquadName)
                    superSimResults['nShots'].append(nShots)
                    superSimResults['nStandard'].append(nStandard)
                    superSimResults['nSuper'].append(nSuper)
                    superSimResults['superProp'].append(actualProp)
                    superSimResults['superPropCat'].append(propCat)
                    superSimResults['totalPts'].append(totalPts)
                    superSimResults['shotOutcomeStandard'].append(standardOutcome)
                    superSimResults['shotOutcomeSuper'].append(superOutcome)
    
    #Convert sim dictionary to dataframe
    df_superSimResults = pd.DataFrame.from_dict(superSimResults)
    
    #Store the simulation results to file
    df_superSimResults.to_csv('..\\..\\Results\\standardSims\\tables\\superSimResults.csv',
                              index = False)
    
else:
    
    #Get number of rounds (for later use)
    nRounds = max(df_scoreFlow['roundNo'])
    
    #Get alphabetically ordered teams to loop through (for later use)
    teamList = list(colourDict.keys())
    
    #Load the sim data from file
    df_superSimResults = pd.read_csv('..\\..\\Results\\standardSims\\tables\\superSimResults.csv')

# %% Get 'standard' sims summaries

#Get max and min scores with different proportions

#Get the proportion category names as a list
propCats = df_superSimResults['superPropCat'].unique()

#Set list to work through of % bins
perBins = ['0%-10%', '10%-20%', '20%-30%', '30%-40%', '40%-50%',
           '50%-60%', '60%-70%', '70%-80%', '80%-90%', '90%-100%']

#Set a check in place for whether to analyse the sims or just load existing data
analyseStandardSims = False ##### change to True to re-analyse sims

if analyseStandardSims:

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
    
else:
    
    #Load analysis from existing data
    os.chdir('..\\..\\Results\\standardSims\\tables')
    df_summaryMaxSimResults = pd.read_csv('standardSuperSimProportionMaxSummary.csv')
    df_summaryMinSimResults = pd.read_csv('standardSuperSimProportionMinSummary.csv')
    os.chdir('..\\..\\general')
    df_teamSuperProps = pd.read_csv('actualSuperShotProportions.csv')

# %% Visualise 'standard' sims

#Set a check in place for whether to create standard sim visuals
visStandardSims = False ##### change to True to re-do visuals

if visStandardSims:

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
        
else:
    
    #Don't re-do visuals
    print('Visuals not requested.')
    
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

# %% Run competitive sims - matched shots
    
#Set nSims variable for this, in case one wants to change it
nSims = 1000

#Set a check in place for whether to run the competitive sims or just load existing data
#Note that the results generated should be the same given the seeds being set
#throughout. If you wish to generate 'new' results then you can alter the seed
#values throughout
runCompSimsMatched = False ##### change to True to re-run sims

if runCompSimsMatched:

    #Generate values for the number of shots in power 5 periods across the league
    #This also grabs the proportions of these shots performed by the 'home' team as
    #a means to later allocate the proportion of the total shots to a team in the sims
    leagueShots = list()
    #Get data from each round
    for rr in range(nRounds):
        #Loop through match number
        for mm in range(4):
            
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
                   
    #Calculate mean for league shots per power 5
    leagueShotsM = np.mean(leagueShots)
    
    #League shots rounds down to 12
    leagueShotsN = np.round(leagueShotsM)
    
    #Allocate the two team shot values evenly across the sims
    teamShotsA = np.array([leagueShotsN/2] * nSims, dtype = int)
    teamShotsB = np.array([leagueShotsN/2] * nSims, dtype = int)
    
    #Set a dictionary to store simulation results in
    compSimResultsMatched = {'teamName': [], 'teamSuperProp': [],
                              'teamShots': [], 'teamSuperShots': [], 'teamStandardShots': [],
                              'teamShotOutcomeStandard': [], 'teamShotOutcomeSuper': [],
                              'opponentName': [], 'opponentSuperProp': [],
                              'opponentShots': [], 'opponentSuperShots': [], 'opponentStandardShots': [],
                              'opponentShotOutcomeStandard': [], 'opponentShotOutcomeSuper': [],
                              'teamScore': [], 'opponentScore': [], 'margin': []}
    
    #Set proportions to compare teams against. In these sims we'll go with 0%, 33%,
    #50%, 66% and 100% to separate with a bit more distinction & given 6 shots are offerred
    compPropsMatched = np.array([0.0,1/3,1/2,2/3,1.0])
    
    #Loop through teams and run 'competitive' power 5 period sims
    for tt in range(len(teamList)):
        
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
        for rr in range(nRounds):
            #Loop through quarters within rounds too
            for qq in range(4):
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
        teamStandardOutcomes = list()
        teamSuperOutcomes = list()
        
        #Loop through the proportions
        for pp in range(len(compPropsMatched)):
            
            #Loop through the number of simulations
            for nn in range(nSims):
                
                #Set standard and super shot proportions
                superProp = compPropsMatched[pp]
                standardProp = 1 - superProp
                
                #Calculate number of standard and super shots to 'take'
                superShots = np.around(teamShotsA[nn] * superProp)
                standardShots = teamShotsA[nn] - superShots
                
                #Set variable to tally current score
                currTeamScore = 0
                
                #Set list to store standard shot outcomes in
                standardOutcomes = []
                #Loop through standard shots and add to total
                if standardShots > 0:
                    #Sample shot success probability from teams data
                    shotProb = np.random.beta(totalMadeStandard, totalMissedStandard,
                                              size = int(standardShots))
                    #Loop through shots
                    for ss in range(int(standardShots)):
                        #Get random number to determine shot success
                        r = random.random()
                        #Check shot success and add to total points if successful
                        if r < shotProb[ss]:
                            #Add to team score
                            currTeamScore = currTeamScore + 1
                            #Append outcome to list
                            standardOutcomes.append('made')
                        else:
                            #Append outcome to list
                            standardOutcomes.append('miss')
                            
                #Set list to store standard shot outcomes in
                superOutcomes = []
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
                            #Add to team score
                            currTeamScore = currTeamScore + 2
                            #Append outcome to list
                            superOutcomes.append('made')
                        else:
                            #Append outcome to list
                            superOutcomes.append('miss')
                            
                            
                #Append data to team list
                teamScore.append(currTeamScore)
                teamShots.append(teamShotsA[nn])
                teamSuperShots.append(superShots)
                teamStandardShots.append(standardShots)
                teamSuperProp.append(compPropsMatched[pp])
                teamStandardOutcomes.append(standardOutcomes)
                teamSuperOutcomes.append(superOutcomes)
                        
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
            for rr in range(nRounds):
                #Loop through quarters within rounds too
                for qq in range(4):
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
            for pp in range(len(compPropsMatched)):
                
                #Set variable for total score and shots
                oppScore = list()
                oppShots = list()
                oppSuperShots = list()
                oppStandardShots = list()
                oppSuperProp = list()
                oppStandardOutcomes = list()
                oppSuperOutcomes = list()
                
                #Loop through the number of simulations
                for nn in range(nSims):
                    
                    #Set standard and super shot proportions
                    superProp = compPropsMatched[pp]
                    standardProp = 1 - superProp
                    
                    #Calculate number of standard and super shots to 'take'
                    superShots = np.around(teamShotsB[nn] * superProp)
                    standardShots = teamShotsB[nn] - superShots
                    
                    #Set variable to tally current score
                    currOppScore = 0
                    
                    #Set list to store standard shot outcomes in
                    standardOutcomes = []                    
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
                                #Add to opp score
                                currOppScore = currOppScore + 1
                                #Append outcome to list
                                standardOutcomes.append('made')
                            else:
                                #Append outcome to list
                                standardOutcomes.append('miss')
                    
                    #Set list to store standard shot outcomes in
                    superOutcomes = []
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
                                #Add to opp score
                                currOppScore = currOppScore + 2
                                #Append outcome to list
                                superOutcomes.append('made')
                            else:
                                #Append outcome to list
                                superOutcomes.append('miss')
                                
                    #Append data to team list
                    oppScore.append(currOppScore)
                    oppShots.append(teamShotsB[nn])
                    oppSuperShots.append(superShots)
                    oppStandardShots.append(standardShots)
                    oppSuperProp.append(compPropsMatched[pp])
                    oppStandardOutcomes.append(standardOutcomes)
                    oppSuperOutcomes.append(superOutcomes)
                    
                #Within each proportion we duplicate the opposition results
                #so that they can be compared to each of the other teams
                #simulated proportions
                oppScore = oppScore * len(compPropsMatched)
                oppShots = oppShots * len(compPropsMatched)
                oppSuperShots = oppSuperShots * len(compPropsMatched)
                oppStandardShots = oppStandardShots * len(compPropsMatched)
                oppSuperProp = oppSuperProp * len(compPropsMatched)
                oppStandardOutcomes = oppStandardOutcomes * len(compPropsMatched)
                oppSuperOutcomes = oppSuperOutcomes * len(compPropsMatched)
                    
                #Calculate margin between current opponent proportion and all team scores
                #Append to the data dictionary
                for kk in range(len(teamScore)):
    
                    #Main team
                    compSimResultsMatched['teamName'].append(teamList[tt])
                    compSimResultsMatched['teamSuperProp'].append(teamSuperProp[kk])
                    compSimResultsMatched['teamShots'].append(teamShots[kk])
                    compSimResultsMatched['teamSuperShots'].append(teamSuperShots[kk])
                    compSimResultsMatched['teamStandardShots'].append(teamStandardShots[kk])
                    compSimResultsMatched['teamShotOutcomeStandard'].append(teamStandardOutcomes[kk])
                    compSimResultsMatched['teamShotOutcomeSuper'].append(teamSuperOutcomes[kk])
                    #Opponent team
                    compSimResultsMatched['opponentName'].append(teamList[cc])
                    compSimResultsMatched['opponentSuperProp'].append(oppSuperProp[kk])
                    compSimResultsMatched['opponentShots'].append(oppShots[kk])
                    compSimResultsMatched['opponentSuperShots'].append(oppSuperShots[kk])
                    compSimResultsMatched['opponentStandardShots'].append(oppStandardShots[kk])
                    compSimResultsMatched['opponentShotOutcomeStandard'].append(oppStandardOutcomes[kk])
                    compSimResultsMatched['opponentShotOutcomeSuper'].append(oppSuperOutcomes[kk])
                    #Scoring
                    compSimResultsMatched['teamScore'].append(teamScore[kk])
                    compSimResultsMatched['opponentScore'].append(oppScore[kk])
                    compSimResultsMatched['margin'].append(teamScore[kk] - oppScore[kk])
    
    #Convert 'competitive' sim results to dataframe
    df_compSimResultsMatched = pd.DataFrame.from_dict(compSimResultsMatched)
    
    #Write competitive sim results to file
    df_compSimResultsMatched.to_csv('..\\competitiveSimsMatched\\tables\\compSimResultsMatchedShots_all.csv',
                             index = False)

else:
    
    #Define competitive proportions for later use
    compPropsMatched = np.array([0.0,1/3,0.50,2/3,1.0])
    
    #Load existing data
    df_compSimResultsMatched = pd.read_csv('..\\competitiveSimsMatched\\tables\\compSimResultsMatchedShots_all.csv')
    
# %% Visualise 'competitive' sims - matched

#Set a check in place for whether to create standard sim visuals
visCompSimsMatched = True ##### change to True to re-do visuals

if visCompSimsMatched:

    # Firstly, compare each relevant match up between teams to see how these
    # individual comparisons shake out. A better comparison here though is looking
    # at each teams match-up against everyone else in total -- which gives an idea
    # of overall strategy for each team.
    
    #Compare individual teams over each iteration of 'match-ups'
    for tt in range(len(teamList)):
        for cc in range(len(teamList)):
            
            #Set a condition to only plot if team names don't match
            if teamList[tt] != teamList[cc]:
                
                #Set teams
                team1 = teamList[tt]
                team2 = teamList[cc]
                
                #Plot figure
                figHelper.indCompSimVis(df_compSimResultsMatched, team1, team2, compPropsMatched, colourDict,
                                       tt, cc, saveDir = '..\\competitiveSimsMatched\\figures')
    
    #Compare each teams match-ups against all other teams
    for tt in range(len(teamList)):
        
        #Plot figure
        figHelper.allCompSimVis(df_compSimResultsMatched, teamList[tt], compPropsMatched, colourDict,
                                saveDir = '..\\competitiveSimsMatched\\figures')
        
    #Compare grouped results across all teams for super shot proportions
    figHelper.groupedCompSimVis(df_compSimResultsMatched, compPropsMatched,
                                saveDir = '..\\competitiveSimsMatched\\figures')
    
    #Visualise 'competitive' sim margins for each team
    
    #This firstly requires the data to be manipulated into a dataframe with specific
    #variables and columns to suit the seaborn package
    
    #Create dictionary to append these data to
    marginDictMatched = {'teamName': [], 'teamSuperProp': [],
                         'opponentName': [], 'opponentSuperProp': [],
                         'margin': [],
                         'teamShots': [], 'teamSuperShots': [], 'teamStandardShots': [],
                         'teamShootingPer': [], 'teamStandardShootingPer': [], 'teamSuperShootingPer': [],
                         'opponentShots': [], 'opponentSuperShots': [], 'opponentStandardShots': [],
                         'opponentShootingPer': [], 'opponentStandardShootingPer': [], 'opponentSuperShootingPer': []}
    
    #Loop through teams and extract their margin results and the proportions
    for tt in range (len(teamList)):
        
        #Extract teams data
        #This is done separately given the need to modify margin
        df_currTeam1 = df_compSimResultsMatched.loc[(df_compSimResultsMatched['teamName'] == teamList[tt]),]
        df_currTeam2 = df_compSimResultsMatched.loc[(df_compSimResultsMatched['opponentName'] == teamList[tt]),]
        df_currTeam1.reset_index(inplace = True)
        df_currTeam2.reset_index(inplace = True)
        
        #Calculate shooting percentage outcomes for each dataframe
        #Get counts of each made list
        standardTeam1 = []
        superTeam1 = []
        standardTeam2 = []
        superTeam2 = []
        standardOpp1 = []
        superOpp1 = []
        standardOpp2 = []
        superOpp2 = []
        for cc in range(len(df_currTeam1)):
            standardTeam1.append(df_currTeam1['teamShotOutcomeStandard'][cc].count('made'))
            superTeam1.append(df_currTeam1['teamShotOutcomeSuper'][cc].count('made'))
            standardOpp1.append(df_currTeam1['opponentShotOutcomeStandard'][cc].count('made'))
            superOpp1.append(df_currTeam1['opponentShotOutcomeSuper'][cc].count('made'))
        for cc in range(len(df_currTeam2)):
            standardTeam2.append(df_currTeam2['teamShotOutcomeStandard'][cc].count('made'))
            superTeam2.append(df_currTeam2['teamShotOutcomeSuper'][cc].count('made'))
            standardOpp2.append(df_currTeam2['opponentShotOutcomeStandard'][cc].count('made'))
            superOpp2.append(df_currTeam2['opponentShotOutcomeSuper'][cc].count('made'))
        #Calculate shooting percentages at each simulation
        standardPerTeam1 = standardTeam1 / df_currTeam1['teamStandardShots']
        superPerTeam1 = superTeam1 / df_currTeam1['teamSuperShots']
        allPerTeam1 = [x + y for x, y in zip(standardTeam1, superTeam1)] / df_currTeam1['teamShots']
        standardPerTeam2 = standardTeam2 / df_currTeam2['teamStandardShots']
        superPerTeam2 = superTeam2 / df_currTeam2['teamSuperShots']
        allPerTeam2 = [x + y for x, y in zip(standardTeam2, superTeam2)] / df_currTeam2['teamShots']
        standardPerOpp1 = standardOpp1 / df_currTeam1['opponentStandardShots']
        superPerOpp1 = superOpp1 / df_currTeam1['opponentSuperShots']
        allPerOpp1 = [x + y for x, y in zip(standardOpp1, superOpp1)] / df_currTeam1['opponentShots']
        standardPerOpp2 = standardOpp2 / df_currTeam2['opponentStandardShots']
        superPerOpp2 = superOpp2 / df_currTeam2['opponentSuperShots']
        allPerOpp2 = [x + y for x, y in zip(standardOpp2, superOpp2)] / df_currTeam2['opponentShots']
        
        #Add data to dictionary
        #First dataframe - use normal margin and 'team' data
        marginDictMatched['teamName'].extend(list(df_currTeam1['teamName'].values))
        marginDictMatched['teamSuperProp'].extend(list(df_currTeam1['teamSuperProp'].values))
        marginDictMatched['opponentName'].extend(list(df_currTeam1['opponentName'].values))
        marginDictMatched['opponentSuperProp'].extend(list(df_currTeam1['opponentSuperProp'].values))
        marginDictMatched['margin'].extend(list(df_currTeam1['margin'].values))
        marginDictMatched['teamShots'].extend(list(df_currTeam1['teamShots'].values))
        marginDictMatched['teamSuperShots'].extend(list(df_currTeam1['teamSuperShots'].values))
        marginDictMatched['teamStandardShots'].extend(list(df_currTeam1['teamStandardShots'].values))
        marginDictMatched['teamShootingPer'].extend(allPerTeam1)
        marginDictMatched['teamStandardShootingPer'].extend(standardPerTeam1)
        marginDictMatched['teamSuperShootingPer'].extend(superPerTeam1)
        marginDictMatched['opponentShots'].extend(list(df_currTeam1['opponentShots'].values))
        marginDictMatched['opponentSuperShots'].extend(list(df_currTeam1['opponentSuperShots'].values))
        marginDictMatched['opponentStandardShots'].extend(list(df_currTeam1['opponentStandardShots'].values))
        marginDictMatched['opponentShootingPer'].extend(allPerOpp1)
        marginDictMatched['opponentStandardShootingPer'].extend(standardPerOpp1)
        marginDictMatched['opponentSuperShootingPer'].extend(superPerOpp1)
        #Second dataframe - invert margin and use 'opponent' data
        marginDictMatched['teamName'].extend(list(df_currTeam2['opponentName'].values))
        marginDictMatched['teamSuperProp'].extend(list(df_currTeam2['opponentSuperProp'].values))
        marginDictMatched['opponentName'].extend(list(df_currTeam2['teamName'].values))
        marginDictMatched['opponentSuperProp'].extend(list(df_currTeam2['teamSuperProp'].values))
        marginDictMatched['margin'].extend(list(df_currTeam2['margin'].values*-1))
        marginDictMatched['teamShots'].extend(list(df_currTeam2['opponentShots'].values))
        marginDictMatched['teamSuperShots'].extend(list(df_currTeam2['opponentSuperShots'].values))
        marginDictMatched['teamStandardShots'].extend(list(df_currTeam2['opponentStandardShots'].values))
        marginDictMatched['teamShootingPer'].extend(allPerOpp2)
        marginDictMatched['teamStandardShootingPer'].extend(standardPerOpp2)
        marginDictMatched['teamSuperShootingPer'].extend(superPerOpp2)
        marginDictMatched['opponentShots'].extend(list(df_currTeam2['teamShots'].values))
        marginDictMatched['opponentSuperShots'].extend(list(df_currTeam2['teamSuperShots'].values))
        marginDictMatched['opponentStandardShots'].extend(list(df_currTeam2['teamStandardShots'].values))
        marginDictMatched['opponentShootingPer'].extend(allPerTeam2)
        marginDictMatched['opponentStandardShootingPer'].extend(standardPerTeam2)
        marginDictMatched['opponentSuperShootingPer'].extend(superPerTeam2)
        
    #Convert to dataframe
    df_compSimMarginsMatched = pd.DataFrame.from_dict(marginDictMatched)
    
    #Export to file
    df_compSimMarginsMatched.to_csv('..\\competitiveSimsMatched\\tables\\compSimMarginsMatched_all.csv',
                                    index = False)
    
    #Visualise the margins for each team and super shot proportions
    figHelper.marginCompSimVis(df_compSimMarginsMatched, compPropsMatched, colourDict,
                               saveDir = '..\\competitiveSimsMatched\\figures')
    
else:
    
    #Load existing data
    df_compSimMarginsMatched = pd.read_csv('..\\competitiveSimsMatched\\tables\\compSimMarginsMatched_all.csv')

# %% Run 'competitive' sims - variable shots

#Set nSims variable for this, in case one wants to change it
nSims = 1000

#Set a check in place for whether to run the competitive sims or just load existing data
#Note that the results generated should be the same given the seeds being set
#throughout. If you wish to generate 'new' results then you can alter the seed
#values throughout
runCompSims = False ##### change to True to re-run sims

if runCompSims:

    #Generate values for the number of shots in power 5 periods across the league
    #This also grabs the proportions of these shots performed by the 'home' team as
    #a means to later allocate the proportion of the total shots to a team in the sims
    leagueShots = list()
    homeShots = list()
    #Get data from each round
    for rr in range(nRounds):
        #Loop through match number
        for mm in range(4):
            
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
                      'teamShotOutcomeStandard': [], 'teamShotOutcomeSuper': [],
                      'opponentName': [], 'opponentSuperProp': [],
                      'opponentShots': [], 'opponentSuperShots': [], 'opponentStandardShots': [],
                      'opponentShotOutcomeStandard': [], 'opponentShotOutcomeSuper': [],
                      'teamScore': [], 'opponentScore': [], 'margin': []}
    
    #Set proportions to compare teams against. In these sims we'll go with 0%, 25%,
    #50%, 75% and 100% to separate with a bit more distinction
    compProps = np.array([0.0,0.25,0.50,0.75,1.0])
    
    #Loop through teams and run 'competitive' power 5 period sims
    for tt in range(len(teamList)):
        
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
        for rr in range(nRounds):
            #Loop through quarters within rounds too
            for qq in range(4):
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
        teamStandardOutcomes = list()
        teamSuperOutcomes = list()
        
        #Loop through the proportions
        for pp in range(len(compProps)):
            
            #Loop through the number of simulations
            for nn in range(nSims):
                
                #Set standard and super shot proportions
                superProp = compProps[pp]
                standardProp = 1 - superProp
                
                #Calculate number of standard and super shots to 'take'
                superShots = np.around(teamShotsA[nn] * superProp)
                standardShots = teamShotsA[nn] - superShots
                
                #Set variable to tally current score
                currTeamScore = 0
                
                #Set list to store standard shot outcomes in
                standardOutcomes = []
                #Loop through standard shots and add to total
                if standardShots > 0:
                    #Sample shot success probability from teams data
                    shotProb = np.random.beta(totalMadeStandard, totalMissedStandard,
                                              size = int(standardShots))
                    #Loop through shots
                    for ss in range(int(standardShots)):
                        #Get random number to determine shot success
                        r = random.random()
                        #Check shot success and add to total points if successful
                        if r < shotProb[ss]:
                            #Add to team score
                            currTeamScore = currTeamScore + 1
                            #Append outcome to list
                            standardOutcomes.append('made')
                        else:
                            #Append outcome to list
                            standardOutcomes.append('miss')
                            
                #Set list to store standard shot outcomes in
                superOutcomes = []
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
                            #Add to team score
                            currTeamScore = currTeamScore + 2
                            #Append outcome to list
                            superOutcomes.append('made')
                        else:
                            #Append outcome to list
                            superOutcomes.append('miss')
                            
                            
                #Append data to team list
                teamScore.append(currTeamScore)
                teamShots.append(teamShotsA[nn])
                teamSuperShots.append(superShots)
                teamStandardShots.append(standardShots)
                teamSuperProp.append(compProps[pp])
                teamStandardOutcomes.append(standardOutcomes)
                teamSuperOutcomes.append(superOutcomes)
                        
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
            for rr in range(nRounds):
                #Loop through quarters within rounds too
                for qq in range(4):
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
            for pp in range(len(compProps)):
                
                #Set variable for total score and shots
                oppScore = list()
                oppShots = list()
                oppSuperShots = list()
                oppStandardShots = list()
                oppSuperProp = list()
                oppStandardOutcomes = list()
                oppSuperOutcomes = list()
                
                #Loop through the number of simulations
                for nn in range(nSims):
                    
                    #Set standard and super shot proportions
                    superProp = compProps[pp]
                    standardProp = 1 - superProp
                    
                    #Calculate number of standard and super shots to 'take'
                    superShots = np.around(teamShotsB[nn] * superProp)
                    standardShots = teamShotsB[nn] - superShots
                    
                    #Set variable to tally current score
                    currOppScore = 0
                    
                    #Set list to store standard shot outcomes in
                    standardOutcomes = []                    
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
                                #Add to opp score
                                currOppScore = currOppScore + 1
                                #Append outcome to list
                                standardOutcomes.append('made')
                            else:
                                #Append outcome to list
                                standardOutcomes.append('miss')
                    
                    #Set list to store standard shot outcomes in
                    superOutcomes = []
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
                                #Add to opp score
                                currOppScore = currOppScore + 2
                                #Append outcome to list
                                superOutcomes.append('made')
                            else:
                                #Append outcome to list
                                superOutcomes.append('miss')
                                
                    #Append data to team list
                    oppScore.append(currOppScore)
                    oppShots.append(teamShotsB[nn])
                    oppSuperShots.append(superShots)
                    oppStandardShots.append(standardShots)
                    oppSuperProp.append(compProps[pp])
                    oppStandardOutcomes.append(standardOutcomes)
                    oppSuperOutcomes.append(superOutcomes)
                    
                #Within each proportion we duplicate the opposition results
                #so that they can be compared to each of the other teams
                #simulated proportions
                oppScore = oppScore * len(compProps)
                oppShots = oppShots * len(compProps)
                oppSuperShots = oppSuperShots * len(compProps)
                oppStandardShots = oppStandardShots * len(compProps)
                oppSuperProp = oppSuperProp * len(compProps)
                oppStandardOutcomes = oppStandardOutcomes * len(compProps)
                oppSuperOutcomes = oppSuperOutcomes * len(compProps)
                    
                #Calculate margin between current opponent proportion and all team scores
                #Append to the data dictionary
                for kk in range(len(teamScore)):
    
                    #Main team
                    compSimResults['teamName'].append(teamList[tt])
                    compSimResults['teamSuperProp'].append(teamSuperProp[kk])
                    compSimResults['teamShots'].append(teamShots[kk])
                    compSimResults['teamSuperShots'].append(teamSuperShots[kk])
                    compSimResults['teamStandardShots'].append(teamStandardShots[kk])
                    compSimResults['teamShotOutcomeStandard'].append(teamStandardOutcomes[kk])
                    compSimResults['teamShotOutcomeSuper'].append(teamSuperOutcomes[kk])
                    #Opponent team
                    compSimResults['opponentName'].append(teamList[cc])
                    compSimResults['opponentSuperProp'].append(oppSuperProp[kk])
                    compSimResults['opponentShots'].append(oppShots[kk])
                    compSimResults['opponentSuperShots'].append(oppSuperShots[kk])
                    compSimResults['opponentStandardShots'].append(oppStandardShots[kk])
                    compSimResults['opponentShotOutcomeStandard'].append(oppStandardOutcomes[kk])
                    compSimResults['opponentShotOutcomeSuper'].append(oppSuperOutcomes[kk])
                    #Scoring
                    compSimResults['teamScore'].append(teamScore[kk])
                    compSimResults['opponentScore'].append(oppScore[kk])
                    compSimResults['margin'].append(teamScore[kk] - oppScore[kk])
    
    #Convert 'competitive' sim results to dataframe
    df_compSimResults = pd.DataFrame.from_dict(compSimResults)
    
    #Write competitive sim results to file
    df_compSimResults.to_csv('..\\competitiveSims\\tables\\compSimResults_all.csv',
                             index = False)

else:
    
    #Define competitive proportions for later use
    compProps = np.array([0.0,0.25,0.50,0.75,1.0])
    
    #Load existing data
    df_compSimResults = pd.read_csv('..\\competitiveSims\\tables\\compSimResults_all.csv')

# %% Visualise 'competitive' sims

#Set a check in place for whether to create standard sim visuals
visCompSims = False ##### change to True to re-do visuals

if visCompSims:

    # Firstly, compare each relevant match up between teams to see how these
    # individual comparisons shake out. A better comparison here though is looking
    # at each teams match-up against everyone else in total -- which gives an idea
    # of overall strategy for each team.
    
    #Compare individual teams over each iteration of 'match-ups'
    for tt in range(len(teamList)):
        for cc in range(len(teamList)):
            
            #Set a condition to only plot if team names don't match
            if teamList[tt] != teamList[cc]:
                
                #Set teams
                team1 = teamList[tt]
                team2 = teamList[cc]
                
                #Plot figure
                figHelper.indCompSimVis(df_compSimResults, team1, team2, compProps, colourDict,
                                       tt, cc, saveDir = '..\\competitiveSims\\figures')
    
    #Compare each teams match-ups against all other teams
    for tt in range(len(teamList)):
        
        #Plot figure
        figHelper.allCompSimVis(df_compSimResults, teamList[tt], compProps, colourDict,
                                saveDir = '..\\competitiveSims\\figures')
        
    #Compare grouped results across all teams for super shot proportions
    figHelper.groupedCompSimVis(df_compSimResults, compProps,
                                saveDir = '..\\competitiveSims\\figures')
    
    #Visualise 'competitive' sim margins for each team
    
    #This firstly requires the data to be manipulated into a dataframe with specific
    #variables and columns to suit the seaborn package
    
    #Create dictionary to append these data to
    marginDict = {'teamName': [], 'teamSuperProp': [],
                  'opponentName': [], 'opponentSuperProp': [],
                  'margin': [],
                  'teamShots': [], 'teamSuperShots': [], 'teamStandardShots': [],
                  'teamShootingPer': [], 'teamStandardShootingPer': [], 'teamSuperShootingPer': [],
                  'opponentShots': [], 'opponentSuperShots': [], 'opponentStandardShots': [],
                  'opponentShootingPer': [], 'opponentStandardShootingPer': [], 'opponentSuperShootingPer': []}
    
    #Loop through teams and extract their margin results and the proportions
    for tt in range (len(teamList)):
        
        #Extract teams data
        #This is done separately given the need to modify margin
        df_currTeam1 = df_compSimResults.loc[(df_compSimResults['teamName'] == teamList[tt]),]
        df_currTeam2 = df_compSimResults.loc[(df_compSimResults['opponentName'] == teamList[tt]),]
        df_currTeam1.reset_index(inplace = True)
        df_currTeam2.reset_index(inplace = True)
        
        #Calculate shooting percentage outcomes for each dataframe
        #Get counts of each made list
        standardTeam1 = []
        superTeam1 = []
        standardTeam2 = []
        superTeam2 = []
        standardOpp1 = []
        superOpp1 = []
        standardOpp2 = []
        superOpp2 = []
        for cc in range(len(df_currTeam1)):
            standardTeam1.append(df_currTeam1['teamShotOutcomeStandard'][cc].count('made'))
            superTeam1.append(df_currTeam1['teamShotOutcomeSuper'][cc].count('made'))
            standardOpp1.append(df_currTeam1['opponentShotOutcomeStandard'][cc].count('made'))
            superOpp1.append(df_currTeam1['opponentShotOutcomeSuper'][cc].count('made'))
        for cc in range(len(df_currTeam2)):
            standardTeam2.append(df_currTeam2['teamShotOutcomeStandard'][cc].count('made'))
            superTeam2.append(df_currTeam2['teamShotOutcomeSuper'][cc].count('made'))
            standardOpp2.append(df_currTeam2['opponentShotOutcomeStandard'][cc].count('made'))
            superOpp2.append(df_currTeam2['opponentShotOutcomeSuper'][cc].count('made'))
        #Calculate shooting percentages at each simulation
        standardPerTeam1 = standardTeam1 / df_currTeam1['teamStandardShots']
        superPerTeam1 = superTeam1 / df_currTeam1['teamSuperShots']
        allPerTeam1 = [x + y for x, y in zip(standardTeam1, superTeam1)] / df_currTeam1['teamShots']
        standardPerTeam2 = standardTeam2 / df_currTeam2['teamStandardShots']
        superPerTeam2 = superTeam2 / df_currTeam2['teamSuperShots']
        allPerTeam2 = [x + y for x, y in zip(standardTeam2, superTeam2)] / df_currTeam2['teamShots']
        standardPerOpp1 = standardOpp1 / df_currTeam1['opponentStandardShots']
        superPerOpp1 = superOpp1 / df_currTeam1['opponentSuperShots']
        allPerOpp1 = [x + y for x, y in zip(standardOpp1, superOpp1)] / df_currTeam1['opponentShots']
        standardPerOpp2 = standardOpp2 / df_currTeam2['opponentStandardShots']
        superPerOpp2 = superOpp2 / df_currTeam2['opponentSuperShots']
        allPerOpp2 = [x + y for x, y in zip(standardOpp2, superOpp2)] / df_currTeam2['opponentShots']
        
        #Add data to dictionary
        #First dataframe - use normal margin and 'team' data
        marginDict['teamName'].extend(list(df_currTeam1['teamName'].values))
        marginDict['teamSuperProp'].extend(list(df_currTeam1['teamSuperProp'].values))
        marginDict['opponentName'].extend(list(df_currTeam1['opponentName'].values))
        marginDict['opponentSuperProp'].extend(list(df_currTeam1['opponentSuperProp'].values))
        marginDict['margin'].extend(list(df_currTeam1['margin'].values))
        marginDict['teamShots'].extend(list(df_currTeam1['teamShots'].values))
        marginDict['teamSuperShots'].extend(list(df_currTeam1['teamSuperShots'].values))
        marginDict['teamStandardShots'].extend(list(df_currTeam1['teamStandardShots'].values))
        marginDict['teamShootingPer'].extend(allPerTeam1)
        marginDict['teamStandardShootingPer'].extend(standardPerTeam1)
        marginDict['teamSuperShootingPer'].extend(superPerTeam1)
        marginDict['opponentShots'].extend(list(df_currTeam1['opponentShots'].values))
        marginDict['opponentSuperShots'].extend(list(df_currTeam1['opponentSuperShots'].values))
        marginDict['opponentStandardShots'].extend(list(df_currTeam1['opponentStandardShots'].values))
        marginDict['opponentShootingPer'].extend(allPerOpp1)
        marginDict['opponentStandardShootingPer'].extend(standardPerOpp1)
        marginDict['opponentSuperShootingPer'].extend(superPerOpp1)
        #Second dataframe - invert margin and use 'opponent' data
        marginDict['teamName'].extend(list(df_currTeam2['opponentName'].values))
        marginDict['teamSuperProp'].extend(list(df_currTeam2['opponentSuperProp'].values))
        marginDict['opponentName'].extend(list(df_currTeam2['teamName'].values))
        marginDict['opponentSuperProp'].extend(list(df_currTeam2['teamSuperProp'].values))
        marginDict['margin'].extend(list(df_currTeam2['margin'].values*-1))
        marginDict['teamShots'].extend(list(df_currTeam2['opponentShots'].values))
        marginDict['teamSuperShots'].extend(list(df_currTeam2['opponentSuperShots'].values))
        marginDict['teamStandardShots'].extend(list(df_currTeam2['opponentStandardShots'].values))
        marginDict['teamShootingPer'].extend(allPerOpp2)
        marginDict['teamStandardShootingPer'].extend(standardPerOpp2)
        marginDict['teamSuperShootingPer'].extend(superPerOpp2)
        marginDict['opponentShots'].extend(list(df_currTeam2['teamShots'].values))
        marginDict['opponentSuperShots'].extend(list(df_currTeam2['teamSuperShots'].values))
        marginDict['opponentStandardShots'].extend(list(df_currTeam2['teamStandardShots'].values))
        marginDict['opponentShootingPer'].extend(allPerTeam2)
        marginDict['opponentStandardShootingPer'].extend(standardPerTeam2)
        marginDict['opponentSuperShootingPer'].extend(superPerTeam2)
        
    #Convert to dataframe
    df_compSimMargins = pd.DataFrame.from_dict(marginDict)
    
    #Export to file
    df_compSimMargins.to_csv('..\\competitiveSims\\tables\\compSimMargins_all.csv',
                             index = False)
    
    #Visualise the margins for each team and super shot proportions
    figHelper.marginCompSimVis(df_compSimMargins, compProps, colourDict,
                               saveDir = '..\\competitiveSims\\figures')
    
else:
    
    #Load existing data
    df_compSimMargins = pd.read_csv('..\\competitiveSims\\tables\\compSimMargins_all.csv')

# %% Collate competitive sim results

#Generate a table with each teams margin +/- 95% CI's for the different proportions
#Generate a similar looking table that records win proportion for each of these comparisons

#Set lists to store data in
rowCats = []

#Loop through teams
for tt in range(len(teamList)):
    
    #Set lists to store win and loss props in
    winProps = []
    lossProps = []
    
    #Set lists to store margin data in
    summData = []
    
    #Loop through the simulated proportions for each team
    for p1 in range(0,len(compProps)):
        for p2 in range(0,len(compProps)):
            
            #Create text label for current summary on first team run through
            if tt == 0:
                rowLabel = 'Team '+str(int(compProps[p1]*100))+'% / '+'Opp. '+str(int(compProps[p2]*100))+'%'
                rowCats.append(rowLabel)
            
            #Extract current teams data and the relevant proportions
            #Note this is done separately to account for the fact that sometimes
            #the current team might be the 'team' or the 'opponent'
            df_currComp1 = df_compSimResults.loc[(df_compSimResults['teamName'] == teamList[tt]) &
                                                 (df_compSimResults['teamSuperProp'] == compProps[p2])&
                                                 (df_compSimResults['opponentName'] != teamList[tt]) &
                                                 (df_compSimResults['opponentSuperProp'] == compProps[p1]),]
            df_currComp2 = df_compSimResults.loc[(df_compSimResults['opponentName'] == teamList[tt]) &
                                                 (df_compSimResults['opponentSuperProp'] == compProps[p2]) &
                                                 (df_compSimResults['teamName'] != teamList[tt]) &
                                                 (df_compSimResults['teamSuperProp'] == compProps[p1]),]
            #For the second dataframe, the margin needs to be flipped to be
            #relative to the current team of interest
            df_currComp2['margin'] = df_currComp2['margin'] * -1
            
            #Now the two dataframes can be concatenated together
            df_currComp = pd.concat([df_currComp1,df_currComp2])
            
            #Calculate proportion of wins & losses for current 'team'
            winProps.append(sum(n > 0 for n in list(df_currComp['margin'])) / len(df_currComp['margin']))
            lossProps.append(sum(n < 0 for n in list(df_currComp['margin'])) / len(df_currComp['margin']))
            
            #Calculate mean and SD win and loss margins
            marginM = df_currComp['margin'].mean()
            marginCI_plus = df_currComp['margin'].mean() + (1.96 * (df_currComp['margin'].std() / np.sqrt(nSims)))
            marginCI_minus = df_currComp['margin'].mean() - (1.96 * (df_currComp['margin'].std() / np.sqrt(nSims)))
            summData.append('{:.2f}'.format(marginM)+' ['+'{:.2f}'.format(marginCI_minus)+', '+
                            '{:.2f}'.format(marginCI_plus)+']')

    #Create the dataframe with the row labels on first iteration
    if tt == 0:
        df_compSimMarginSummary = pd.DataFrame(data = None, index = rowCats)
    
    #Add the summary data to the dataframe
    df_compSimMarginSummary[teamList[tt]] = summData
    
    ##### TODO: append an 'All' category to final column of table...
    
    ##### TODO: incorporate win/loss proportions table too...
    
#Export to csv
df_compSimMarginSummary.to_csv('..\\competitiveSims\\tables\\compSimMargins_summary.csv',
                               index = True)

            
    

# %% TODO: REPORTING

#Tabulating major findings of study - win percentages across different teams/comparisons
#Individual teams, but probably tabulate grouped ones too    

# Add some summary statistics (mean, range, IQR's etc.) printed out to table
# Essentially the box plot data in tabular form

# Summary figures/tables across individual teams as the data points to group data

        
# %% TODO: ANALYSIS

# Regression model to determine important factors in determining super shot 
# period margin...

# Attempt to create a bayesian linear model for the Fever's outcomes vs. Firebirds (for size)
# Fever is easiest as don't need to mess with inverted margins yet...

#See: https://github.com/WillKoehrsen/Data-Analysis/blob/master/bayesian_lr/Bayesian%20Linear%20Regression%20Project.ipynb

#Extract team
df_currTeam = df_compSimMargins.loc[(df_compSimMargins['teamName'] == 'Fever') &
                                    (df_compSimMargins['opponentName'] == 'Firebirds'),]
### Need opponent name check to for others probably?

#Convert nan's to zero
##### TODO: Probably better to remove these for inaccuracy 
df_currTeam.fillna(0, inplace = True)

#Drop the opponent and team name
df_currTeam.drop('opponentName', inplace = True, axis = 1)
df_currTeam.drop('teamName', inplace = True, axis = 1)

#Just use all variables here
#There's probably some double up here with total shots, and then standard/super shots
#Also consider relative variables (i.e. team took 1.5x higher proportion of super shots)
#This is probably better as it captures the variability between teams better

#Check if super shot proportion is an actual continuous calculation or categorical?

#Split data into train (70%) and test (30%)
from sklearn.model_selection import train_test_split
labels = df_currTeam['margin']
X_train, X_test, y_train, y_test = train_test_split(df_currTeam, labels, 
                                                    test_size = 0.30,
                                                    random_state = 123)


#Create the formula for the regression problem
formula = 'margin ~ ' + ' + '.join(['%s' % variable for variable in X_train.columns[1:]])
# formula

#Build a bayesian model using somewhat standard parameters
import pymc3 as pm
with pm.Model() as normal_model:
    
    # The prior for the model parameters will be a normal distribution
    family = pm.glm.families.Normal()
    
    # Creating the model requires a formula and data (and optionally a family)
    pm.GLM.from_formula(formula, data = X_train, family = family)
    
    # Perform Markov Chain Monte Carlo sampling
    normal_trace = pm.sample(draws=2000, chains = 2, tune = 500)
    
    #### this potentially takes a long time?

#### don't think the model works that great?


