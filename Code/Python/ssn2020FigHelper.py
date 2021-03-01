# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 20:29:59 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This helper script contains a series of functions that are used for
plotting figures from the analysed data.

"""

# %% Import packages

import pandas as pd
pd.options.mode.chained_assignment = None #turn of pandas chained warnings
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle 
import math
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

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

# %% All teams heatmap

def allTeamsHeatmap(df_superSimResults, teamList, superShotProps,
                    propCats, teamSuperProps,
                    plotNorm = True, plotAbs = True, saveDir = os.getcwd()):

    # Function for plotting total team points from standard vs. super shots
    # in each game of the round
    #
    # Input:    df_superSimResults - results dataframe of simulations
    #           teamList - list of team name strings
    #           superShotProps - list of super shot proportions tested
    #           propCats - array of super shot categorys grabbed
    #           teamSuperProps - values of teams actual super shot proportions
    #           plotNorm - whether to plot the normalised heatmap
    #           plotAbs - whether to plot the absolute heatmap
    #           saveDir - directory to save files in to
    
    #Get current directory to navigate back to
    currDir = os.getcwd()
    
    #Navigate to figures directory
    os.chdir(saveDir)
    
    #Set-up axes to plot on
    whichAx = [[0,0], [0,1],
               [1,0], [1,1],
               [2,0], [2,1],
               [3,0], [3,1]]
    
    #Create an all team heatmap
    
    #Normalised to maximum score
    if plotNorm:
    
        #Create figure to plot on
        fig, ax = plt.subplots(figsize=(18, 9), nrows = 4, ncols = 2)
        
        #Loop through teams and plot heat grid of their points
        for tt in range(0,len(teamList)):
            
            #Extract current teams data
            df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
            
            #Get the number of simulations ran for the current teams shots
            nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
            
            #Initialise array to store data in
            simArray = np.zeros([len(superShotProps)-1,nTeamSims])
            
            #Loop through the proportions
            for pp in range(0,len(propCats)):
                
                #Extract the dataframe of the current proportion
                df_currProp = df_currTeamSims.iloc[pp*nTeamSims:(pp*nTeamSims)+nTeamSims]
                
                #Extract the score
                scoreVals = df_currProp['totalPts'].values
                
                #Sort the values from lowest to highest
                scoreVals.sort()
                
                #Place in array (in reverse order)
                simArray[(pp+1)*-1,:] = scoreVals
                
            #Normalise sim array to teams maximum value (i.e. 0-1)
            teamMax = np.max(simArray)
            simArray_norm = simArray / teamMax
            
            #Convert sim to a dataframe for plotting
            df_simArray = pd.DataFrame(simArray)
            df_simArray_norm = pd.DataFrame(simArray_norm)
            #Set the index using the prop categories
            propCats.sort()
            df_simArray.set_index(propCats[::-1], inplace = True)
            df_simArray_norm.set_index(propCats[::-1], inplace = True)
            
            #Plot heatmap
            sns.heatmap(df_simArray_norm,
                        cmap="RdYlGn", annot = False,
                        linewidths = 0, # vmin = gMin, vmax = gMax,
                        ax = ax[whichAx[tt][0],whichAx[tt][1]])
            
            #Add horizontal separators via horizontal line
            lineWidth = 2
            for ii in range(simArray.shape[0]+1):
                ax[whichAx[tt][0],whichAx[tt][1]].axhline(ii, color = 'white', lw = lineWidth)
            
            #Outline the actual proportion for the team
            topLine = len(df_simArray) - math.ceil(teamSuperProps[tt]*10) - 1
            bottomLine = len(df_simArray) - math.floor(teamSuperProps[tt]*10) - 1
            ax[whichAx[tt][0],whichAx[tt][1]].add_patch(Rectangle(xy = (0-10, bottomLine), 
                                                                  width = nTeamSims*2, height = 1, 
                                                                  fill = False,  
                                                                  edgecolor = 'black', 
                                                                  lw = lineWidth,
                                                                  zorder = 4))
                
            #Remove x-axis
            ax[whichAx[tt][0],whichAx[tt][1]].get_xaxis().set_ticks([])
            
            #Add x-axis label
            if whichAx[tt][0] == 3:
                ax[whichAx[tt][0],whichAx[tt][1]].set_xlabel('Power 5 Simulations (n = '+locale.format_string("%d", nTeamSims, grouping=True)+')')
            
            #Set y-ticks
            ax[whichAx[tt][0],whichAx[tt][1]].set_yticks([0.5, 1.5, 2.5, 3.5, 4.5,
                                                          5.5, 6.5, 7.5, 8.5, 9.5])
            
            #Set y-tick labels
            ax[whichAx[tt][0],whichAx[tt][1]].set_yticklabels(list(df_simArray.index),
                                                              fontsize = 8)
            
            #Add y-axis label
            if whichAx[tt][1] == 0:
                ax[whichAx[tt][0],whichAx[tt][1]].set_ylabel('Super Shot Proportion')
            
            #Add colourbar label
            ax[whichAx[tt][0],whichAx[tt][1]].collections[0].colorbar.set_label('Goals Scored\n(% max. value)')
            
            #Add title
            ax[whichAx[tt][0],whichAx[tt][1]].set_title(teamList[tt],
                                                        fontweight = 'bold',
                                                        fontsize = 12)
    
        #Set tight plot layout to fill frame
        plt.tight_layout()
        plt.show()
    
        #Save all teams figure
        plt.savefig('SuperShotSimulations_HeatMap_AllTeams_Norm.pdf')
        plt.savefig('SuperShotSimulations_HeatMap_AllTeams_Norm.png', format = 'png', dpi = 300)
        
        #Close figure
        plt.close()
    
    #Absolute score
    if plotAbs:
    
        #Create figure to plot on
        fig, ax = plt.subplots(figsize=(18, 9), nrows = 4, ncols = 2)
        
        #Loop through teams and plot heat grid of their points
        for tt in range(0,len(teamList)):
            
            #Extract current teams data
            df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
            
            #Get the number of simulations ran for the current teams shots
            nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
            
            #Initialise array to store data in
            simArray = np.zeros([len(superShotProps)-1,nTeamSims])
            
            #Loop through the proportions
            for pp in range(0,len(propCats)):
                
                #Extract the dataframe of the current proportion
                df_currProp = df_currTeamSims.iloc[pp*nTeamSims:(pp*nTeamSims)+nTeamSims]
                
                #Extract the score
                scoreVals = df_currProp['totalPts'].values
                
                #Sort the values from lowest to highest
                scoreVals.sort()
                
                #Place in array (in reverse order)
                simArray[(pp+1)*-1,:] = scoreVals
                
            #Normalise sim array to teams maximum value (i.e. 0-1)
            teamMax = np.max(simArray)
            
            #Convert sim to a dataframe for plotting
            df_simArray = pd.DataFrame(simArray)
            #Set the index using the prop categories
            propCats.sort()
            df_simArray.set_index(propCats[::-1], inplace = True)
            
            #Plot heatmap
            sns.heatmap(df_simArray,
                        cmap="RdYlGn", annot = False,
                        linewidths = 0, vmin = 0, vmax = teamMax,
                        cbar_kws={"ticks":[0,teamMax/2,teamMax]},
                        ax = ax[whichAx[tt][0],whichAx[tt][1]])
            
            #Add horizontal separators via horizontal line
            lineWidth = 2
            for ii in range(simArray.shape[0]+1):
                ax[whichAx[tt][0],whichAx[tt][1]].axhline(ii, color = 'white', lw = lineWidth)
            
            #Outline the actual proportion for the team
            topLine = len(df_simArray) - math.ceil(teamSuperProps[tt]*10) - 1
            bottomLine = len(df_simArray) - math.floor(teamSuperProps[tt]*10) - 1
            ax[whichAx[tt][0],whichAx[tt][1]].add_patch(Rectangle(xy = (0-10, bottomLine), 
                                                                  width = nTeamSims*2, height = 1, 
                                                                  fill = False,  
                                                                  edgecolor = 'black', 
                                                                  lw = lineWidth,
                                                                  zorder = 4))
                
            #Remove x-axis
            ax[whichAx[tt][0],whichAx[tt][1]].get_xaxis().set_ticks([])
            
            #Add x-axis label
            if whichAx[tt][0] == 3:
                ax[whichAx[tt][0],whichAx[tt][1]].set_xlabel('Power 5 Simulations (n = '+locale.format_string("%d", nTeamSims, grouping=True)+')')
            
            #Set y-ticks
            ax[whichAx[tt][0],whichAx[tt][1]].set_yticks([0.5, 1.5, 2.5, 3.5, 4.5,
                                                          5.5, 6.5, 7.5, 8.5, 9.5])
            
            #Set y-tick labels
            ax[whichAx[tt][0],whichAx[tt][1]].set_yticklabels(list(df_simArray.index),
                                                              fontsize = 8)
            
            #Add y-axis label
            if whichAx[tt][1] == 0:
                ax[whichAx[tt][0],whichAx[tt][1]].set_ylabel('Super Shot Proportion')
            
            #Add colourbar label
            ax[whichAx[tt][0],whichAx[tt][1]].collections[0].colorbar.set_label('Goals Scored')
                
            #Add title
            ax[whichAx[tt][0],whichAx[tt][1]].set_title(teamList[tt],
                                                        fontweight = 'bold',
                                                        fontsize = 12)
            
        #Set tight plot layout to fill frame
        plt.tight_layout()
        plt.show()
        
        #Save all teams figure
        plt.savefig('SuperShotSimulations_HeatMap_AllTeams_Abs.pdf')
        plt.savefig('SuperShotSimulations_HeatMap_AllTeams_Abs.png', format = 'png', dpi = 300)
    
        #Close figure
        plt.close()
    
    #Return to working directory
    os.chdir(currDir)
    
# %% Single teams heatmap

def singleTeamHeatmap(df_superSimResults, superShotProps,
                      propCats, teamSuperProps = None,
                      teamName = None, teamColour = None,
                      saveDir = os.getcwd()):

    # Function for plotting total team points from standard vs. super shots
    # in each game of the round
    #
    # Input:    df_superSimResults - results dataframe of simulations
    #           superShotProps - list of super shot proportions tested
    #           propCats - array of super shot categorys grabbed
    #           teamSuperProps - value of teams actual super shot proportions
    #           teamName - name of team to plot
    #           teamColour - hex code for teams colour plot
    #           saveDir - directory to save files in to
    
    #Check inputs
    if teamName is None:
        raise ValueError('A team name is required.')
    if teamSuperProps is None:
        raise ValueError('Teams super shot proportion is required.')
    if teamColour is None:
        raise ValueError('Teams hex colour code is required.')
    
    #Get current directory to navigate back to
    currDir = os.getcwd()
    
    #Navigate to figures directory
    os.chdir(saveDir)
    
    #Create figure and axes to plot on
    fig = plt.figure(figsize=(12, 3.5))
    ax1 = plt.subplot2grid((1, 4), (0, 0), colspan = 3)
    ax2 = plt.subplot2grid((1, 4), (0, 3), colspan = 1)
    
    #Heat map
    
    #Extract current teams data
    df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamName),]
    
    #Get the number of simulations ran for the current teams shots
    nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
    
    #Initialise array to store data in
    simArray = np.zeros([len(superShotProps)-1,nTeamSims])
    
    #Loop through the proportions
    for pp in range(0,len(propCats)):
        
        #Extract the dataframe of the current proportion
        df_currProp = df_currTeamSims.iloc[pp*nTeamSims:(pp*nTeamSims)+nTeamSims]
        
        #Extract the score
        scoreVals = df_currProp['totalPts'].values
        
        #Sort the values from lowest to highest
        scoreVals.sort()
        
        #Place in array (in reverse order)
        simArray[(pp+1)*-1,:] = scoreVals
    
    #Convert sim to a dataframe for plotting
    df_simArray = pd.DataFrame(simArray)
    #Set the index using the prop categories
    propCats.sort()
    df_simArray.set_index(propCats[::-1], inplace = True)
    
    #Get team max for color bar
    teamMax = np.max(simArray)
    
    #Plot heatmap
    sns.heatmap(df_simArray, cmap="RdYlGn", annot = False,
                vmin = 0, vmax = teamMax,
                cbar_kws={"ticks":[0,teamMax/2,teamMax]},
                linewidths = 0, ax = ax1)
    
    #Add horizontal separators via horizontal line
    lineWidth = 2
    for ii in range(simArray.shape[0]+1):
        ax1.axhline(ii, color = 'white', lw = lineWidth)
    
    #Outline the actual proportion for the team
    topLine = len(df_simArray) - math.ceil(teamSuperProps*10) - 1
    bottomLine = len(df_simArray) - math.floor(teamSuperProps*10) - 1
    ax1.add_patch(Rectangle(xy = (0-10, bottomLine), 
                            width = nTeamSims*2, height = 1, 
                            fill = False,  
                            edgecolor = 'black', 
                            lw = lineWidth,
                            zorder = 4))
        
    #Remove x-axis
    ax1.get_xaxis().set_ticks([])
    
    #Add x-axis label
    ax1.set_xlabel('Rebel Power 5 Simulations (n = '+locale.format_string("%d", nTeamSims, grouping=True)+')')
    
    #Set y-ticks
    ax1.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5,
                   5.5, 6.5, 7.5, 8.5, 9.5])
    
    #Set y-tick labels
    ax1.set_yticklabels(list(df_simArray.index),
                       fontsize = 10)
    
    #Add y-axis label
    ax1.set_ylabel('Super Shot Proportion')
    
    #Add colourbar label
    ax1.collections[0].colorbar.set_label('Goals Scored')
    
    #Add title
    ax1.set_title(teamName,
                 fontweight = 'bold',
                 fontsize = 12)
    
    #Box plot
    
    #Create the boxplot
    gx = sns.boxplot(x = 'superPropCat', y = 'totalPts',
                     data = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamName),],
                     whis = [0, 100], width = 0.65,
                     color = teamColour,
                     ax = ax2)
    
    #Set the box plot face and line colours

    #First, identify the box to keep solid based on teams actual super shot proportions
    solidBarInd = int(np.floor(teamSuperProps*10))

    #Loop through boxes and fix colours
    for ii in range(0,len(ax2.artists)):
    
        #Get the current artist
        artist = ax2.artists[ii]
    
        #If the bar matches the one we want to keep solid, just change lines to black
        if ii == solidBarInd:
        
            #Set edge colour to black
            artist.set_edgecolor('k')
        
            #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
            #Loop over them here, and use black
            for jj in range(ii*6,ii*6+6):
                line = ax2.lines[jj]
                line.set_color('k')
                line.set_mfc('k')
                line.set_mec('k')
            
        else:
        
            #Set the linecolor on the artist to the facecolor, and set the facecolor to None
            col = artist.get_facecolor()
            artist.set_edgecolor(col)
            artist.set_facecolor('None')
        
            #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
            #Loop over them here, and use the same colour as above
            for jj in range(ii*6,ii*6+6):
                line = ax2.lines[jj]
                line.set_color(col)
                line.set_mfc(col)
                line.set_mec(col)

    #Set x labels
    gx.set(xlabel = 'Super Shot Proportion')
    
    #Set y label only for first column
    gx.set(ylabel = 'Goals Scored')
    
    #Set y-ticks
    ax2.set_yticks([0,teamMax/2,teamMax])
    
    #Flip y-axes to right side
    ax2.yaxis.set_ticks_position('right')
    ax2.yaxis.set_label_position('right')
    
    #Rotate x-tick labels, but only for bottom row
    ax2.tick_params('x', labelrotation = 90)

    #Set title
    ax2.set_title('', fontdict = {'fontsize': 12,'fontweight': 'bold'})

    #Adjust subplots to fit
    plt.subplots_adjust(bottom = 0.30)
    plt.show()
    
    #Save team figure
    plt.savefig('SuperShotSimulations_HeatMap_'+teamName+'.pdf')
    plt.savefig('SuperShotSimulations_HeatMap_'+teamName+'.png', format = 'png', dpi = 300)
    
    #Close figure
    plt.close()

    #Return to working directory
    os.chdir(currDir)
    
# %% Visualisation of individual teams competitive sims

def indCompSimVis(df_compSimResults, team1, team2, compProps, colourDict,
                  tt, cc, saveDir = os.getcwd()):
    
    # Function to plot distributions of competitive sims for two teams
    #
    # Input:    df_compSimResults - results dataframe of simulations
    #           team1 - team name for first team
    #           team2 - team name for second team
    #           compProps - proportions of super shots being compared
    #           colourDict - colour dictionary for team colours on plots
    #           tt - team index number for team 1
    #           saveDir - directory to save files in to
    
    #Get current directory to navigate back to
    currDir = os.getcwd()
    
    #Navigate to figures directory
    os.chdir(saveDir)
    
    #Get each teams colour
    teamCol1 = colourDict[team1]
    teamCol2 = colourDict[team2]
    
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
                df_currComp = df_compSimResults.loc[(df_compSimResults['teamName'] == team1) &
                                                    (df_compSimResults['opponentName'] == team2) &
                                                    (df_compSimResults['teamSuperProp'] == compProps[p2]) &
                                                    (df_compSimResults['opponentSuperProp'] == compProps[p1]),]
            elif cc < tt:
                df_currComp = df_compSimResults.loc[(df_compSimResults['teamName'] == team2) &
                                                    (df_compSimResults['opponentName'] == team1) &
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
                                 team2+' '+str(math.trunc(compProps[p1]*100))+'% / '+
                                 team1+' '+str(math.trunc(compProps[p2]*100))+'%',
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
                                  team2+' '+str(math.trunc(compProps[p1]*100))+'%',
                                  ha = 'left', fontsize = 9,
                                  color = teamCol2,
                                  transform = ax[p1,p2].transAxes)
            #Set team as right figure title and colour
            txt2 = ax[p1,p2].text(0.5 + titleWidth/2, 1.075,
                                  team1+' '+str(math.trunc(compProps[p2]*100))+'%',
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
    
    #Set tight figure layout
    plt.tight_layout()
    plt.show()
    
    #Save team figure
    plt.savefig('CompetitiveSims_'+team1+'-'+team2+'_MarginDistribution.pdf')
    plt.savefig('CompetitiveSims_'+team1+'-'+team2+'_MarginDistribution.png', format = 'png', dpi = 300)
    
    #Close figure
    plt.close()
    
    #Return to working directory
    os.chdir(currDir)
    
# %% Visulalise all of a teams competitive sims

def allCompSimVis(df_compSimResults, teamName, compProps, colourDict, saveDir = os.getcwd()):
    
    # Function to plot distributions of competitive sims for two teams
    #
    # Input:    df_compSimResults - results dataframe of simulations
    #           teamName - name of team for current visualisation
    #           compProps - proportions of super shots being compared
    #           colourDict - colour dictionary for team colours on plots
    #           saveDir - directory to save files in to
    
    #Get current directory to navigate back to
    currDir = os.getcwd()
    
    #Navigate to figures directory
    os.chdir(saveDir)
    
    #Get the current teams colour
    teamCol = colourDict[teamName]
    
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
            df_currComp1 = df_compSimResults.loc[(df_compSimResults['teamName'] == teamName) &
                                                 (df_compSimResults['teamSuperProp'] == compProps[p2])&
                                                 (df_compSimResults['opponentName'] != teamName) &
                                                 (df_compSimResults['opponentSuperProp'] == compProps[p1]),]
            df_currComp2 = df_compSimResults.loc[(df_compSimResults['opponentName'] == teamName) &
                                                 (df_compSimResults['opponentSuperProp'] == compProps[p2]) &
                                                 (df_compSimResults['teamName'] != teamName) &
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
                                 'Opponents '+str(math.trunc(compProps[p1]*100))+'% / '+
                                 teamName+' '+str(math.trunc(compProps[p2]*100))+'%',
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
                                  'Opponents '+str(math.trunc(compProps[p1]*100))+'%',
                                  ha = 'left', fontsize = 9,
                                  color = 'k',
                                  transform = ax[p1,p2].transAxes)
            #Set team as right figure title and colour
            txt2 = ax[p1,p2].text(0.5 + titleWidth/2, 1.075,
                                  teamName+' '+str(math.trunc(compProps[p2]*100))+'%',
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
    plt.show()    
    
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
        
    #Save team figure
    plt.savefig('CompetitiveSims_'+teamName+'-AllOpponents_MarginDistribution.pdf')
    plt.savefig('CompetitiveSims_'+teamName+'-AllOpponents_MarginDistribution.png', format = 'png', dpi = 300)
    
    #Close figure
    plt.close()
    
    #Return to working directory
    os.chdir(currDir)
    
    #Close figure
    plt.close()
    
# %% Visualise grouped data across teams for competitive sims

def groupedCompSimVis(df_compSimResults, compProps, saveDir = os.getcwd()):
    
    # Function to plot distributions of competitive sims for two teams
    #
    # Input:    df_compSimResults - results dataframe of simulations
    #           compProps - proportions of super shots being compared
    #           saveDir - directory to save files in to
    
    #Get current directory to navigate back to
    currDir = os.getcwd()
    
    #Navigate to figures directory
    os.chdir(saveDir)

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
    plt.show()
    
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
    
    #Save figure
    plt.savefig('CompetitiveSims_GroupedTeams_MarginDistribution.pdf')
    plt.savefig('CompetitiveSims_GroupedTeams_MarginDistribution.png', format = 'png', dpi = 300)
    
    #Close figure
    plt.close()
    
    #Return to working directory
    os.chdir(currDir)
    
    #Close figure
    plt.close()

# %% Visualise team margins from the competitive sims

def marginCompSimVis(df_compSimMargins, compProps, colourDict, saveDir = os.getcwd()):
    
    # Function to plot distributions of competitive sims for two teams
    #
    # Input:    df_compSimMargins - results dataframe of simulations
    #           compProps - proportions of super shots being compared
    #           colourDict - colour dictionary for team colours on plots
    #           saveDir - directory to save files in to
    
    #Get current directory to navigate back to
    currDir = os.getcwd()
    
    #Navigate to figures directory
    os.chdir(saveDir)
    
    #Set the subplot figure to plot on
    fig, ax = plt.subplots(figsize=(11, 11), nrows = 5, ncols = 5)
    
    #Loop through the simulated proportions for each team
    for p1 in range(0,len(compProps)):
        for p2 in range(0,len(compProps)):
    
            #Split to get example of 0% prop vs. 100% prop opponent
            df_currPlot = df_compSimMargins.loc[(df_compSimMargins['teamSuperProp'] == compProps[p1]) &
                                                (df_compSimMargins['opponentSuperProp'] == compProps[p2]),]
    
            #Plot data
            sns.boxplot(x = 'teamName', y = 'margin',
                        hue = 'teamName', palette = list(colourDict.values()),
                        dodge = False, whis = [0,100],
                        data = df_currPlot, ax = ax[p1,p2])
    
            #Turn off legend
            ax[p1,p2].legend().set_visible(False)
    
            #Add dashed line at zero
            ax[p1,p2].axhline(y = 0, linestyle = '--', color = 'grey', linewidth = 1, zorder = 0)
    
            #Convert box plots to team colours and blank faces
            for ii in range(0,len(ax[p1,p2].artists)):
                
                #Get the current artist
                artist = ax[p1,p2].artists[ii]
                
                #Set the linecolor on the artist to the facecolor, and set the facecolor to None
                col = artist.get_facecolor()
                artist.set_edgecolor(col)
                artist.set_facecolor('None')
    
                #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
                #Loop over them here, and use the same colour as above
                for jj in range(ii*6,ii*6+6):
                    line = ax[p1,p2].lines[jj]
                    line.set_color(col)
                    line.set_mfc(col)
                    line.set_mec(col)
                    
            #Set title
            txt = ax[p1,p2].text(0.5, 1.075,
                                 'Team '+str(math.trunc(compProps[p2]*100))+'% / ' +
                                 'Opponent '+str(math.trunc(compProps[p1]*100))+'%',
                                 ha = 'center', fontsize = 9,
                                 transform = ax[p1,p2].transAxes)
            
            #Format x-axes ticks
            #Remove x-label
            ax[p1,p2].set_xlabel('')
            #Keep/remove team names
            if p1 == len(compProps)-1:
                #Set labels, fontsize and rotation
                ax[p1,p2].set_xticklabels(ax[p1,p2].get_xticklabels(),
                                          fontsize = 8, rotation = 90)
            else:
                #Remove labels
                ax[p1,p2].set_xticklabels([], fontsize = 8)
                
            #Set y-label if on first column
            if p2 == 0:
                ax[p1,p2].set_ylabel('Margin', fontsize = 9)
            else:
                #Remove label
                ax[p1,p2].set_ylabel('')
    
    #Identify max and min height of axes and set this limit
    maxY = 0 #blank starting value
    minY = 0 #blank starting value
    for aa in range(0,len(fig.get_axes())):
        #Get current axes
        lims = fig.get_axes()[aa].get_ylim()
        #Check if greater or less than current limits
        if lims[0] < minY:
            minY = lims[0]
        if lims[1] > maxY:
            maxY = lims[1]
                
    #Reset to nearest whole number ceiling
    maxY = math.ceil(maxY)
    minY = math.ceil(minY)
    for aa in range(0,len(fig.get_axes())):
        fig.get_axes()[aa].set_ylim([minY,maxY])
    
    #Set y-axes ticks to 5 margin intervals.
    #Get neareast divisible 5s of max and min
    y1 = int(maxY - (maxY % 5))
    y2 = int(minY - (minY % 5))
    #Set values
    for ncol in range(0,ax.shape[1]):
        for nrow in range(0,ax.shape[0]):
            #Set ticks if on col 1
            if ncol == 0:
                ax[nrow,ncol].set_yticks(np.linspace(y2,y1,int(np.diff([y2,y1])/5 + 1)))
            else:
                ax[nrow,ncol].set_yticks(np.linspace(y2,y1,int(np.diff([y2,y1])/5 + 1)))
                ax[nrow,ncol].set_yticklabels([])
            
    #Set tight figure layout
    plt.tight_layout()
    plt.show()
    
    #Save figure
    plt.savefig('CompetitiveSims_AllTeams_Margins.pdf')
    plt.savefig('CompetitiveSims_AllTeams_Margins.png', format = 'png', dpi = 300)
    
    #Close figure
    plt.close()
    
    #Return to working directory
    os.chdir(currDir)
    
    #Close figure
    plt.close()
    
# %% Relative odds of missing outer vs. inner circle

def relOddsVis(df_relOdds, df_teamInfo, colourDict, saveDir = os.getcwd()):
    
    # Function to plot distributions of competitive sims for two teams
    #
    # Input:    df_relOdds - dataframe with relative odds data
    #           df_teamInfo - dataframe with team info
    #           colourDict - colour dictionary for team colours on plots
    #           saveDir - directory to save files in to
    
    #Get current directory to navigate back to
    currDir = os.getcwd()
    
    #Navigate to figures directory
    os.chdir(saveDir)
    
    #Settings for how much to subtract/add to x-point for datapoints
    nSquads = len(df_teamInfo)
    offset = np.linspace(-nSquads/2,nSquads/2,nSquads+1) / 10
    
    #Create figure
    fig, ax = plt.subplots(figsize=(8,5))
    
    #Plot the combined data
    
    #Plot all periods data
    #Get data values
    dataVals = df_relOdds.loc[(df_relOdds['period'] == 'all'),
                              ['mean','lower95','upper95']].to_numpy().flatten()
    #Plot point
    plt.plot(1+offset[0],dataVals[0],
             marker = 'o', color = 'k',
             markersize = 6, label = 'All Teams')
    #Plot line
    plt.plot([1+offset[0],1+offset[0]],[dataVals[1],dataVals[2]],
             color = 'k', linewidth = 2)
    
    #Plot standard period data
    #Get data values
    dataVals = df_relOdds.loc[(df_relOdds['period'] == 'standard'),
                              ['mean','lower95','upper95']].to_numpy().flatten()
    #Plot point
    plt.plot(3+offset[0],dataVals[0],
             marker = 's', color = 'k',
             markersize = 6)
    #Plot line
    plt.plot([3+offset[0],3+offset[0]],[dataVals[1],dataVals[2]],
             color = 'k', linewidth = 2)
    
    #Plot super period data
    #Get data values
    dataVals = df_relOdds.loc[(df_relOdds['period'] == 'super'),
                              ['mean','lower95','upper95']].to_numpy().flatten()
    #Plot point
    plt.plot(5+offset[0],dataVals[0],
             marker = 'd', color = 'k',
             markersize = 6)
    #Plot line
    plt.plot([5+offset[0],5+offset[0]],[dataVals[1],dataVals[2]],
             color = 'k', linewidth = 2)
    
    #Loop through teams
    for tt in range(len(df_teamInfo['squadId'])):
        
        #Set current squad name
        currSquadName = df_teamInfo['squadNickname'][tt]
        
        #Plot all periods data
        #Get data values
        dataVals = df_relOdds.loc[(df_relOdds['team'] == currSquadName) &
                                  (df_relOdds['period'] == 'all'),
                                  ['mean','lower95','upper95']].to_numpy().flatten()
        #Plot point
        plt.plot(1+offset[tt+1],dataVals[0],
                 marker = 'o', color = colourDict[currSquadName],
                 markersize = 6, label = currSquadName)
        #Plot line
        plt.plot([1+offset[tt+1],1+offset[tt+1]],[dataVals[1],dataVals[2]],
                 color = colourDict[currSquadName], linewidth = 2)
        
        #Plot standard period data
        #Get data values
        dataVals = df_relOdds.loc[(df_relOdds['team'] == currSquadName) &
                                  (df_relOdds['period'] == 'standard'),
                                  ['mean','lower95','upper95']].to_numpy().flatten()
        #Plot point
        plt.plot(3+offset[tt+1],dataVals[0],
                 marker = 's', color = colourDict[currSquadName],
                 markersize = 6)
        #Plot line
        plt.plot([3+offset[tt+1],3+offset[tt+1]],[dataVals[1],dataVals[2]],
                 color = colourDict[currSquadName], linewidth = 2)
        
        #Plot super period data
        #Get data values
        dataVals = df_relOdds.loc[(df_relOdds['team'] == currSquadName) &
                                  (df_relOdds['period'] == 'super'),
                                  ['mean','lower95','upper95']].to_numpy().flatten()
        #Plot point
        plt.plot(5+offset[tt+1],dataVals[0],
                 marker = 'd', color = colourDict[currSquadName],
                 markersize = 6)
        #Plot line
        plt.plot([5+offset[tt+1],5+offset[tt+1]],[dataVals[1],dataVals[2]],
                 color = colourDict[currSquadName], linewidth = 2)
        
    #Add horizontal line at 2:1 value
    ax.axhline(y = 2, linestyle = '--', linewidth = 1,
               color = 'grey', zorder = 0)
    
    #Set X-ticks and labels
    ax.set_xticks([1,3,5])
    ax.set_xticklabels(['All Match', 'Standard Period', 'Super Shot Period'])
    
    #Set Y-axis limits and label
    ax.set_ylim([0,ax.get_ylim()[1]])
    ax.set_ylabel('Relative Odds of Missing from Outer vs. Inner Circle')
    
    #Set legend
    plt.legend(ncol = 3)
    
    #Tight layout
    plt.tight_layout()
    
    #Save figure
    plt.savefig('RelativeOdds_OuterInner_AllTeams.pdf')
    plt.savefig('RelativeOdds_OuterInner_AllTeams.png', format = 'png', dpi = 300)
    
    #Return to working directory
    os.chdir(currDir)
    
    #Close figure
    plt.close()
    
# %% Relative odds of missing outer vs. inner circle for defenses

def relOddsDefVis(df_relOddsDef, df_teamInfo, colourDict, saveDir = os.getcwd()):
    
    # Function to plot distributions of competitive sims for two teams
    #
    # Input:    df_relOddDefs - dataframe with relative odds defensive data
    #           df_teamInfo - dataframe with team info
    #           colourDict - colour dictionary for team colours on plots
    #           saveDir - directory to save files in to
    
    #Get current directory to navigate back to
    currDir = os.getcwd()
    
    #Navigate to figures directory
    os.chdir(saveDir)
    
    #Settings for how much to subtract/add to x-point for datapoints
    nSquads = len(df_teamInfo)
    offset = np.linspace(-nSquads/2,nSquads/2,nSquads) / 10
    
    #Create figure
    fig, ax = plt.subplots(figsize=(8,5))
    
    #Loop through teams
    for tt in range(len(df_teamInfo['squadId'])):
        
        #Set current squad name
        currSquadName = df_teamInfo['squadNickname'][tt]
        
        #Plot all periods data
        #Get data values
        dataVals = df_relOddsDef.loc[(df_relOddsDef['team'] == currSquadName) &
                                     (df_relOddsDef['period'] == 'all'),
                                     ['mean','lower95','upper95']].to_numpy().flatten()
        #Plot point
        plt.plot(1+offset[tt],dataVals[0],
                 marker = 'o', color = colourDict[currSquadName],
                 markersize = 6, label = currSquadName)
        #Plot line
        plt.plot([1+offset[tt],1+offset[tt]],[dataVals[1],dataVals[2]],
                 color = colourDict[currSquadName], linewidth = 2)
        
        #Plot standard period data
        #Get data values
        dataVals = df_relOddsDef.loc[(df_relOddsDef['team'] == currSquadName) &
                                     (df_relOddsDef['period'] == 'standard'),
                                     ['mean','lower95','upper95']].to_numpy().flatten()
        #Plot point
        plt.plot(3+offset[tt],dataVals[0],
                 marker = 's', color = colourDict[currSquadName],
                 markersize = 6)
        #Plot line
        plt.plot([3+offset[tt],3+offset[tt]],[dataVals[1],dataVals[2]],
                 color = colourDict[currSquadName], linewidth = 2)
        
        #Plot super period data
        #Get data values
        dataVals = df_relOddsDef.loc[(df_relOddsDef['team'] == currSquadName) &
                                      (df_relOddsDef['period'] == 'super'),
                                      ['mean','lower95','upper95']].to_numpy().flatten()
        #Plot point
        plt.plot(5+offset[tt],dataVals[0],
                 marker = 'd', color = colourDict[currSquadName],
                 markersize = 6)
        #Plot line
        plt.plot([5+offset[tt],5+offset[tt]],[dataVals[1],dataVals[2]],
                 color = colourDict[currSquadName], linewidth = 2)
        
    #Add horizontal line at 2:1 value
    ax.axhline(y = 2, linestyle = '--', linewidth = 1,
               color = 'grey', zorder = 0)
    
    #Set X-ticks and labels
    ax.set_xticks([1,3,5])
    ax.set_xticklabels(['All Match', 'Standard Period', 'Super Shot Period'])
    
    #Set Y-axis limits and label
    ax.set_ylim([0,ax.get_ylim()[1]])
    ax.set_ylabel('Relative Odds of Opp. Missing from Outer vs. Inner Circle')
    
    #Set legend
    plt.legend(ncol = 2)
    
    #Tight layout
    plt.tight_layout()
    
    #Save figure
    plt.savefig('RelativeOddsDef_OuterInner_AllTeams.pdf')
    plt.savefig('RelativeOddsDef_OuterInner_AllTeams.png', format = 'png', dpi = 300)
    
    #Return to working directory
    os.chdir(currDir)
    
    #Close figure
    plt.close()
