# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 21:13:39 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    TODO: add notes...
    
"""

# %% Import packages

#Python packages
import pandas as pd
pd.options.mode.chained_assignment = None #turn off pandas chained warnings
import numpy as np
import scipy.stats as stats
import json
import seaborn as sns
import matplotlib.pyplot as plt
import math
import itertools

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
colourDict = {'All Teams': '#000000',
              'Fever': '#00953b',
              'Firebirds': '#4b2c69',
              'GIANTS': '#f57921',
              'Lightning': '#fdb61c',
              'Magpies': '#494b4a',
              'Swifts': '#0082cd',
              'Thunderbirds': '#e54078',
              'Vixens': '#00a68e'}

#Set team list variable
teamList = ['Fever',
            'Firebirds',
            'GIANTS',
            'Lightning',
            'Magpies',
            'Swifts',
            'Thunderbirds',
            'Vixens']

# %% Set-up

#Read in datasets
scoreFlowData = pd.read_csv('..\\Data\\scoreFlowSuper.csv')
teamSuperCounts = pd.read_csv('..\\Data\\teamSuperCounts.csv')
oppSuperCounts = pd.read_csv('..\\Data\\oppSuperCounts.csv')

# %% Examine relative odds of outer vs. inner circle shooting

# #### TODO: probably don't want this in updated paper...

# #This effectively replicates the analysis from our original paper but with data
# #from 2020-2022 seasons.

# #Set a check in place whether to run this analysis or load data in from previous run
# runRelOdds = True ####change to false to load in existing data

# #Set number of trials to run
# nRelOddsTrials = 100000

# #Run analysis
# if runRelOdds:
    
#     #Set a dictionary to store data in
#     relOddsData = {'squadId': [], 'mean': [], 'lower95': [], 'upper95': []}
#     relOddsDefData = {'squadId': [], 'mean': [], 'lower95': [], 'upper95': []}
    
#     #Run through first iteration using all teams data
    
#     #Set seed
#     np.random.seed(12345)
    
#     #Group by shot type to create sums
#     shotSums = teamSuperCounts.groupby('scoreName').sum()
    
#     #Create the beta distributions for inner and outercircle
#     betaInner = stats.beta(shotSums['shotCount']['miss'], shotSums['shotCount']['goal'])
#     betaOuter = stats.beta(shotSums['shotCount']['2pt Miss'], shotSums['shotCount']['2pt Goal'])
    
#     #Sample values from beta distributions
#     valsInner = np.random.beta(shotSums['shotCount']['miss'], shotSums['shotCount']['goal'],
#                               size = nRelOddsTrials)
#     valsOuter = np.random.beta(shotSums['shotCount']['2pt Miss'], shotSums['shotCount']['2pt Goal'],
#                               size = nRelOddsTrials)
    
#     #Determine relative odds of missing from outer to inner circle
#     sampleRatios = valsOuter / valsInner
    
#     #Create values for empirical cumulative distribution function
#     cdfSplit_x = np.sort(sampleRatios)
#     cdfSplit_y = np.arange(1, nRelOddsTrials+1) / nRelOddsTrials
    
#     #Calculate confidence intervals of the cumulative distribution function
#     #Find where the CDF y-values equal 0.05/0.95, or the closest index to this,
#     #and grab that index of the x-values
#     lower95ind = np.where(cdfSplit_y == 0.05)[0][0]
#     upper95ind = np.where(cdfSplit_y == 0.95)[0][0]
#     ci95_lower = cdfSplit_x[lower95ind]
#     ci95_upper = cdfSplit_x[upper95ind]
    
#     #Store values in dictionary
#     relOddsData['squadId'].append('all')
#     relOddsData['mean'].append(sampleRatios.mean())
#     relOddsData['lower95'].append(ci95_lower)
#     relOddsData['upper95'].append(ci95_upper)
    
#     #Repeat analysis looping through teams
#     for team in teamList:
        
#         #Run for shooting stats by team
        
#         #Set seed
#         np.random.seed(int(12345*teamList.index(team)))
        
#         #Group by shot type to create sums
#         shotSums = teamSuperCounts.groupby(['squadId','scoreName']).sum()
        
#         #Create the beta distributions for inner and outercircle
#         betaInner = stats.beta(shotSums['shotCount'][team]['miss'], shotSums['shotCount'][team]['goal'])
#         betaOuter = stats.beta(shotSums['shotCount'][team]['2pt Miss'], shotSums['shotCount'][team]['2pt Goal'])
        
#         #Sample values from beta distributions
#         valsInner = np.random.beta(shotSums['shotCount'][team]['miss'], shotSums['shotCount'][team]['goal'],
#                                    size = nRelOddsTrials)
#         valsOuter = np.random.beta(shotSums['shotCount'][team]['2pt Miss'], shotSums['shotCount'][team]['2pt Goal'],
#                                    size = nRelOddsTrials)

#         #Determine relative odds of missing from outer to inner circle
#         sampleRatios = valsOuter / valsInner
        
#         #Create values for empirical cumulative distribution function
#         cdfSplit_x = np.sort(sampleRatios)
#         cdfSplit_y = np.arange(1, nRelOddsTrials+1) / nRelOddsTrials
        
#         #Calculate confidence intervals of the cumulative distribution function
#         #Find where the CDF y-values equal 0.05/0.95, or the closest index to this,
#         #and grab that index of the x-values
#         lower95ind = np.where(cdfSplit_y == 0.05)[0][0]
#         upper95ind = np.where(cdfSplit_y == 0.95)[0][0]
#         ci95_lower = cdfSplit_x[lower95ind]
#         ci95_upper = cdfSplit_x[upper95ind]
        
#         #Store values in dictionary
#         relOddsData['squadId'].append(team)
#         relOddsData['mean'].append(sampleRatios.mean())
#         relOddsData['lower95'].append(ci95_lower)
#         relOddsData['upper95'].append(ci95_upper)
        
#         #Run for shooting stats against team
        
#         #Set seed
#         np.random.seed(int(12345*teamList.index(team)))
        
#         #Group by shot type to create sums
#         shotSums = oppSuperCounts.groupby(['oppSquadId','scoreName']).sum()
        
#         #Create the beta distributions for inner and outercircle
#         betaInner = stats.beta(shotSums['shotCount'][team]['miss'], shotSums['shotCount'][team]['goal'])
#         betaOuter = stats.beta(shotSums['shotCount'][team]['2pt Miss'], shotSums['shotCount'][team]['2pt Goal'])
        
#         #Sample values from beta distributions
#         valsInner = np.random.beta(shotSums['shotCount'][team]['miss'], shotSums['shotCount'][team]['goal'],
#                                    size = nRelOddsTrials)
#         valsOuter = np.random.beta(shotSums['shotCount'][team]['2pt Miss'], shotSums['shotCount'][team]['2pt Goal'],
#                                    size = nRelOddsTrials)

#         #Determine relative odds of missing from outer to inner circle
#         sampleRatios = valsOuter / valsInner
        
#         #Create values for empirical cumulative distribution function
#         cdfSplit_x = np.sort(sampleRatios)
#         cdfSplit_y = np.arange(1, nRelOddsTrials+1) / nRelOddsTrials
        
#         #Calculate confidence intervals of the cumulative distribution function
#         #Find where the CDF y-values equal 0.05/0.95, or the closest index to this,
#         #and grab that index of the x-values
#         lower95ind = np.where(cdfSplit_y == 0.05)[0][0]
#         upper95ind = np.where(cdfSplit_y == 0.95)[0][0]
#         ci95_lower = cdfSplit_x[lower95ind]
#         ci95_upper = cdfSplit_x[upper95ind]
        
#         #Store values in dictionary
#         relOddsDefData['squadId'].append(team)
#         relOddsDefData['mean'].append(sampleRatios.mean())
#         relOddsDefData['lower95'].append(ci95_lower)
#         relOddsDefData['upper95'].append(ci95_upper)
    
#     #Visualise results
    
#     #Create figure
#     fig, ax = plt.subplots(figsize=(9,4), nrows = 1, ncols = 2,
#                            sharex = False, sharey = True)
    
#     #Shooting statistics
    
#     #Set colour array to include black for all team data
#     plotCol = ['#000000']+[col for col in colourDict.values()]
    
#     #Create labels to include all team label
#     plotLabels = ['All Teams']+[team for team in colourDict.keys()]
    
#     #Plot data
#     for ii in range(len(relOddsData['squadId'])):
#         ax[0].errorbar(ii, relOddsData['mean'][ii],
#                        yerr = np.array(relOddsData['upper95'][ii]) - np.array(relOddsData['lower95'][ii]),
#                        marker = 'o', markersize = 6,
#                        ls = 'none', lw = 2,
#                        color = plotCol[ii], label = plotLabels[ii], zorder = 2)
        
#     #Add legend
#     ax[0].legend(ncol = 2)
        
#     #Plot line at 2:1 for reference
#     ax[0].axhline(y = 2, linestyle = '--', linewidth = 1,
#                   color = 'grey', zorder = 0)
    
#     #Set lower limit at zero
#     ax[0].set_ylim(0,ax[0].get_ylim()[1])
    
#     #Set no x-labels
#     ax[0].set_xticks([])
    
#     #Set y-label
#     ax[0].set_ylabel('Relative Odds of Missing from Outer vs. Inner Circle',
#                      fontsize = 8)
    
#     #Add caption lettering reference
#     ax[0].text(ax[0].get_xlim()[0], ax[0].get_ylim()[1] * 0.99,
#                ' A', ha = 'left', va = 'top',
#                fontsize = 16, fontweight = 'bold')
    
#     #Defensive statistics
    
#     #Plot data
#     for ii in range(len(relOddsDefData['squadId'])):
#         ax[1].errorbar(ii, relOddsDefData['mean'][ii],
#                        yerr = np.array(relOddsDefData['upper95'][ii]) - np.array(relOddsDefData['lower95'][ii]),
#                        marker = 'o', markersize = 6,
#                        ls = 'none', lw = 2,
#                        color = colourDict[relOddsDefData['squadId'][ii]],
#                        label = relOddsDefData['squadId'][ii], zorder = 2)
    
#     #Add legend
#     ax[1].legend(ncol = 2)
        
#     #Plot line at 2:1 for reference
#     ax[1].axhline(y = 2, linestyle = '--', linewidth = 1,
#                   color = 'grey', zorder = 0)
    
#     #Set no x-labels
#     ax[1].set_xticks([])
    
#     #Set y-label
#     ax[1].set_ylabel('Relative Odds of Opponent Missing from Outer vs. Inner Circle',
#                      fontsize = 8, labelpad = 10)
    
#     #Add caption lettering reference
#     ax[1].text(ax[1].get_xlim()[0], ax[1].get_ylim()[1] * 0.99,
#                ' B', ha = 'left', va = 'top',
#                fontsize = 16, fontweight = 'bold')
    
#     #Set tight layout
#     plt.tight_layout()
    

# #### NOTE: Relative risk of missing from inner is so low...hence relative is effected highly...

# %% Simulate scoring for teams in Super Shot period

#Here we run simulations replicating a 'typical' amount of shots each team receives
#during the Power 5 period. We apply 'tendencies' to how many of these are selected
#as Super Shots, and then simulate the outcome of each shot based on the distributions
#foor shot success from the different zones.

#Set a 'tendency' variable. This applies an odds for whether a team will take a
#shot as a Super Shot or not, with higher 'tendencies' relating to a higher chance
#they will lean towards a Super Shot. This is in place of explicitly prescribing
#the proportion of shots to be taken. Everything will be referenced against the 
#no super shot tendency as a means to explore expected goals gained.
shotTendency = [0, 0.25, 0.5, 0.75, 1.0]
shotTendencyLabels = ['Zero', 'Low', 'Moderate', 'High', 'All Out']

#Set number of simulations to run through
nSims = 1000

#Set a check in place for whether to run the sims or load in existing results
#Note that the results generated should be the same given the seeds being set
#throughout. If you wish to generate 'new' results then you can alter the seed
#values throughout
runStandardSims = False ##### change to True to re-run sims

#Run simulations
if runStandardSims:
    
    #Create a dictionary to store results in
    standardSimsData = {'squadId': [], 'simId': [], 'shotTendency': [],
                        'nShots': [], 'nStandard': [], 'nSuper': [],
                        'totalGoals': [], 'relativeGoals': []}
    
    #Loop through teams
    for team in teamList:
        
        #Calculate mean and SD for number of shots in Power 5 across season
        nPeriods = len(scoreFlowData.groupby(['squadId','matchId','period']).count()['shotOutcome'][team].to_numpy())
        meanShots = scoreFlowData.groupby(['squadId','matchId','period']).count()['shotOutcome'][team].to_numpy().mean()
        sdShots = scoreFlowData.groupby(['squadId','matchId','period']).count()['shotOutcome'][team].to_numpy().std()
        
        #Sample from truncated normal distribution with mean/SD parameters
        #This is truncated to the 95% CIs for expected shots in a Power 5 period
        lowLim = meanShots - (1.96 * (sdShots / math.sqrt(nPeriods)))
        uppLim = meanShots + (1.96 * (sdShots / math.sqrt(nPeriods)))
        #Set seed for consistent sampling
        np.random.seed(12345 + teamList.index(team))
        nSimShots = np.around(stats.truncnorm((lowLim - meanShots) / sdShots,
                                              (uppLim - meanShots) / sdShots,
                                              loc = meanShots,
                                              scale = sdShots).rvs(nSims))
        
        #Sum the shooting numbers for the current team
        shotSums = teamSuperCounts.groupby(['squadId','scoreName']).sum()
        
        #Loop through nSims
        for simId in range(nSims):
            
            #Simulate a set of probability values to match to tendency to determine
            #whether or not a super shot is taken or not
            np.random.seed(54321 * (simId+1) + teamList.index(team))
            tendencyProbs = np.random.rand(int(nSimShots[simId]))
            
            #Sample chance of success for the numnber of simulation shots from each
            #of the standard and super shot distributions
            #Standard shots
            np.random.seed(999 * (simId+1) - teamList.index(team))
            standardShotProbSuccess = np.random.beta(shotSums['shotCount'][team]['goal'],
                                                     shotSums['shotCount'][team]['miss'],
                                                     size = int(nSimShots[simId]))
            #Super shots
            np.random.seed(111 * (simId+1) - teamList.index(team))
            superShotProbSuccess = np.random.beta(shotSums['shotCount'][team]['2pt Goal'],
                                                  shotSums['shotCount'][team]['2pt Miss'],
                                                  size = int(nSimShots[simId]))
            
            #Sample the random values that will dictate shot success by being 
            #lower (i.e. successful) or higher (i.e. unsuccessful) versus the 
            #shot probabilities
            np.random.seed(10101 * (simId+1) - teamList.index(team))
            shotSuccessComparator = np.random.rand(int(nSimShots[simId]))
            
            #Loop through tendency approaches
            for tendency in shotTendency:
                
                #Create a logic array for whether the shot is a Super or not based
                #on tendency probabilities for the current shot set
                takeSuperShot = tendency > tendencyProbs
                takeSuperShotMultiplier = [2 if takeSuperShot[ii] else 1 for ii in range(int(nSimShots[simId]))]
                
                #Get the probabilities of shot success based on the shot type
                allShotProbSuccess = np.array([superShotProbSuccess[ii] if takeSuperShot[ii] else standardShotProbSuccess[ii] for ii in range(int(nSimShots[simId]))])
                
                #Determine success of shots
                logicShotSuccess = allShotProbSuccess > shotSuccessComparator
                
                #Calculate total goals scored based on shot success and type
                totalGoals = np.sum(logicShotSuccess * takeSuperShotMultiplier)
                
                #Store the relative value if tendency is 'zero'
                if tendency == 0:
                    goalNormaliser = totalGoals
                
                #Append data to dictionary
                standardSimsData['squadId'].append(team)
                standardSimsData['simId'].append(int(simId))
                standardSimsData['shotTendency'].append(shotTendencyLabels[shotTendency.index(tendency)])
                standardSimsData['nShots'].append(int(nSimShots[simId]))
                standardSimsData['nStandard'].append(int(np.sum(~np.array(takeSuperShot))))
                standardSimsData['nSuper'].append(int(np.sum(np.array(takeSuperShot))))
                standardSimsData['totalGoals'].append(int(totalGoals))
                standardSimsData['relativeGoals'].append(totalGoals / goalNormaliser)
                
    #Save standard sim data to json
    with open('..\\Results\\standardSims\\standardSimsData.json', 'w') as jsonFile:
        json.dump(standardSimsData, jsonFile)
        
else:
    
    #Read in existing simulation data
    with open('..\\Results\\standardSims\\standardSimsData.json', 'r') as jsonFile:
        standardSimsData = json.load(jsonFile)
        
#Convert to datafram
standardSimsData_df = pd.DataFrame.from_dict(standardSimsData)
        
#Export some summary data related to the standard sims
#Summarise all team data
standardSimsRelativeGoalSummary = standardSimsData_df.groupby('shotTendency').describe()['relativeGoals'][['mean','std']].reset_index()
standardSimsRelativeGoalSummary['squadId'] = ['All Teams'] * len(standardSimsRelativeGoalSummary)
#Concatenate on the grouped team data
standardSimsRelativeGoalSummary = pd.concat([standardSimsRelativeGoalSummary,
                                             standardSimsData_df.groupby(['squadId',
                                                                          'shotTendency']).describe()['relativeGoals'][['mean','std']].reset_index()])
#Export to csv
standardSimsRelativeGoalSummary.to_csv('..\\Results\\standardSims\\standardSims_relativeGoals_meanSD.csv',
                                       index = False)

# %% Visualise standard sims data

#Set-up figure
fig, ax = plt.subplots(nrows = 3, ncols = 3, figsize = (8,10),
                       sharex = True, sharey = True)

#Adjust spacing
plt.subplots_adjust(left = 0.075, right = 0.95,
                    bottom = 0.1, top = 0.95,
                    wspace = 0.1, hspace = 0.1)

#Plot data from all teams and the squad Id's separately
for squadName in list(colourDict.keys()):
    
    #Set axis id
    axisId = list(colourDict.keys()).index(squadName)
    
    #Check if all teams
    if squadName == 'All Teams':
        
        #Plot violin
        sns.violinplot(data = standardSimsData_df,
                       x = 'shotTendency', y = 'relativeGoals',
                       order = shotTendencyLabels[1:],
                       color = colourDict[squadName],
                       cut = 0, inner = None, width = 0.9,
                       ax = ax.flatten()[axisId], zorder = 1)
        
        #Update violin alpha and line width
        plt.setp(ax.flatten()[axisId].collections, alpha = 0.3)
        plt.setp(ax.flatten()[axisId].collections, linewidth = 0)
            
        #Plot mean point
        sns.pointplot(data = standardSimsData_df,
                      x = 'shotTendency', y = 'relativeGoals',
                      ci = 'sd', join = False,
                      order = shotTendencyLabels[1:],
                      markers = 'o', markersize = 4,
                      color = colourDict[squadName],
                      ax = ax.flatten()[axisId], zorder = 3)
        
        #Plot range
        for tendency in shotTendencyLabels[1:]:
            #Get range values
            minVal = standardSimsData_df.loc[standardSimsData_df['shotTendency'] == tendency,]['relativeGoals'].to_numpy().min()
            maxVal = standardSimsData_df.loc[standardSimsData_df['shotTendency'] == tendency,]['relativeGoals'].to_numpy().max()
            #Plot range
            ax.flatten()[axisId].vlines(shotTendencyLabels[1:].index(tendency), minVal, maxVal,
                                        color = colourDict[squadName], lw = 1, ls ='--')
            
        
    else:
        
        #Split by team
        sns.violinplot(data = standardSimsData_df.loc[standardSimsData_df['squadId'] == squadName],
                       x = 'shotTendency', y = 'relativeGoals',
                       order = shotTendencyLabels[1:],
                       color = colourDict[squadName],
                       cut = 0, inner = None, width = 0.9,
                       ax = ax.flatten()[axisId], zorder = 1)
        
        #Update violin alpha and line width
        plt.setp(ax.flatten()[axisId].collections, alpha = 0.3)
        plt.setp(ax.flatten()[axisId].collections, linewidth = 0)
        
        #Plot pointplot
        sns.pointplot(data = standardSimsData_df.loc[standardSimsData_df['squadId'] == squadName],
                      x = 'shotTendency', y = 'relativeGoals',
                      ci = 'sd', join = False,
                      order = shotTendencyLabels[1:],
                      markers = 'o', markersize = 4,
                      color = colourDict[squadName],
                      ax = ax.flatten()[axisId], zorder = 3)
        
        #Plot range
        for tendency in shotTendencyLabels[1:]:
            #Get range values
            minVal = standardSimsData_df.loc[(standardSimsData_df['squadId'] == squadName) &
                                             (standardSimsData_df['shotTendency'] == tendency),]['relativeGoals'].to_numpy().min()
            maxVal = standardSimsData_df.loc[(standardSimsData_df['squadId'] == squadName) &
                                             (standardSimsData_df['shotTendency'] == tendency),]['relativeGoals'].to_numpy().max()
            #Plot range
            ax.flatten()[axisId].vlines(shotTendencyLabels[1:].index(tendency), minVal, maxVal,
                                        color = colourDict[squadName], lw = 1, ls ='--')
            
    #Add relative line at y = 1
    ax.flatten()[axisId].axhline(y = 1, ls = '--', lw = 0.5,
                                 color = 'k', zorder = 0)
    
    #Set title
    ax.flatten()[axisId].set_title(squadName, fontsize = 12, fontweight = 'bold')
    
    #Turn off x-label
    ax.flatten()[axisId].set_xlabel('')
    
    #Apply y-label appropriately
    if (axisId % 3) == 0:
        ax.flatten()[axisId].set_ylabel('Relative Goals Scored',
                                        fontsize = 12, fontweight = 'bold')
    else:
        ax.flatten()[axisId].set_ylabel('')
        
#Tight layout
plt.tight_layout()

#Save figure
plt.savefig('..\\Results\\standardSims\\relativeGoalsScored.png',
            format = 'png', facecolor = fig.get_facecolor(),
            dpi = 300)
plt.savefig('..\\Results\\standardSims\\relativeGoalsScored.jpeg',
            format = 'jpeg', facecolor = fig.get_facecolor(),
            dpi = 600)


#Close figure
plt.close()

#Display all team results
print('Relative goals scored at each tendency level across all teams [+/- 95% CIs]:')
for tendencyLabel in shotTendencyLabels[1:]:
    #Calculate lower and upper CI's
    vals = standardSimsData_df.loc[standardSimsData_df['shotTendency'] == tendencyLabel,
                                   ]['relativeGoals'].to_numpy()
    ciLow = vals.mean() - (1.96 * (vals.std() / math.sqrt(nSims)))
    ciHigh = vals.mean() + (1.96 * (vals.std() / math.sqrt(nSims)))
    #Display
    print(f'{tendencyLabel}: {np.round(vals.mean(),2)} [{np.round(ciLow,2)}, {np.round(ciHigh,2)}]')

# %% Simulate competitive Power 5 periods between teams

#Here we run simulations replicating a 'typical' Power 5 period between teams. 
#This is reflected in each team receiving a relevant share of the typical total
#amount of shots in the Power 5 period. We then look at the various combinations
#of Super Shot tendencies teams can apply to their share of these shots. The share
#of shots is balanced among the two teams in that the +/- difference between teams
#for shots is even across the total simulations. Tendencies for taking Super Shots
#are applied in the same way as earlier.

#Set a 'tendency' variable. This applies an odds for whether a team will take a
#shot as a Super Shot or not, with higher 'tendencies' relating to a higher chance
#they will lean towards a Super Shot. This is in place of explicitly prescribing
#the proportion of shots to be taken. Everything will be referenced against the 
#no super shot tendency as a means to explore expected goals gained.
shotTendency = [0, 0.25, 0.5, 0.75, 1.0]
shotTendencyLabels = ['Zero', 'Low', 'Moderate', 'High', 'All Out']

#Set number of simulations to run through
nSims = 1000

#Create the team combinations to simulate
teamCompetitions = [(x,y) for x in teamList for y in teamList[teamList.index(x)+1:]]

#Create the tendency combinations for each team competition
tendencyCompetitions = list(itertools.product(shotTendency,shotTendency))

#Set a check in place for whether to run the sims or load in existing results
#Note that the results generated should be the same given the seeds being set
#throughout. If you wish to generate 'new' results then you can alter the seed
#values throughout
runCompSims = False ##### change to True to re-run sims

#Run simulations
if runCompSims:
    
    #Determine the number of shots to use in each simulation period

    #Calculate mean and SD (and range) for TOTAL number of shots in Power 5 across season
    meanShots = scoreFlowData.groupby(['matchId','period']).count()['shotOutcome'].to_numpy().mean()
    sdShots = scoreFlowData.groupby(['matchId','period']).count()['shotOutcome'].to_numpy().std()
    minShots = scoreFlowData.groupby(['matchId','period']).count()['shotOutcome'].to_numpy().min()
    maxShots = scoreFlowData.groupby(['matchId','period']).count()['shotOutcome'].to_numpy().max()

    #Sample from truncated normal distribution
    #This is truncated to range of shots in a Power 5 period
    #We do half the number of sims here as we're going to invert it between the teams
    #so that it's matched
    #Set seed for consistent sampling
    np.random.seed(12345)
    nSimShots = np.around(stats.truncnorm((minShots - meanShots) / sdShots,
                                          (maxShots - meanShots) / sdShots,
                                          loc = meanShots,
                                          scale = sdShots).rvs(int(nSims/2)))

    #Determine the mean and SD (and range) for PROPORTION of shots teams get in Power 5 across season
    shotProp_teamA = []
    #Extract shots grouped by match, period and team
    groupedPeriodShots = scoreFlowData.groupby(['matchId','squadId','period']).count()['shotOutcome'].reset_index(drop = False)
    #Loop through matchId's
    for matchId in groupedPeriodShots['matchId'].unique():
        #Extract match data
        currMatch = groupedPeriodShots.loc[groupedPeriodShots['matchId'] == matchId,]
        #Get squad names
        squadNames = list(currMatch['squadId'].unique())
        #Calculate the proportion of 'team A'
        shotProp = currMatch.loc[currMatch['squadId'] == squadNames[0],]['shotOutcome'].to_numpy() \
            / (currMatch.loc[currMatch['squadId'] == squadNames[0],]['shotOutcome'].to_numpy() \
               + currMatch.loc[currMatch['squadId'] == squadNames[1],]['shotOutcome'].to_numpy())
        #Append to list
        [shotProp_teamA.append(indShotProp) for indShotProp in shotProp]
    #Calculate mean, sd and range
    meanPropTeamA = np.array(shotProp_teamA).mean()
    sdPropTeamA = np.array(shotProp_teamA).std()
    minPropTeamA = np.array(shotProp_teamA).min()
    maxPropTeamA = np.array(shotProp_teamA).max()

    #Sample from truncated normal distribution
    #This is truncated to range of shot proportions in a Power 5 period
    #We do half the number of sims here as we're going to invert it between the teams
    #so that it's matched
    #Set seed for consistent sampling
    np.random.seed(54321)
    nSimProps = stats.truncnorm((minPropTeamA - meanPropTeamA) / sdPropTeamA,
                                (maxPropTeamA - meanPropTeamA) / sdPropTeamA,
                                loc = meanPropTeamA,
                                scale = sdPropTeamA).rvs(int(nSims/2))

    #Take the proportion of total shots from the simulated values
    #Subtract these from the total shots to allocate the values to team B
    simShotsTeamA = np.around(nSimShots * nSimProps)
    simShotsTeamB = nSimShots - simShotsTeamA

    #Stack these together alternately to balance across teams
    simShotsA = np.concatenate((simShotsTeamA,simShotsTeamB))
    simShotsB = np.concatenate((simShotsTeamB,simShotsTeamA))

    #Sum the shooting numbers for the current team
    shotSums = teamSuperCounts.groupby(['squadId','scoreName']).sum()
    
    #Create a dictionary to store results in
    compSimsData = {'simId': [], 'uniqueSimId': [], 'teamA': [], 'teamB': [],
                    'shotTendencyA': [], 'shotTendencyB': [],
                    'nShotsA': [], 'nStandardA': [], 'nSuperA': [],
                    'nShotsB': [], 'nStandardB': [], 'nSuperB': [],
                    'totalGoalsA': [], 'totalGoalsB': [], 'simMargin': []}
    
    #Loop through competitions
    for competition in teamCompetitions:
        
        #Extract teams
        teamA = competition[0]
        teamB = competition[1]
        
        #Loop through sims
        for simId in range(nSims):
            
            #Simulate a set of probability values to match to tendency to determine
            #whether or not a super shot is taken or not. This is done for each team
            #Team A
            np.random.seed(54321 * (simId+1) + teamList.index(teamA))
            tendencyProbsA = np.random.rand(int(simShotsA[simId]))
            #Team B
            np.random.seed(12345 * (simId+1) + teamList.index(teamB))
            tendencyProbsB = np.random.rand(int(simShotsB[simId]))
            
            #Sample chance of success for the numnber of simulation shots from each
            #of the standard and super shot distributions. Done for each team
            #Team A
            #Standard shots
            np.random.seed(999 * (simId+1) - teamList.index(teamA))
            standardShotProbSuccessA = np.random.beta(shotSums['shotCount'][teamA]['goal'],
                                                      shotSums['shotCount'][teamA]['miss'],
                                                      size = int(simShotsA[simId]))
            #Super shots
            np.random.seed(111 * (simId+1) - teamList.index(teamA))
            superShotProbSuccessA = np.random.beta(shotSums['shotCount'][teamA]['2pt Goal'],
                                                   shotSums['shotCount'][teamA]['2pt Miss'],
                                                   size = int(simShotsA[simId]))
            #Team B
            #Standard shots
            np.random.seed(888 * (simId+1) - teamList.index(teamB))
            standardShotProbSuccessB = np.random.beta(shotSums['shotCount'][teamB]['goal'],
                                                      shotSums['shotCount'][teamB]['miss'],
                                                      size = int(simShotsB[simId]))
            #Super shots
            np.random.seed(222 * (simId+1) - teamList.index(teamB))
            superShotProbSuccessB = np.random.beta(shotSums['shotCount'][teamB]['2pt Goal'],
                                                   shotSums['shotCount'][teamB]['2pt Miss'],
                                                   size = int(simShotsB[simId]))
            
            #Sample the random values that will dictate shot success by being 
            #lower (i.e. successful) or higher (i.e. unsuccessful) versus the 
            #shot probabilities. Done for both teams
            #Team A
            np.random.seed(10101 * (simId+1) - teamList.index(teamA))
            shotSuccessComparatorA = np.random.rand(int(simShotsA[simId]))
            #Team B
            np.random.seed(20202 * (simId+1) - teamList.index(teamB))
            shotSuccessComparatorB = np.random.rand(int(simShotsB[simId]))
            
            #Loop through tendency competitions
            for tendency in tendencyCompetitions:
                
                #Create a logic array for whether the shot is a Super or not based
                #on tendency probabilities for the current shot set. This is done
                #for both teams.
                #Team A
                takeSuperShotA = tendency[0] > tendencyProbsA
                takeSuperShotMultiplierA = [2 if takeSuperShotA[ii] else 1 for ii in range(int(simShotsA[simId]))]
                #Team B
                takeSuperShotB = tendency[1] > tendencyProbsB
                takeSuperShotMultiplierB = [2 if takeSuperShotB[ii] else 1 for ii in range(int(simShotsB[simId]))]
                
                #Get the probabilities of shot success based on the shot type
                #Team A
                allShotProbSuccessA = np.array([superShotProbSuccessA[ii] if takeSuperShotA[ii] else standardShotProbSuccessA[ii] for ii in range(int(simShotsA[simId]))])
                #Team B
                allShotProbSuccessB = np.array([superShotProbSuccessB[ii] if takeSuperShotB[ii] else standardShotProbSuccessB[ii] for ii in range(int(simShotsB[simId]))])
                
                #Determine success of shots
                #Team A
                logicShotSuccessA = allShotProbSuccessA > shotSuccessComparatorA
                #Team B
                logicShotSuccessB = allShotProbSuccessB > shotSuccessComparatorB
                
                #Calculate total goals scored based on shot success and type
                #Team A
                totalGoalsA = np.sum(logicShotSuccessA * takeSuperShotMultiplierA)
                totalGoalsB = np.sum(logicShotSuccessB * takeSuperShotMultiplierB)
                
                #Calculate margin
                simMargin = totalGoalsA - totalGoalsB
                
                #Append data to dictionary
                compSimsData['simId'].append(int(simId))
                compSimsData['uniqueSimId'].append('sim'+''.join([str(ii) for ii in [simId,teamList.index(teamA),teamList.index(teamB)]])+'_'+str(int(tendency[0]*100))+'_'+str(int(tendency[1]*100)))
                compSimsData['teamA'].append(teamA)
                compSimsData['teamB'].append(teamB)
                compSimsData['shotTendencyA'].append(shotTendencyLabels[shotTendency.index(tendency[0])])
                compSimsData['shotTendencyB'].append(shotTendencyLabels[shotTendency.index(tendency[1])])
                compSimsData['nShotsA'].append(int(simShotsA[simId]))
                compSimsData['nShotsB'].append(int(simShotsB[simId]))
                compSimsData['nStandardA'].append(int(np.sum(~np.array(takeSuperShotA))))
                compSimsData['nStandardB'].append(int(np.sum(~np.array(takeSuperShotB))))
                compSimsData['nSuperA'].append(int(np.sum(np.array(takeSuperShotA))))
                compSimsData['nSuperB'].append(int(np.sum(np.array(takeSuperShotB))))
                compSimsData['totalGoalsA'].append(int(totalGoalsA))
                compSimsData['totalGoalsB'].append(int(totalGoalsB))
                compSimsData['simMargin'].append(int(simMargin))
                
    #Save standard sim data to json
    with open('..\\Results\\compSims\\compSimsData.json', 'w') as jsonFile:
        json.dump(compSimsData, jsonFile)
                
else:
    
    #Read in existing simulation data
    with open('..\\Results\\compSims\\compSimsData.json', 'r') as jsonFile:
        compSimsData = json.load(jsonFile)
        
#Convert to dataframe
compSimsData_df = pd.DataFrame.from_dict(compSimsData)

# %% Visualise competitive sim margins

#Set-up figure
fig, ax = plt.subplots(nrows = 5, ncols = 5, figsize = (10,8),
                       sharex = True, sharey = True)

#Adjust spacing
plt.subplots_adjust(left = 0.06, right = 0.96,
                    bottom = 0.13, top = 0.97,
                    wspace = 0.1, hspace = 0.1)
                
#Create a shortened list of tendency competitions to plot
tendencyCompetitionsPaired = [(x,y) for x in shotTendencyLabels for y in shotTendencyLabels[shotTendencyLabels.index(x)+1:]]
for tendency in shotTendencyLabels:
    tendencyCompetitionsPaired.append((tendency, tendency))

#Loop through paired competitions and plot data
for tendency in tendencyCompetitions:
    
    #Get pair
    tendencyPair = (shotTendencyLabels[shotTendency.index(tendency[0])],
                    shotTendencyLabels[shotTendency.index(tendency[1])])
    
    #Identify the axes to plot on based on index in tendency labels list
    plotAx = ax[shotTendencyLabels.index(tendencyPair[1]),
                shotTendencyLabels.index(tendencyPair[0])]
        
    #Extract data meeting shot tendency conditions
    #Get the two paired combos
    currDataComboA = compSimsData_df.loc[(compSimsData_df['shotTendencyA'] == tendencyPair[0]) &
                                          (compSimsData_df['shotTendencyB'] == tendencyPair[1]),]
    currDataComboB = compSimsData_df.loc[(compSimsData_df['shotTendencyA'] == tendencyPair[1]) &
                                          (compSimsData_df['shotTendencyB'] == tendencyPair[0]),]
    
    #Invert margins in B data to reflect current team
    currDataComboB['simMargin'] = currDataComboB['simMargin']*-1
    
    #Create list to store violin data in
    violinData = []
    
    #Put all team data into an array
    violinData.append(pd.concat([currDataComboA,currDataComboB])['simMargin'].to_numpy())
    
    #Loop through teams and extract data for the current tendency combos
    for team in teamList:
        
        #Extract data for team
        currDataComboA_teamA = currDataComboA.loc[currDataComboA['teamA'] == team,]
        currDataComboB_teamB = currDataComboB.loc[currDataComboB['teamB'] == team,]
        
        #Extract and store data in array for violin plot
        violinData.append(pd.concat([currDataComboA_teamA,currDataComboB_teamB])['simMargin'].to_numpy())
        
    #Plot and edit the violins and data points separately
    for ii, arr in enumerate(violinData):
        #Plot violin
        violinPart = plotAx.violinplot(dataset = arr, positions = [ii],
                                       showextrema = True, widths = 0.9)
        #Edit colouring
        #Violin
        violinPart['bodies'][0].set_facecolor(list(colourDict.values())[ii])
        violinPart['bodies'][0].set_edgecolor('None')
        violinPart['bodies'][0].set_alpha(0.3)
        violinPart['bodies'][0].set_zorder(1)
        #Bars
        violinPart['cbars'].set_color(list(colourDict.values())[ii])
        violinPart['cbars'].set_linestyle('--')
        violinPart['cbars'].set_alpha(0.5)
        violinPart['cbars'].set_linewidth(1)
        violinPart['cbars'].set_capstyle('butt')
        #Caps
        violinPart['cmaxes'].set_color(list(colourDict.values())[ii])
        violinPart['cmaxes'].set_alpha(0.5)
        violinPart['cmins'].set_color(list(colourDict.values())[ii])
        violinPart['cmins'].set_alpha(0.5)
        #Plot mean point
        plotAx.scatter(ii, arr.mean(),
                       marker = 'o', s = 15, zorder = 2,
                       color = list(colourDict.values())[ii])
        #Plot standard deviation
        plotAx.vlines(ii, arr.mean() - arr.std(), arr.mean() + arr.std(),
                      color  = list(colourDict.values())[ii],
                      ls = '-', lw = 2, zorder = 3)
        
    #Add margin line at y = 0
    plotAx.axhline(y = 0, ls = '--', lw = 0.5,
                   color = 'k', zorder = 0)
    
    #Set title & additional y-label where pairs match
    if tendencyPair[1] == 'Zero':
        #Add title
        plotAx.set_title(tendencyPair[0], fontsize = 14, fontweight = 'bold')
           
    #Set additional side titles
    if tendencyPair[0] == 'All Out':
        #Add secondary axis
        plotAx2 = plotAx.twinx()
        #Turn off ticks and labels on this axis
        plotAx2.set_yticks([])
        #Add label
        plotAx2.set_ylabel(tendencyPair[1], labelpad = 15,
                           fontsize = 14, fontstyle = 'italic', fontweight = 'regular',
                           rotation = -90)

    #Set x-Label
    plotAx.set_xlabel('')

    #Set x-labels & ticks appropriately
    if tendencyPair[1] == 'All Out':
        #Set x-ticks
        plotAx.set_xticks(range(len(list(colourDict.keys()))))
        #Apply x-tick labels appropriately
        plotAx.set_xticklabels(list(colourDict.keys()),
                               fontsize = 10, fontweight = 'bold',
                               rotation = 90)
        
    #Apply y-label and ticks appropriately
    if tendencyPair[0] == 'Zero':
        #Label
        plotAx.set_ylabel('Margin', fontsize = 12, fontweight = 'bold')
        #Ticks
        plotAx.set_yticks(np.linspace(-20,20,5,dtype=int))
        plotAx.set_yticklabels(np.linspace(-20,20,5,dtype=int),
                               fontsize = 10)
    else:
        #Label
        plotAx.set_ylabel('')
        
#Save figure
plt.savefig('..\\Results\\compSims\\compSimMargins.png',
            format = 'png', facecolor = fig.get_facecolor(),
            dpi = 300)
plt.savefig('..\\Results\\compSims\\compSimMargins.jpeg',
            format = 'jpeg', facecolor = fig.get_facecolor(),
            dpi = 600)

#Close figure
plt.close()

# %% Collate and plot individual team results

#Loop through teams
for team in teamList:
    
    #Set-up figure
    fig, ax = plt.subplots(nrows = 5, ncols = 5, figsize = (10,8),
                           sharex = True, sharey = True)

    #Adjust spacing
    plt.subplots_adjust(left = 0.06, right = 0.96,
                        bottom = 0.06, top = 0.97,
                        wspace = 0.1, hspace = 0.1)

    #Loop through paired competitions and plot data
    for tendency in tendencyCompetitions:
        
        #Get pair
        tendencyPair = (shotTendencyLabels[shotTendency.index(tendency[0])],
                        shotTendencyLabels[shotTendency.index(tendency[1])])
        
        #Identify the axes to plot on based on index in tendency labels list
        plotAx = ax[shotTendencyLabels.index(tendencyPair[1]),
                    shotTendencyLabels.index(tendencyPair[0])]
            
        #Extract data meeting shot tendency conditions
        #Get the two paired combos
        currDataComboA = compSimsData_df.loc[(compSimsData_df['shotTendencyA'] == tendencyPair[0]) &
                                             (compSimsData_df['teamA'] == team) &
                                             (compSimsData_df['shotTendencyB'] == tendencyPair[1]),]
        currDataComboB = compSimsData_df.loc[(compSimsData_df['shotTendencyA'] == tendencyPair[1]) &
                                              (compSimsData_df['shotTendencyB'] == tendencyPair[0]) & 
                                              (compSimsData_df['teamB'] == team),]
        
        #Invert margins in B data to reflect current team
        currDataComboB['simMargin'] = currDataComboB['simMargin']*-1
        
        #Concatenate dataframes
        currDataCombo = pd.concat([currDataComboA, currDataComboB])
        
        #Calculate number of bins necessary to allocate one margin point to each bin
        #Put condition in place to have 2 point margin bins for when
        #both teams are at 'All Out' as odd margins aren't possible
        if tendencyPair[0] == 'All Out' and tendencyPair[1] == 'All Out':
            nBins = (currDataCombo['simMargin'].to_numpy().max() - currDataCombo['simMargin'].to_numpy().min() + 2) / 2
        else:
            nBins = (currDataCombo['simMargin'].to_numpy().max() - currDataCombo['simMargin'].to_numpy().min()) + 1
        
        #Calculate proportion of wins & losses for current 'team'
        winProps = (sum(n > 0 for n in currDataComboA['simMargin']) + sum(n < 0 for n in currDataComboB['simMargin'])) / len(currDataCombo)
        lossProps = (sum(n < 0 for n in currDataComboA['simMargin']) + sum(n > 0 for n in currDataComboB['simMargin'])) / len(currDataCombo)
        
        #Calculate mean and SD win/loss margin
        winMarginM = np.concatenate((currDataComboA.loc[currDataComboA['simMargin'] > 0,]['simMargin'].to_numpy(),
                                     currDataComboB.loc[currDataComboB['simMargin'] < 0,]['simMargin'].to_numpy())).mean()
        winMarginSD = np.concatenate((currDataComboA.loc[currDataComboA['simMargin'] > 0,]['simMargin'].to_numpy(),
                                      currDataComboB.loc[currDataComboB['simMargin'] < 0,]['simMargin'].to_numpy())).std()
        lossMarginM = np.concatenate((currDataComboA.loc[currDataComboA['simMargin'] < 0,]['simMargin'].to_numpy(),
                                      currDataComboB.loc[currDataComboB['simMargin'] > 0,]['simMargin'].to_numpy())).mean()
        lossMarginSD = np.concatenate((currDataComboA.loc[currDataComboA['simMargin'] < 0,]['simMargin'].to_numpy(),
                                       currDataComboB.loc[currDataComboB['simMargin'] > 0,]['simMargin'].to_numpy())).std()
        
        #Plot the current histogram
        hx = sns.histplot(currDataCombo['simMargin'], kde = False,
                          bins = int(nBins), color = 'grey',
                          ax = plotAx,
                          alpha = 0.75, linewidth = 1)
        
        #Set colours of each bars depending on bin value
        #Team wins get their colour while others remain greyed out
        #Get the unique values of bins in a sorted list
        sortedBinVals = np.linspace(currDataCombo['simMargin'].to_numpy().min(),
                                    currDataCombo['simMargin'].to_numpy().max(),
                                    int(nBins))
        for binInd, binVal in enumerate(sortedBinVals):
            #Check bin value and plot colour accordingly
            if binVal > 0:
                hx.patches[binInd].set_facecolor(colourDict[team])
                hx.patches[binInd].set_alpha(0.7)
                hx.patches[binInd].set_edgecolor(colourDict[team])
            #Add vertical line if zero
            elif binVal == 0:
                plotAx.axvline(0, color = 'k', ls = '--', lw = 0.5)
        
        #Set loss proportion (i.e. opposition wins)
        plotAx.text(0.025, 0.800,
                    str(round(lossProps*100,1))+'%\n'+str(round(lossMarginM,1))+' '+u'\u00B1'+' '+str(round(lossMarginSD,1)),
                    ha = 'left', fontsize = 8,
                    color = 'grey',
                    transform = plotAx.transAxes)
        #Set win proportion (i.e. team wins)
        plotAx.text(0.975, 0.800,
                    str(round(winProps*100,1))+'%\n'+str(round(winMarginM,1))+' '+u'\u00B1'+' '+str(round(winMarginSD,1)),
                    ha = 'right', fontsize = 8,
                    color = colourDict[team],
                    transform = plotAx.transAxes)
        
        #Set title & additional y-label where pairs match
        if tendencyPair[1] == 'Zero':
            #Add title
            plotAx.set_title(tendencyPair[0], color = colourDict[team],
                             fontsize = 12, fontweight = 'bold')
            
            
        #Set additional side titles
        if tendencyPair[0] == 'All Out':
            #Add secondary axis
            plotAx2 = plotAx.twinx()
            #Turn off ticks and labels on this axis
            plotAx2.set_yticks([])
            #Add label
            plotAx2.set_ylabel(tendencyPair[1], labelpad = 15,
                               fontsize = 12, fontweight = 'bold',
                               rotation = -90)

        #Set x-labels & ticks appropriately
        if tendencyPair[1] == 'All Out':
            #Label
            plotAx.set_xlabel('Margin', fontsize = 10, fontweight = 'bold')
            #Tick
            plotAx.set_xticks(np.linspace(-20,20,5,dtype=int))
            plotAx.set_xticklabels(np.linspace(-20,20,5,dtype=int),
                                   fontsize = 8)
        else:
            #Label
            plotAx.set_xlabel('')
        
        #Apply y-label appropriately
        if tendencyPair[0] == 'Zero':
            plotAx.set_ylabel('Count (n)', fontsize = 10, fontweight = 'bold')
        else:
            plotAx.set_ylabel('')
    
    #Save figure
    plt.savefig(f'..\\Results\\compSims\\{team}_compSimHistograms.png',
                format = 'png', facecolor = fig.get_facecolor(),
                dpi = 300)
    
    #Close figure
    plt.close()

# %%% ----- End of superShotSimulator.py -----