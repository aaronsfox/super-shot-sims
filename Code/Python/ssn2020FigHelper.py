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

