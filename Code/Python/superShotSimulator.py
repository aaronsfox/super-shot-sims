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
    
"""

# %% Import packages

#Python packages
import pandas as pd
pd.options.mode.chained_assignment = None #turn off pandas chained warnings
import numpy as np
import scipy.stats as stats
import random
import seaborn as sns
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

# %% REPEAT ANALYSIS: Relative odds of missing

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

#Visualise the two distributions as probability density functions over the periods
#Set the subplot figure to plot on
fig, ax = plt.subplots(figsize=(9, 3), nrows = 1, ncols = 3)
x = np.linspace(0,1,1000002)[1:-1] #probability values to plot over
#All match
ax[0].plot(x, betaInnerAll.pdf(x), ls = '-', c='blue', label = 'Inner Circle')
ax[0].plot(x, betaOuterAll.pdf(x), ls = '-', c='red', label = 'Outer Circle')
ax[0].set_title(r'$\beta$'' Distributions for Missed Shots: All Match',
                fontweight = 'bold', fontsize = 8)
ax[0].set_xlabel('$x$') #x label
ax[0].set_ylabel(r'$p(x|\alpha,\beta)$') #y label
ax[0].legend() #add legend
ax[0].set_xlim(0.0,0.6) #Adjust x-limit for better viewing
#Standard period
ax[1].plot(x, betaInnerStandard.pdf(x), ls = '-', c='blue', label = 'Inner Circle')
ax[1].plot(x, betaOuterStandard.pdf(x), ls = '-', c='red', label = 'Outer Circle')
ax[1].set_title(r'$\beta$'' Distributions for Missed Shots: Standard Period',
                fontweight = 'bold', fontsize = 8)
ax[1].set_xlabel('$x$') #x label
ax[1].set_ylabel(r'$p(x|\alpha,\beta)$') #y label
ax[1].legend() #add legend
ax[1].set_xlim(0.0,0.6) #Adjust x-limit for better viewing
#Super period
ax[2].plot(x, betaInnerSuper.pdf(x), ls = '-', c='blue', label = 'Inner Circle')
ax[2].plot(x, betaOuterSuper.pdf(x), ls = '-', c='red', label = 'Outer Circle')
ax[2].set_title(r'$\beta$'' Distributions for Missed Shots: Power 5 Period',
                fontweight = 'bold', fontsize = 8)
ax[2].set_xlabel('$x$') #x label
ax[2].set_ylabel(r'$p(x|\alpha,\beta)$') #y label
ax[2].legend() #add legend
ax[2].set_xlim(0.0,0.6) #Adjust x-limit for better viewing
#Tight plot layout
plt.tight_layout()

#Determine how much relatively higher odds of missing from outer circle are to
#the inner circle
sampleRatiosAll = valsOuterAll/valsInnerAll
sampleRatiosStandard = valsOuterStandard/valsInnerStandard
sampleRatiosSuper = valsOuterSuper/valsInnerSuper

#Visualise the relative sample ratios on a histogram
fig, ax = plt.subplots(figsize=(9, 3), nrows = 1, ncols = 3)
ax[0].hist(sampleRatiosAll, bins = 'auto')
ax[0].set_title('Ratios for Missed Shots in Outer vs. Inner Circle: All Match',
                fontweight = 'bold', fontsize = 6)
ax[1].hist(sampleRatiosStandard, bins = 'auto')
ax[1].set_title('Ratios for Missed Shots in Outer vs. Inner Circle: Standard Period',
                fontweight = 'bold', fontsize = 6)
ax[2].hist(sampleRatiosSuper, bins = 'auto')
ax[2].set_title('Ratios for Missed Shots in Outer vs. Inner Circle: Power 5 Period',
                fontweight = 'bold', fontsize = 6)
plt.tight_layout()

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

#Create a string that puts these values together and prints
print('Relative odds [95% CIs] of missing from outer to inner circle all match: '+str(round(sampleRatiosAll.mean(),2)) + ' [' + str(round(ci95_lowerAll,2)) + ',' + str(round(ci95_upperAll,2)) + ']')
print('Relative odds [95% CIs] of missing from outer to inner circle in standard periods: '+str(round(sampleRatiosStandard.mean(),2)) + ' [' + str(round(ci95_lowerStandard,2)) + ',' + str(round(ci95_upperStandard,2)) + ']')
print('Relative odds [95% CIs] of missing from outer to inner circle Power 5 periods: '+str(round(sampleRatiosSuper.mean(),2)) + ' [' + str(round(ci95_lowerSuper,2)) + ',' + str(round(ci95_upperSuper,2)) + ']')

# %% REPEAT ANALYSIS: Tactics (i.e. shot proportions) & scoring with new rules

#Create a list to test for proportions of shots taken inside vs outside
insideProportions = np.linspace(1.0,0.0,11)
insideProportionsStr = list(map(str,np.round(insideProportions,1)))

#Create a dataframe to store the goals scored values in
df_goalsScoredSplit = pd.DataFrame([],columns = insideProportionsStr,
                                   index = range(0,nTrials))
df_goalsScoredSplit_2pt = pd.DataFrame([],columns = insideProportionsStr,
                                       index = range(0,nTrials))

#Calculate average rate of shots each team gets in the Power 5 period
nMatches = len(df_matchInfo)
nShotsPer5 = len(df_scoreFlow.loc[(df_scoreFlow['periodCategory'] == 'twoPoint'),'shotCircle']) / nMatches / 4 / 2 #divided across 4 quarters and 2 teams

#Loop through the different proportions and calculate goals scored under the two
#different scoring rules, considering that missed sampling values for the inside
#and outside shooting are stored in 'valsInnerSuper' and 'valsOuterSuper'. Note 
#that this means we're considering shot success probability from the actual 
#Power 5 periods, which is probably the most accurate assumption.

#Get inside and outside success rates
insideRates = 1 - valsInnerSuper
outsideRates = 1 - valsOuterSuper

#Loop through the different proportions
for pp in range(0,len(insideProportions)):

    #Calculate goals scored for current proportion of inside shots
    #Add the inside and outside rates together
    #Standard scoring
    currGoals = (insideRates * nShotsPer5 * insideProportions[pp]) + (outsideRates * nShotsPer5 * (1-insideProportions[pp]))
    #2pt scoring
    currGoals_2pt = (insideRates * nShotsPer5 * insideProportions[pp]) + (outsideRates * nShotsPer5 * (1-insideProportions[pp]) * 2)
    
    #Append to relevant column of dataframe
    df_goalsScoredSplit[insideProportionsStr[pp]] = currGoals
    df_goalsScoredSplit_2pt[insideProportionsStr[pp]] = currGoals_2pt

#Convert the two different results to a manageable dataframe to visualise with seaborn

#Create a string for the outside shot proportion
outsideProportion = ['0%','10%','20%','30%','40%','50%','60%','70%','80%','90%','100%']

#Create an empty dataframe with relevant columns
df_goalsScoredSplit_comparison = pd.DataFrame(columns = ['Goals Scored','Rule System','Outside Shot Proportion'])

#Loop through the standard scoring dataframe
for pp in range(0,len(insideProportions)):
    #Create temporary matching dataframe to append to main one
    df_append = pd.DataFrame(columns = ['Goals Scored','Rule System','Outside Shot Proportion'])
    #Add the goals scored values
    df_append['Goals Scored'] = df_goalsScoredSplit[insideProportionsStr[pp]]
    #Set the labelling variables
    df_append['Rule System'] = 'Standard'
    df_append['Outside Shot Proportion'] = outsideProportion[pp]
    #Append to main dataframe
    df_goalsScoredSplit_comparison = df_goalsScoredSplit_comparison.append(df_append,ignore_index=True)

#Loop through the new scoring dataframe
for pp in range(0,len(insideProportions)):
    #Create temporary matching dataframe to append to main one
    df_append = pd.DataFrame(columns = ['Goals Scored','Rule System','Outside Shot Proportion'])
    #Add the goals scored values
    df_append['Goals Scored'] = df_goalsScoredSplit_2pt[insideProportionsStr[pp]]
    #Set the labelling variables
    df_append['Rule System'] = 'Two-Point'
    df_append['Outside Shot Proportion'] = outsideProportion[pp]
    #Append to main dataframe
    df_goalsScoredSplit_comparison = df_goalsScoredSplit_comparison.append(df_append,ignore_index=True)

#Create bar plot
fig, ax = plt.subplots(figsize=(6,5))
gx = sns.barplot(x = 'Outside Shot Proportion',
                 y = 'Goals Scored',
                 hue = 'Rule System',   
                 ci = 'sd',
                 errcolor= '0.0',
                 errwidth = 2.0,
                 capsize = 0.0,
                 zorder = 5,
                 palette = ['black','darkgray'],
                 data = df_goalsScoredSplit_comparison)

#Set x and y labels
gx.set(xlabel = 'Proportion of Shots in Outer Circle',
       ylabel = 'Points Scored')

#Set y ticks to go from 0-9
ax.set(ylim = (0.0,7.0))
ax.yaxis.set_ticks(np.arange(0, 8, step = 1))

#Outline bars with black
for patch in ax.patches:
    patch.set_edgecolor('k')

#Set legend details
#Remove legend title
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles[0:], labels=labels[0:])
# plt.setp(ax.get_legend().get_title(), fontweight ='bold')
plt.setp(ax.get_legend().get_texts(), fontweight = 'bold')

# NOTE: this approach slightly differs to the simulation approach below, in that
# it allocates an overall success rate to the scoring (i.e. you get 50% of the
# score if that's what the overall sucess rate is). This contrasts to below in
# that each individual shot is given an X% chance of going in, and played against
# the random probability generator. Due to this, there is basically no chance of
# the first approach resulting in a score of zero - whereas this can quite readily
# happen with lower success rates as can be seen in the simulations below.

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

# We conduct various visualisations here. Firstly, compare each relevant match
# up between teams to see how these individual comparisons shake out. A better
# comparison here though is looking at each teams match-up against everyone else
# in total -- which gives an idea of overall strategy for each team.

##### TODO: add over to fig helper function

#Compare over each iteration of 'match-ups'
for tt in range(0,len(teamList)):
    for cc in range(0,len(teamList)):
        
        #Set a condition to only plot if team names don't match
        if teamList[tt] != teamList[cc]:
            
            #Get each teams colour
            teamCol1 = colourDict[teamList[tt]]
            teamCol2 = colourDict[teamList[cc]]
            
            #Set an array to store win % in
            winProps = np.zeros([len(compProps),len(compProps)])
            lossProps = np.zeros([len(compProps),len(compProps)])
            
            #Set an array to store mean/SD win and loss margins
            winMarginM = np.zeros([len(compProps),len(compProps)])
            winMarginSD = np.zeros([len(compProps),len(compProps)])
            lossMarginM = np.zeros([len(compProps),len(compProps)])
            lossMarginSD = np.zeros([len(compProps),len(compProps)])
            
            #Set the subplot figure to plot on
            fig, ax = plt.subplots(figsize=(11, 11), nrows = 5, ncols = 5)
            
            #Loop through the simulated proportions for each team
            for p1 in range(0,len(compProps)):
                for p2 in range(0,len(compProps)):
                    
                    #Extract current match up
                    #This needs a condition in place to grab the appropriate 
                    #proportions for the relevant teams based on position in 
                    #the team list
                    if tt < cc:
                        df_currComp = df_compSimResults.loc[(df_compSimResults['teamName'] == teamList[tt]) &
                                                            (df_compSimResults['opponentName'] == teamList[cc]) &
                                                            (df_compSimResults['teamSuperProp'] == compProps[p2]) &
                                                            (df_compSimResults['opponentSuperProp'] == compProps[p1]),]
                    elif cc < tt:
                        df_currComp = df_compSimResults.loc[(df_compSimResults['teamName'] == teamList[cc]) &
                                                            (df_compSimResults['opponentName'] == teamList[tt]) &
                                                            (df_compSimResults['teamSuperProp'] == compProps[p1]) &
                                                            (df_compSimResults['opponentSuperProp'] == compProps[p2]),]
                        #Similarly, if the team order is flipped, the margins
                        #for these comparisons need to be inverted to plot
                        #properly
                        df_currComp['margin'] = df_currComp['margin'] * -1
                        
                    #Calculate number of bins necessary to allocate one margin point to each bin
                    #Put condition in place to have 2 point margin bins for when
                    #both teams are at 100%, as odd margins aren't possible
                    if p1 == len(compProps)-1 & p2 == len(compProps)-1:
                        nBins = (np.max(df_currComp['margin']) - np.min(df_currComp['margin']) + 2) / 2
                    else:
                        nBins = np.max(df_currComp['margin']) - np.min(df_currComp['margin']) + 1
                    
                    #Calculate proportion of wins & losses for current 'team'
                    winProps[p1,p2] = sum(n > 0 for n in list(df_currComp['margin'])) / len(df_currComp['margin'])
                    lossProps[p1,p2] = sum(n < 0 for n in list(df_currComp['margin'])) / len(df_currComp['margin'])
                    
                    #Calculate mean and SD win and loss margins
                    winMarginM[p1,p2] = df_currComp.loc[(df_currComp['margin'] > 0),['margin']].mean()[0]
                    winMarginSD[p1,p2] = df_currComp.loc[(df_currComp['margin'] > 0),['margin']].std()[0]
                    lossMarginM[p1,p2] = df_currComp.loc[(df_currComp['margin'] < 0),['margin']].mean()[0]
                    lossMarginSD[p1,p2] = df_currComp.loc[(df_currComp['margin'] < 0),['margin']].std()[0]
                    
                    #Plot the current histogram
                    #Note that this distplot function works with seaborn 0.10, but
                    #has been slated for removal in later versions
                    hx = sns.distplot(df_currComp['margin'], kde = False,
                                      bins = int(nBins), color = 'grey',
                                      ax = ax[p1,p2],
                                      hist_kws = {'alpha': 0.75,
                                                  'linewidth': 1.0})
                            
                    #Set colours of each bars depending on bin value
                    #Get the unique values of bins in a sorted list
                    sortedBinVals = np.linspace(np.min(df_currComp['margin']),
                                                np.max(df_currComp['margin']),
                                                int(nBins))
                    for pp in range(0,len(sortedBinVals)):
                        #Check bin value and plot colour accordingly
                        if sortedBinVals[pp] < 0:
                            hx.patches[pp].set_facecolor(teamCol2)
                            hx.patches[pp].set_edgecolor(teamCol2)
                        elif sortedBinVals[pp] > 0:
                            hx.patches[pp].set_facecolor(teamCol1)
                            hx.patches[pp].set_edgecolor(teamCol1)
                        # elif sortedBinVals[pp] == 0:
                        #     hx.patches[pp].set_edgecolor('k')
                        #Add vertical line if zero
                        elif sortedBinVals[pp] == 0:
                            ax[p1,p2].axvline(0,color = 'k',
                                              linestyle = '--', linewidth = 0.5)
                    
                    #Set title
                    #This requires some manipulation and trickery to have a multi
                    #coloured title in the right place.
                    #First, we place a dummy title in the spot that we want
                    #This full title can only be one text colour, so we will 
                    #have to replace it
                    txt = ax[p1,p2].text(0.5, 1.075,
                                         teamList[cc]+' '+str(math.trunc(compProps[p1]*100))+'% / '+
                                         teamList[tt]+' '+str(math.trunc(compProps[p2]*100))+'%',
                                         ha = 'center', fontsize = 9,
                                         transform = ax[p1,p2].transAxes)
                    #We get the bounding box associated with this text
                    bb = txt.get_window_extent(renderer = fig.canvas.get_renderer())
                    #We then transform the bounding box to the axes coordinates
                    transf = ax[p1,p2].transAxes.inverted()
                    bbAx = bb.transformed(transf)
                    #Next, grab the width of the bounding box
                    titleWidth = bbAx.width
                    #With this info we can now remove the original text
                    txt.remove()
                    #With the title width, we can place the team names appropriately
                    #and do this separately to get different colours
                    #Set opponent as left figure title and colour
                    txt1 = ax[p1,p2].text(0.5 - titleWidth/2, 1.075,
                                          teamList[cc]+' '+str(math.trunc(compProps[p1]*100))+'%',
                                          ha = 'left', fontsize = 9,
                                          color = teamCol2,
                                          transform = ax[p1,p2].transAxes)
                    #Set team as right figure title and colour
                    txt2 = ax[p1,p2].text(0.5 + titleWidth/2, 1.075,
                                          teamList[tt]+' '+str(math.trunc(compProps[p2]*100))+'%',
                                          ha = 'right', fontsize = 9,
                                          color = teamCol1,
                                          transform = ax[p1,p2].transAxes)
                    #Now we just need to place the black slash in the middle
                    #We do this with a similar process to above, but now just
                    #grab the edges of the boxes associated with the team names
                    bb1 = txt1.get_window_extent(renderer = fig.canvas.get_renderer())
                    bbAx1 = bb1.transformed(transf)
                    txt1width = bbAx1.width
                    bb2 = txt2.get_window_extent(renderer = fig.canvas.get_renderer())
                    bbAx2 = bb2.transformed(transf)
                    txt2width = bbAx2.width
                    #Figure out the midpoint between the two text boxes
                    midPt = (((0.5 - titleWidth/2) + txt1width) + ((0.5 + titleWidth/2) - txt2width)) / 2
                    #Add the slash text centred around midpoint
                    ax[p1,p2].text(midPt, 1.075, ' / ', ha = 'center', fontsize = 9,
                                   color = 'k', transform = ax[p1,p2].transAxes)
                                        
            #Identify max y height of bars and set all y-axes to this limit
            maxY = 0 #blank starting value
            for aa in range(0,len(fig.get_axes())):
                #Loop through patches of current axes and get heights, replace if 
                #greater than current limit
                for hh in range(0,len(fig.get_axes()[aa].patches)):
                    #Get current axes y limit and append if greater than current max
                    if fig.get_axes()[aa].patches[hh].get_height() > maxY:
                        maxY = fig.get_axes()[aa].patches[hh].get_height()
                    
            #Reset to nearest 25 ceiling
            maxY = 25 * math.ceil(maxY/25)
            for aa in range(0,len(fig.get_axes())):
                fig.get_axes()[aa].set_ylim([0,maxY])
                
            #Set min and max X starting values to the min and max margins
            minX = np.min(df_currComp['margin'])
            maxX = np.max(df_currComp['margin'])
                    
            #Reset to nearest 5 floor/ceiling
            minX = 5 * math.floor(minX/5)
            maxX = 5 * math.ceil(maxX/5)
            #Set the x-ticks
            for aa in range(0,len(fig.get_axes())):
                fig.get_axes()[aa].set_xlim([minX,maxX])
            
            #Set y-axes ticks to 25 intervals.
            #Set tick and axes labels only on first column
            for ncol in range(0,ax.shape[1]):
                for nrow in range(0,ax.shape[0]):
                    #Set ticks
                    ax[nrow,ncol].set_yticks(np.linspace(0,maxY,int(maxY/25+1)))
                    #Set labels and fontsize
                    axLabels = list(np.linspace(0,maxY,int(maxY/25+1)))
                    axLabels = [math.trunc(value) for value in axLabels]
                    ax[nrow,ncol].set_yticklabels(axLabels, fontsize = 8)
                    #Set y-label if on first column
                    if ncol == 0:
                        ax[nrow,ncol].set_ylabel('Count', fontsize = 9)
                    else:
                        #Remove label
                        ax[nrow,ncol].set_ylabel('')
                        
            #Set x-axes ticks to 5 intervals.
            #Set tick and axes labels only on bottom row
            for ncol in range(0,ax.shape[1]):
                for nrow in range(0,ax.shape[0]):
                    #Set ticks
                    ax[nrow,ncol].set_xticks(np.linspace(minX,maxX,int(((maxX-minX)/5)+1)))
                    #Set labels and fontsize
                    axLabels = list(np.linspace(minX,maxX,int(((maxX-minX)/5)+1)))
                    axLabels = [math.trunc(value) for value in axLabels]
                    ax[nrow,ncol].set_xticklabels(axLabels, fontsize = 8)
                    #Set y-label if on first column
                    if nrow == ax.shape[0]-1:
                        ax[nrow,ncol].set_xlabel('Margin', fontsize = 9)
                    else:
                        #Remove label
                        ax[nrow,ncol].set_xlabel('')
                        
            #Set tight figure layout
            plt.tight_layout()
            
            #Add win proportion text annotations to each axes
            for nrow in range(0,ax.shape[0]):
                for ncol in range(0,ax.shape[1]):
                    #Set loss proportion (i.e. opposition wins)
                    ax[nrow,ncol].text(0.05, 0.825,
                                       str(round(lossProps[nrow,ncol]*100,1))+'%\n'+
                                       str(round(lossMarginM[nrow,ncol],1))+' '+u'\u00B1'+' '+str(round(lossMarginSD[nrow,ncol],1)),
                                       ha = 'left', fontsize = 8,
                                       color = teamCol2,
                                       transform = ax[nrow,ncol].transAxes)
                    #Set win proportion (i.e. team wins)
                    ax[nrow,ncol].text(0.95, 0.825,
                                       str(round(winProps[nrow,ncol]*100,1))+'%\n'+
                                       str(round(winMarginM[nrow,ncol],1))+' '+u'\u00B1'+' '+str(round(winMarginSD[nrow,ncol],1)),
                                       ha = 'right', fontsize = 8,
                                       color = teamCol1,
                                       transform = ax[nrow,ncol].transAxes)
            
            ##### TODO: save figures 
            
            #Close figure
            plt.close()
                    
###############            

#Compare each teams match-ups against all other teams
for tt in range(0,len(teamList)):
    
    #Get the current teams colour
    teamCol = colourDict[teamList[tt]]
    
    #Set an array to store win % in
    winProps = np.zeros([len(compProps),len(compProps)])
    lossProps = np.zeros([len(compProps),len(compProps)])
    
    #Set an array to store mean/SD win and loss margins
    winMarginM = np.zeros([len(compProps),len(compProps)])
    winMarginSD = np.zeros([len(compProps),len(compProps)])
    lossMarginM = np.zeros([len(compProps),len(compProps)])
    lossMarginSD = np.zeros([len(compProps),len(compProps)])
    
    #Set the subplot figure to plot on
    fig, ax = plt.subplots(figsize=(11, 11), nrows = 5, ncols = 5)
    
    #Loop through the simulated proportions for each team
    for p1 in range(0,len(compProps)):
        for p2 in range(0,len(compProps)):
            
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
                
            #Calculate number of bins necessary to allocate one margin point to each bin
            #Put condition in place to have 2 point margin bins for when
            #both teams are at 100%, as odd margins aren't possible
            if p1 == len(compProps)-1 & p2 == len(compProps)-1:
                nBins = (np.max(df_currComp['margin']) - np.min(df_currComp['margin']) + 2) / 2
            else:
                nBins = np.max(df_currComp['margin']) - np.min(df_currComp['margin']) + 1
            
            #Calculate proportion of wins & losses for current 'team'
            winProps[p1,p2] = sum(n > 0 for n in list(df_currComp['margin'])) / len(df_currComp['margin'])
            lossProps[p1,p2] = sum(n < 0 for n in list(df_currComp['margin'])) / len(df_currComp['margin'])
            
            #Calculate mean and SD win and loss margins
            winMarginM[p1,p2] = df_currComp.loc[(df_currComp['margin'] > 0),['margin']].mean()[0]
            winMarginSD[p1,p2] = df_currComp.loc[(df_currComp['margin'] > 0),['margin']].std()[0]
            lossMarginM[p1,p2] = df_currComp.loc[(df_currComp['margin'] < 0),['margin']].mean()[0]
            lossMarginSD[p1,p2] = df_currComp.loc[(df_currComp['margin'] < 0),['margin']].std()[0]
            
            #Plot the current histogram
            #Note that this distplot function works with seaborn 0.10, but
            #has been slated for removal in later versions
            hx = sns.distplot(df_currComp['margin'], kde = False,
                              bins = int(nBins), color = 'grey',
                              ax = ax[p1,p2],
                              hist_kws = {'alpha': 0.75,
                                          'linewidth': 1.0})
            
            #Set colours of each bars depending on bin value
            #For this one, we'll fill the bars the team wins, and not the bars
            #the team loses (i.e. fill them white)
            #Get the unique values of bins in a sorted list
            sortedBinVals = np.linspace(np.min(df_currComp['margin']),
                                        np.max(df_currComp['margin']),
                                        int(nBins))
            for pp in range(0,len(sortedBinVals)):
                #Check bin value and plot colour accordingly
                if sortedBinVals[pp] < 0:
                    hx.patches[pp].set_facecolor('w')
                    hx.patches[pp].set_edgecolor(teamCol)
                elif sortedBinVals[pp] > 0:
                    hx.patches[pp].set_facecolor(teamCol)
                    hx.patches[pp].set_edgecolor(teamCol)
                # elif sortedBinVals[pp] == 0:
                #     hx.patches[pp].set_edgecolor('k')
                #Add vertical line if zero
                elif sortedBinVals[pp] == 0:
                    ax[p1,p2].axvline(0,color = 'k',
                                      linestyle = '--', linewidth = 0.5)
            
            #Set title
            #This requires some manipulation and trickery to have a multi
            #coloured title in the right place.
            #First, we place a dummy title in the spot that we want
            #This full title can only be one text colour, so we will 
            #have to replace it
            txt = ax[p1,p2].text(0.5, 1.075,
                                 'Others '+str(math.trunc(compProps[p1]*100))+'% / '+
                                 teamList[tt]+' '+str(math.trunc(compProps[p2]*100))+'%',
                                 ha = 'center', fontsize = 9,
                                 transform = ax[p1,p2].transAxes)
            #We get the bounding box associated with this text
            bb = txt.get_window_extent(renderer = fig.canvas.get_renderer())
            #We then transform the bounding box to the axes coordinates
            transf = ax[p1,p2].transAxes.inverted()
            bbAx = bb.transformed(transf)
            #Next, grab the width of the bounding box
            titleWidth = bbAx.width
            #With this info we can now remove the original text
            txt.remove()
            #With the title width, we can place the team names appropriately
            #and do this separately to get different colours
            #Set opponent as left figure title and colour
            txt1 = ax[p1,p2].text(0.5 - titleWidth/2, 1.075,
                                  'Others '+str(math.trunc(compProps[p1]*100))+'%',
                                  ha = 'left', fontsize = 9,
                                  color = 'k',
                                  transform = ax[p1,p2].transAxes)
            #Set team as right figure title and colour
            txt2 = ax[p1,p2].text(0.5 + titleWidth/2, 1.075,
                                  teamList[tt]+' '+str(math.trunc(compProps[p2]*100))+'%',
                                  ha = 'right', fontsize = 9,
                                  color = teamCol,
                                  transform = ax[p1,p2].transAxes)
            #Now we just need to place the black slash in the middle
            #We do this with a similar process to above, but now just
            #grab the edges of the boxes associated with the team names
            bb1 = txt1.get_window_extent(renderer = fig.canvas.get_renderer())
            bbAx1 = bb1.transformed(transf)
            txt1width = bbAx1.width
            bb2 = txt2.get_window_extent(renderer = fig.canvas.get_renderer())
            bbAx2 = bb2.transformed(transf)
            txt2width = bbAx2.width
            #Figure out the midpoint between the two text boxes
            midPt = (((0.5 - titleWidth/2) + txt1width) + ((0.5 + titleWidth/2) - txt2width)) / 2
            #Add the slash text centred around midpoint
            ax[p1,p2].text(midPt, 1.075, ' / ', ha = 'center', fontsize = 9,
                           color = 'k', transform = ax[p1,p2].transAxes)
            
    #Identify max y height of bars and set all y-axes to this limit
    maxY = 0 #blank starting value
    for aa in range(0,len(fig.get_axes())):
        #Loop through patches of current axes and get heights, replace if 
        #greater than current limit
        for hh in range(0,len(fig.get_axes()[aa].patches)):
            #Get current axes y limit and append if greater than current max
            if fig.get_axes()[aa].patches[hh].get_height() > maxY:
                maxY = fig.get_axes()[aa].patches[hh].get_height()
            
    #Reset to nearest 250 ceiling
    maxY = 250 * math.ceil(maxY/250)
    for aa in range(0,len(fig.get_axes())):
        fig.get_axes()[aa].set_ylim([0,maxY])
        
    #Set min and max X starting values to the min and max margins
    minX = np.min(df_currComp['margin'])
    maxX = np.max(df_currComp['margin'])
            
    #Reset to nearest 5 floor/ceiling
    minX = 5 * math.floor(minX/5)
    maxX = 5 * math.ceil(maxX/5)
    #Set the x-ticks
    for aa in range(0,len(fig.get_axes())):
        fig.get_axes()[aa].set_xlim([minX,maxX])
    
    #Set y-axes ticks to 250 intervals.
    #Set tick and axes labels only on first column
    for ncol in range(0,ax.shape[1]):
        for nrow in range(0,ax.shape[0]):
            #Set ticks
            ax[nrow,ncol].set_yticks(np.linspace(0,maxY,int(maxY/250+1)))
            #Set labels and fontsize
            axLabels = list(np.linspace(0,maxY,int(maxY/250+1)))
            axLabels = [math.trunc(value) for value in axLabels]
            ax[nrow,ncol].set_yticklabels(axLabels, fontsize = 8)
            #Set y-label if on first column
            if ncol == 0:
                ax[nrow,ncol].set_ylabel('Count', fontsize = 9)
            else:
                #Remove label
                ax[nrow,ncol].set_ylabel('')
                
    #Set x-axes ticks to 5 intervals.
    #Set tick and axes labels only on bottom row
    for ncol in range(0,ax.shape[1]):
        for nrow in range(0,ax.shape[0]):
            #Set ticks
            ax[nrow,ncol].set_xticks(np.linspace(minX,maxX,int(((maxX-minX)/5)+1)))
            #Set labels and fontsize
            axLabels = list(np.linspace(minX,maxX,int(((maxX-minX)/5)+1)))
            axLabels = [math.trunc(value) for value in axLabels]
            ax[nrow,ncol].set_xticklabels(axLabels, fontsize = 8)
            #Set y-label if on first column
            if nrow == ax.shape[0]-1:
                ax[nrow,ncol].set_xlabel('Margin', fontsize = 9)
            else:
                #Remove label
                ax[nrow,ncol].set_xlabel('')
                
    #Set tight figure layout
    plt.tight_layout()
    
    #Add win proportion text annotations to each axes
    for nrow in range(0,ax.shape[0]):
        for ncol in range(0,ax.shape[1]):
            #Set loss proportion (i.e. opposition wins)
            ax[nrow,ncol].text(0.05, 0.825,
                               str(round(lossProps[nrow,ncol]*100,1))+'%\n'+
                               str(round(lossMarginM[nrow,ncol],1))+' '+u'\u00B1'+' '+str(round(lossMarginSD[nrow,ncol],1)),
                               ha = 'left', fontsize = 8,
                               color = 'k',
                               transform = ax[nrow,ncol].transAxes)
            #Set win proportion (i.e. team wins)
            ax[nrow,ncol].text(0.95, 0.825,
                               str(round(winProps[nrow,ncol]*100,1))+'%\n'+
                               str(round(winMarginM[nrow,ncol],1))+' '+u'\u00B1'+' '+str(round(winMarginSD[nrow,ncol],1)),
                               ha = 'right', fontsize = 8,
                               color = teamCol,
                               transform = ax[nrow,ncol].transAxes)
    
    ##### TODO: save figures 
    
    #Close figure
    plt.close()
    
#################

#Compare the various proportions for every team

#Set the two colours for win (green) vs. loss (red)
winCol = '#008708'
lossCol = '#c10000'

#Set an array to store win % in
winProps = np.zeros([len(compProps),len(compProps)])
lossProps = np.zeros([len(compProps),len(compProps)])

#Set an array to store mean/SD win and loss margins
winMarginM = np.zeros([len(compProps),len(compProps)])
winMarginSD = np.zeros([len(compProps),len(compProps)])
lossMarginM = np.zeros([len(compProps),len(compProps)])
lossMarginSD = np.zeros([len(compProps),len(compProps)])

#Set the subplot figure to plot on
fig, ax = plt.subplots(figsize=(11, 11), nrows = 5, ncols = 5)

#Loop through the simulated proportions for each team
for p1 in range(0,len(compProps)):
    for p2 in range(0,len(compProps)):
        
        #Extract all teams data and the relevant proportions
        #Note this is done separately to account for the fact that sometimes
        #the current team might be the 'team' or the 'opponent'
        df_currComp1 = df_compSimResults.loc[(df_compSimResults['teamSuperProp'] == compProps[p2])&
                                             (df_compSimResults['opponentSuperProp'] == compProps[p1]),]
        df_currComp2 = df_compSimResults.loc[(df_compSimResults['opponentSuperProp'] == compProps[p2]) &
                                             (df_compSimResults['teamSuperProp'] == compProps[p1]),]
        #For the second dataframe, the margin needs to be flipped to be
        #relative to the current team of interest
        df_currComp2['margin'] = df_currComp2['margin'] * -1
        
        #Now the two dataframes can be concatenated together
        df_currComp = pd.concat([df_currComp1,df_currComp2])
            
        #Calculate number of bins necessary to allocate one margin point to each bin
        #Put condition in place to have 2 point margin bins for when
        #both teams are at 100%, as odd margins aren't possible
        if p1 == len(compProps)-1 & p2 == len(compProps)-1:
            nBins = (np.max(df_currComp['margin']) - np.min(df_currComp['margin']) + 2) / 2
        else:
            nBins = np.max(df_currComp['margin']) - np.min(df_currComp['margin']) + 1
        
        #Calculate proportion of wins & losses for current 'team'
        winProps[p1,p2] = sum(n > 0 for n in list(df_currComp['margin'])) / len(df_currComp['margin'])
        lossProps[p1,p2] = sum(n < 0 for n in list(df_currComp['margin'])) / len(df_currComp['margin'])
        
        #Calculate mean and SD win and loss margins
        winMarginM[p1,p2] = df_currComp.loc[(df_currComp['margin'] > 0),['margin']].mean()[0]
        winMarginSD[p1,p2] = df_currComp.loc[(df_currComp['margin'] > 0),['margin']].std()[0]
        lossMarginM[p1,p2] = df_currComp.loc[(df_currComp['margin'] < 0),['margin']].mean()[0]
        lossMarginSD[p1,p2] = df_currComp.loc[(df_currComp['margin'] < 0),['margin']].std()[0]
        
        #Plot the current histogram
        #Note that this distplot function works with seaborn 0.10, but
        #has been slated for removal in later versions
        hx = sns.distplot(df_currComp['margin'], kde = False,
                          bins = int(nBins), color = 'grey',
                          ax = ax[p1,p2],
                          hist_kws = {'alpha': 0.75,
                                      'linewidth': 1.0})
        
        #Set colours of each bars depending on bin value
        #For this one, we'll fill the bars the team wins, and not the bars
        #the team loses (i.e. fill them white)
        #Get the unique values of bins in a sorted list
        sortedBinVals = np.linspace(np.min(df_currComp['margin']),
                                    np.max(df_currComp['margin']),
                                    int(nBins))
        for pp in range(0,len(sortedBinVals)):
            #Check bin value and plot colour accordingly
            if sortedBinVals[pp] < 0:
                hx.patches[pp].set_facecolor(lossCol)
                hx.patches[pp].set_edgecolor(lossCol)
            elif sortedBinVals[pp] > 0:
                hx.patches[pp].set_facecolor(winCol)
                hx.patches[pp].set_edgecolor(winCol)
            # elif sortedBinVals[pp] == 0:
            #     hx.patches[pp].set_edgecolor('k')
            #Add vertical line if zero
            elif sortedBinVals[pp] == 0:
                ax[p1,p2].axvline(0,color = 'k',
                                  linestyle = '--', linewidth = 0.5)
        
        #Set title
        txt = ax[p1,p2].text(0.5, 1.075,
                             'Opponent '+str(math.trunc(compProps[p1]*100))+'% / '+
                             'Team '+str(math.trunc(compProps[p2]*100))+'%',
                             ha = 'center', fontsize = 9,
                             transform = ax[p1,p2].transAxes)
        
#Identify max y height of bars and set all y-axes to this limit
maxY = 0 #blank starting value
for aa in range(0,len(fig.get_axes())):
    #Loop through patches of current axes and get heights, replace if 
    #greater than current limit
    for hh in range(0,len(fig.get_axes()[aa].patches)):
        #Get current axes y limit and append if greater than current max
        if fig.get_axes()[aa].patches[hh].get_height() > maxY:
            maxY = fig.get_axes()[aa].patches[hh].get_height()
        
#Reset to nearest 250 ceiling
maxY = 1000 * math.ceil(maxY/1000)
for aa in range(0,len(fig.get_axes())):
    fig.get_axes()[aa].set_ylim([0,maxY])
    
#Set min and max X starting values to the min and max margins
minX = np.min(df_currComp['margin'])
maxX = np.max(df_currComp['margin'])
        
#Reset to nearest 5 floor/ceiling
minX = 5 * math.floor(minX/5)
maxX = 5 * math.ceil(maxX/5)
#Set the x-ticks
for aa in range(0,len(fig.get_axes())):
    fig.get_axes()[aa].set_xlim([minX,maxX])

#Set y-axes ticks to 2500 intervals.
#Set tick and axes labels only on first column
for ncol in range(0,ax.shape[1]):
    for nrow in range(0,ax.shape[0]):
        #Set ticks
        ax[nrow,ncol].set_yticks(np.linspace(0,maxY,int(maxY/2500+1)))
        #Set labels and fontsize
        axLabels = list(np.linspace(0,maxY,int(maxY/2500+1)))
        axLabels = [math.trunc(value) for value in axLabels]
        ax[nrow,ncol].set_yticklabels(axLabels, fontsize = 8)
        #Set y-label if on first column
        if ncol == 0:
            ax[nrow,ncol].set_ylabel('Count', fontsize = 9)
        else:
            #Remove label
            ax[nrow,ncol].set_ylabel('')
            
#Set x-axes ticks to 5 intervals.
#Set tick and axes labels only on bottom row
for ncol in range(0,ax.shape[1]):
    for nrow in range(0,ax.shape[0]):
        #Set ticks
        ax[nrow,ncol].set_xticks(np.linspace(minX,maxX,int(((maxX-minX)/5)+1)))
        #Set labels and fontsize
        axLabels = list(np.linspace(minX,maxX,int(((maxX-minX)/5)+1)))
        axLabels = [math.trunc(value) for value in axLabels]
        ax[nrow,ncol].set_xticklabels(axLabels, fontsize = 8)
        #Set y-label if on first column
        if nrow == ax.shape[0]-1:
            ax[nrow,ncol].set_xlabel('Margin', fontsize = 9)
        else:
            #Remove label
            ax[nrow,ncol].set_xlabel('')
            
#Set tight figure layout
plt.tight_layout()

#Add win proportion text annotations to each axes
for nrow in range(0,ax.shape[0]):
    for ncol in range(0,ax.shape[1]):
        #Set loss proportion (i.e. opposition wins)
        ax[nrow,ncol].text(0.05, 0.825,
                           str(round(lossProps[nrow,ncol]*100,1))+'%\n'+
                           str(round(lossMarginM[nrow,ncol],1))+' '+u'\u00B1'+' '+str(round(lossMarginSD[nrow,ncol],1)),
                           ha = 'left', fontsize = 8,
                           color = lossCol,
                           transform = ax[nrow,ncol].transAxes)
        #Set win proportion (i.e. team wins)
        ax[nrow,ncol].text(0.95, 0.825,
                           str(round(winProps[nrow,ncol]*100,1))+'%\n'+
                           str(round(winMarginM[nrow,ncol],1))+' '+u'\u00B1'+' '+str(round(winMarginSD[nrow,ncol],1)),
                           ha = 'right', fontsize = 8,
                           color = winCol,
                           transform = ax[nrow,ncol].transAxes)

##### TODO: save figures 

#Close figure
plt.close()

# %% Visualise 'competitive' sim margins

#This firstly requires the data to be manipulated into a dataframe with specific
#variables and columns to suit the seaborn package

#Create dictionary to append these data to
marginDict = {'teamName': [], 'teamSuperProp': [],
              'opponentName': [], 'opponentSuperProp': [],
              'margin': []}

#Loop through teams and extract their margin results and the proportions
for tt in range (len(teamList)):
    
    #Extract teams data
    #This is done separately given the need to modify margin
    df_currTeam1 = df_compSimResults.loc[(df_compSimResults['teamName'] == teamList[tt]),]
    df_currTeam2 = df_compSimResults.loc[(df_compSimResults['opponentName'] == teamList[tt]),]
    
    #Add data to dictionary
    #First dataframe - use normal margin and 'team' data
    marginDict['teamName'].extend(list(df_currTeam1['teamName'].values))
    marginDict['teamSuperProp'].extend(list(df_currTeam1['teamSuperProp'].values))
    marginDict['opponentName'].extend(list(df_currTeam1['opponentName'].values))
    marginDict['opponentSuperProp'].extend(list(df_currTeam1['opponentSuperProp'].values))
    marginDict['margin'].extend(list(df_currTeam1['margin'].values))
    #Second dataframe - invert margin and use 'opponent' data
    marginDict['teamName'].extend(list(df_currTeam2['opponentName'].values))
    marginDict['teamSuperProp'].extend(list(df_currTeam2['opponentSuperProp'].values))
    marginDict['opponentName'].extend(list(df_currTeam2['teamName'].values))
    marginDict['opponentSuperProp'].extend(list(df_currTeam2['teamSuperProp'].values))
    marginDict['margin'].extend(list(df_currTeam2['margin'].values*-1))
    
#Convert to dataframe
df_compSimMargins = pd.DataFrame.from_dict(marginDict)

#### Test plot

#Split to get example of 0% prop vs. 100% prop opponent
df_currPlot = df_compSimMargins.loc[(df_compSimMargins['teamSuperProp'] == 0.0) &
                                    (df_compSimMargins['opponentSuperProp'] == 1.0),]

sns.boxplot(x = 'teamName', y = 'margin',
            hue = 'teamName', palette = list(colourDict.values()),
            dodge = False, whis = [0,100],
            data = df_currPlot)

##### Edits:
    ##### Turn off legend, convert to white with coloured outlimne,
    ##### add dashed line at zero (underneath), box width for separating plots,
    ##### subplot for 0% vs. others, edit cap width
        
# %% TODO:
    
# Add some summary statistics (mean, range, IQR's etc.) printed out to table
# Essentially the box plot data in tabular form

# Summary figures/tables across individual teams as the data points to group data

        
# %%








