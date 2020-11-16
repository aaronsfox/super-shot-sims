# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 20:05:01 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This helper script contains a series of functions that are used for
getting data from the Super Netball 2020 season files.
    
"""

# %% Import packages

import pandas as pd
pd.options.mode.chained_assignment = None #turn of pandas chained warnings
import json
import re
import numpy as np

# %% getMatchData

def getMatchData(jsonFileList = None, df_squadLists = None,
                 exportDict = True, exportDf = True,
                 exportTeamData = True, exportPlayerData = True,
                 exportMatchData = True, exportScoreData = True,
                 exportLineUpData = True, exportPlayerStatsData = True,
                 exportTeamStatsData = True):
    
    # Function for importing the Champion Data .json files for SSN 2020
    #
    # Input:    jsonFileList - list of .json files to import
    #           df_squadLists - dataframe of players in each squad for look-up
    #           exportDict - boolean flag whether to return to data dictionaries
    #           exportDf - boolean flag whether to export the dataframes
    #           exportTeamData - boolean flag whether to export the team data
    #           exportPlayerData - boolean flag whether to export the player data 
    #           exportMatchData - boolean flag whether to export the match data
    #           exportScoreData - boolean flag whether to export the score flow data
    #           exportLineUpData - boolean flag whether to export the line up data

    #Create blank dictionaries to store data in

    #Match info
    matchInfo = {'id': [], 'homeSquadId': [], 'awaySquadId': [],
                 'startTime': [], 'roundNo': [], 'matchNo': [],
                 'venueId': [], 'venueName': [], 'periodSeconds': []}
    
    #Team info
    teamInfo = {'squadCode': [], 'squadId': [],
                'squadName': [], 'squadNickname': []}
    
    #Player info
    playerInfo = {'playerId': [], 'displayName': [],
                  'firstName': [], 'surname': [],
                  'shortDisplayName': [], 'squadId': []}
    
    #Score flow data
    scoreFlowData = {'roundNo': [], 'matchNo': [], 'homeScore': [], 'awayScore': [],
                     'preShotAhead': [], 'postShotAhead': [],
                     'preShotMargin': [], 'postShotMargin': [],
                     'period': [], 'periodSeconds': [], 'periodCategory': [], 'matchSeconds': [],
                     'playerId': [],'squadId': [], 'scoreName': [], 'shotOutcome': [], 'scorePoints': [],
                     'distanceCode': [], 'positionCode': [], 'shotCircle': []}
    
    #Substitution data
    substitutionData = {'roundNo': [], 'matchNo': [],
                        'period': [], 'periodSeconds': [], 'matchSeconds': [],
                        'playerId': [], 'squadId': [], 'fromPos': [], 'toPos': []}
    
    #Line-up data
    lineUpData = {'lineUpId': [], 'lineUpName': [], 'matchNo': [], 'roundNo': [], 'squadId': [],
                  'matchSecondsStart': [], 'matchSecondsEnd': [], 'durationSeconds': [],
                  'pointsFor': [], 'pointsAgainst': [], 'plusMinus': []}
    
    #Individual player data
    individualLineUpData = {'playerId': [], 'playerName':[], 'squadId': [], 'playerPosition': [],
                            'roundNo': [], 'matchNo': [],
                            'matchSecondsStart': [], 'matchSecondsEnd': [], 'durationSeconds': [],
                            'pointsFor': [], 'pointsAgainst': [], 'plusMinus': []}
    
    #Individual player stats
    playerStatsData = {'playerId': [], 'playerName': [], 'squadId': [],
                       'roundNo': [], 'matchNo': [], 'matchId': [], 'period' : [],
                       'attempt_from_zone1': [], 'attempt_from_zone2': [],
                       'badHands': [], 'badPasses': [], 'blocked': [], 'blocks': [],
                       'breaks': [], 'centrePassReceives': [], 'centrePassToGoalPerc': [],
                       'contactPenalties': [], 'deflectionWithGain': [], 'deflectionWithNoGain': [],
                       'deflections': [], 'disposals': [], 'feedWithAttempt': [], 'feeds': [],
                       'gain': [], 'gainToGoalPerc': [], 'generalPlayTurnovers': [],
                       'goalAssists': [], 'goalAttempts': [], 'goalMisses': [],
                       'goal_from_zone1': [], 'goal_from_zone2': [], 'goals': [],
                       'interceptPassThrown': [], 'intercepts': [], 'missedGoalTurnover': [],
                       'netPoints': [], 'obstructionPenalties': [], 'offsides': [],
                       'passes': [], 'penalties': [], 'pickups': [], 'possessionChanges': [],
                       'possessions': [], 'rebounds': [], 'tossUpWin': []}
    
    #Team stats
    teamStatsData = {'squadId': [], 'roundNo': [], 'matchNo': [], 'matchId': [], 'period' : [],
                     'attempt_from_zone1': [], 'attempt_from_zone2': [],
                     'badHands': [], 'badPasses': [], 'blocked': [], 'blocks': [],
                     'breaks': [], 'centrePassReceives': [], 'centrePassToGoalPerc': [],
                     'contactPenalties': [], 'deflectionPossessionGain': [], 'deflectionWithGain': [], 'deflectionWithNoGain': [],
                     'deflections': [], 'disposals': [], 'feedWithAttempt': [], 'feeds': [],
                     'gain': [], 'gainToGoalPerc': [], 'generalPlayTurnovers': [],
                     'goalAssists': [], 'goalAttempts': [], 'goalMisses': [],
                     'goal_from_zone1': [], 'goal_from_zone2': [], 'goals': [],
                     'goalsFromCentrePass': [], 'goalsFromGain': [], 'goalsFromTurnovers': [],
                     'interceptPassThrown': [], 'intercepts': [], 'missedShotConversion': [],
                     'netPoints': [], 'obstructionPenalties': [], 'offsides': [],
                     'passes': [], 'penalties': [], 'pickups': [], 'possessionChanges': [],
                     'possessions': [], 'rebounds': [], 'tossUpWin': []}
    
    #Create a variable for starting positions
    starterPositions = ['GS','GA','WA','C','WD','GD','GK']
    
    #Sort json file list alpha-numerically so that round 1 remains first
    def sortedNicely(l):
        """ Sorts the given iterable in the way that is expected.
        Required arguments:
        l -- The iterable to be sorted. """
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key = alphanum_key)
    jsonFileList = sortedNicely(jsonFileList)
    
    #Loop through file list and extract data
    for ff in range(0,len(jsonFileList)):
        
        #Load the .json data
        with open(jsonFileList[ff]) as json_file:
            data = json.load(json_file)
            
        #Extract match details
        matchInfo['id'].append(data['matchInfo']['matchId'][0])
        matchInfo['homeSquadId'].append(data['matchInfo']['homeSquadId'][0])
        matchInfo['awaySquadId'].append(data['matchInfo']['awaySquadId'][0])
        matchInfo['startTime'].append(data['matchInfo']['localStartTime'][0])
        matchInfo['roundNo'].append(data['matchInfo']['roundNumber'][0])
        matchInfo['matchNo'].append(data['matchInfo']['matchNumber'][0])
        matchInfo['venueId'].append(data['matchInfo']['venueId'][0])
        matchInfo['venueName'].append(data['matchInfo']['venueName'][0])
        qtrSeconds = list()
        for qq in range(0,4):
            qtrSeconds.append(data['periodInfo']['qtr'][qq]['periodSeconds'][0])
        matchInfo['periodSeconds'].append(qtrSeconds)
    
        #If round 1, extract the league team details to lists
        if data['matchInfo']['roundNumber'][0] == 1:
            #Append the two teams details
            teamInfo['squadCode'].append(data['teamInfo']['team'][0]['squadCode'][0])
            teamInfo['squadId'].append(data['teamInfo']['team'][0]['squadId'][0])
            teamInfo['squadName'].append(data['teamInfo']['team'][0]['squadName'][0])
            teamInfo['squadNickname'].append(data['teamInfo']['team'][0]['squadNickname'][0])
            teamInfo['squadCode'].append(data['teamInfo']['team'][1]['squadCode'][0])
            teamInfo['squadId'].append(data['teamInfo']['team'][1]['squadId'][0])
            teamInfo['squadName'].append(data['teamInfo']['team'][1]['squadName'][0])
            teamInfo['squadNickname'].append(data['teamInfo']['team'][1]['squadNickname'][0])
        
        #Extract player details from each team     
        for pp in range(0,len(data['playerInfo']['player'])):
            #First, check if the player ID is in the current id list
            currPlayerId = playerInfo['playerId']
            if data['playerInfo']['player'][pp]['playerId'][0] not in currPlayerId:
                #Grab the new player details
                playerInfo['playerId'].append(data['playerInfo']['player'][pp]['playerId'][0])
                playerInfo['displayName'].append(data['playerInfo']['player'][pp]['displayName'][0])
                playerInfo['firstName'].append(data['playerInfo']['player'][pp]['firstname'][0])
                playerInfo['surname'].append(data['playerInfo']['player'][pp]['surname'][0])
                playerInfo['shortDisplayName'].append(data['playerInfo']['player'][pp]['shortDisplayName'][0])
                #Find which squad they belong to in the squad list dataframe
                currPlayerSquad = df_squadLists.loc[(df_squadLists['displayName'] == \
                                                     data['playerInfo']['player'][pp]['displayName'][0]),\
                                                    ].reset_index()['squadNickname'][0]
                #Get the squad ID from the team info and append to players info
                currPlayerSquadId = teamInfo['squadId'][teamInfo['squadNickname'].index(currPlayerSquad)]
                playerInfo['squadId'].append(currPlayerSquadId)
                
        #Extract score flow data
        for ss in range(0,len(data['scoreFlow']['score'])):
            scoreFlowData['roundNo'].append(data['matchInfo']['roundNumber'][0])
            scoreFlowData['matchNo'].append(data['matchInfo']['matchNumber'][0])
            scoreFlowData['period'].append(data['scoreFlow']['score'][ss]['period'][0])
            scoreFlowData['periodSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0])
            if data['scoreFlow']['score'][ss]['periodSeconds'][0] > 600:
                scoreFlowData['periodCategory'].append('twoPoint')
            else:
                scoreFlowData['periodCategory'].append('standard')
            if data['scoreFlow']['score'][ss]['period'][0] == 1:
                #Just use period seconds
                scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0])
            elif data['scoreFlow']['score'][ss]['period'][0] == 2:
                #Add the preceding period seconds
                scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0])
            elif data['scoreFlow']['score'][ss]['period'][0] == 3:
                #Add the preceding period seconds
                scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1])
            elif data['scoreFlow']['score'][ss]['period'][0] == 4:
                #Add the preceding period seconds
                scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1] + matchInfo['periodSeconds'][ff][2])
            scoreFlowData['playerId'].append(data['scoreFlow']['score'][ss]['playerId'][0])
            scoreFlowData['squadId'].append(data['scoreFlow']['score'][ss]['squadId'][0])
            scoreFlowData['scoreName'].append(data['scoreFlow']['score'][ss]['scoreName'][0])
            scoreFlowData['scorePoints'].append(data['scoreFlow']['score'][ss]['scorepoints'][0])
            scoreFlowData['distanceCode'].append(data['scoreFlow']['score'][ss]['distanceCode'][0])
            scoreFlowData['positionCode'].append(data['scoreFlow']['score'][ss]['positionCode'][0])
            ##### TODO: check and document this better from Mitch's twitter sample image
            #Get current distance and position code in one variable
            currCode = [data['scoreFlow']['score'][ss]['positionCode'][0],
                        data['scoreFlow']['score'][ss]['distanceCode'][0]]
            if currCode == [2,3] or currCode == [2,1] or currCode == [1,1] or currCode == [0,1] or currCode == [0,3]:
                scoreFlowData['shotCircle'].append('outerCircle')
            else:
                scoreFlowData['shotCircle'].append('innerCircle')
            if data['scoreFlow']['score'][ss]['scorepoints'][0] == 0:
                scoreFlowData['shotOutcome'].append(False)
            else:
                scoreFlowData['shotOutcome'].append(True)
            #Get game score and margin
            if ss == 0:
                #Set starting details
                currHomeScore = 0
                currAwayScore = 0
                preShotMargin = 0
                preShotAhead = np.nan
            else:
                #Get curr length of score flow data and subsequent index to look up
                nInd = len(scoreFlowData['preShotAhead']) - 1
                #Set starting details
                currHomeScore = scoreFlowData['homeScore'][nInd]
                currAwayScore = scoreFlowData['awayScore'][nInd]
                preShotMargin = scoreFlowData['postShotMargin'][nInd]
                preShotAhead = scoreFlowData['postShotAhead'][nInd]            
            #Check who scored and add to tally
            if data['scoreFlow']['score'][ss]['squadId'][0] == matchInfo['homeSquadId'][ff]:
                #Add to home score
                currHomeScore = currHomeScore + data['scoreFlow']['score'][ss]['scorepoints'][0]
            elif data['scoreFlow']['score'][ss]['squadId'][0] == matchInfo['awaySquadId'][ff]:
                #Add to away score
                currAwayScore = currAwayScore + data['scoreFlow']['score'][ss]['scorepoints'][0]
            #Check who is now in front
            if currHomeScore > currAwayScore:
                postShotAhead = matchInfo['homeSquadId'][ff]
            elif currAwayScore > currHomeScore:
                postShotAhead = matchInfo['awaySquadId'][ff]
            else:
                postShotAhead = np.nan
            #Calculate margin (home score up = positive)
            postShotMargin = currHomeScore - currAwayScore
            #Append to dictionary
            scoreFlowData['homeScore'].append(currHomeScore)
            scoreFlowData['awayScore'].append(currAwayScore)
            scoreFlowData['preShotAhead'].append(preShotAhead)
            scoreFlowData['postShotAhead'].append(postShotAhead)
            scoreFlowData['preShotMargin'].append(preShotMargin)
            scoreFlowData['postShotMargin'].append(postShotMargin)
            
        #Extract substitution data
        for ss in range(0,len(data['playerSubs']['player'])):
            #Get current round and match number from match data
            substitutionData['roundNo'].append(matchInfo['roundNo'][ff])
            substitutionData['matchNo'].append(matchInfo['matchNo'][ff])
            #Get period and period seconds
            substitutionData['period'].append(data['playerSubs']['player'][ss]['period'][0])
            substitutionData['periodSeconds'].append(data['playerSubs']['player'][ss]['periodSeconds'][0])
            #Convert to match seconds based on match info and period number
            if data['playerSubs']['player'][ss]['period'][0] == 1:
                #Just use the period seconds
                substitutionData['matchSeconds'].append(data['playerSubs']['player'][ss]['periodSeconds'][0])
            elif data['playerSubs']['player'][ss]['period'][0] == 2:
                #Add the matches period 1 seconds to the total
                newSeconds = data['playerSubs']['player'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0]
                #Add to data dictionary
                substitutionData['matchSeconds'].append(newSeconds)
            elif data['playerSubs']['player'][ss]['period'][0] == 3:
                #Add the matches period 1 & 2 seconds to the total
                newSeconds = data['playerSubs']['player'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1]
                #Add to data dictionary
                substitutionData['matchSeconds'].append(newSeconds)
            elif data['playerSubs']['player'][ss]['period'][0] == 4:
                #Add the matches period 1, 2 & 3 seconds to the total
                newSeconds = data['playerSubs']['player'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1] + matchInfo['periodSeconds'][ff][2]
                #Add to data dictionary
                substitutionData['matchSeconds'].append(newSeconds)
            #Get player and squad ID's
            substitutionData['playerId'].append(data['playerSubs']['player'][ss]['playerId'][0])
            substitutionData['squadId'].append(data['playerSubs']['player'][ss]['squadId'][0])
            #Get substitution positions
            substitutionData['fromPos'].append(data['playerSubs']['player'][ss]['fromPos'][0])
            substitutionData['toPos'].append(data['playerSubs']['player'][ss]['toPos'][0])
                    
        #Extract lineup data
        
        ##### TODO: consider adding durations for within one/two-point periods
        
        #Get the squad ID and name order
        if data['teamInfo']['team'][0]['squadId'][0] < data['teamInfo']['team'][1]['squadId'][0]:
            lineUpSquadId1 = data['teamInfo']['team'][0]['squadId'][0]
            lineUpSquadName1 = teamInfo['squadNickname'][teamInfo['squadId'].index(lineUpSquadId1)]
            lineUpSquadId2 = data['teamInfo']['team'][1]['squadId'][0]
            lineUpSquadName2 = teamInfo['squadNickname'][teamInfo['squadId'].index(lineUpSquadId2)]
        else:
            lineUpSquadId1 = data['teamInfo']['team'][1]['squadId'][0]
            lineUpSquadName1 = teamInfo['squadNickname'][teamInfo['squadId'].index(lineUpSquadId1)]
            lineUpSquadId2 = data['teamInfo']['team'][0]['squadId'][0]
            lineUpSquadName2 = teamInfo['squadNickname'][teamInfo['squadId'].index(lineUpSquadId2)]
        
        #Get the starting lineups
        
        #Find the first player in the player list that matches the first squad ID.
        #This should theoretically always be at index 0
        #Set starting search parameters
        playerNo = 0
        startIndSquad1 = []
        #Loop through players
        while not startIndSquad1:
            #Get current player name
            currPlayerName = data['playerInfo']['player'][playerNo]['displayName'][0]
            #Get this players squad ID
            currPlayerSquadId = playerInfo['squadId'][playerInfo['displayName'].index(currPlayerName)]
            #Check if it matches the first squad ID and append if so. This should exit the loop
            if currPlayerSquadId == lineUpSquadId1:
                startIndSquad1.append(playerNo)
            else:
                #Add to the search index for player no
                playerNo = playerNo + 1
                
        #Find the first player in the player list that matches the second squad ID.
        #Set starting search parameters
        playerNo = 0
        startIndSquad2 = []
        #Loop through players
        while not startIndSquad2:
            #Get current player name
            currPlayerName = data['playerInfo']['player'][playerNo]['displayName'][0]
            #Get this players squad ID
            currPlayerSquadId = playerInfo['squadId'][playerInfo['displayName'].index(currPlayerName)]
            #Check if it matches the first squad ID and append if so. This should exit the loop
            if currPlayerSquadId == lineUpSquadId2:
                startIndSquad2.append(playerNo)
            else:
                #Add to the search index for player no
                playerNo = playerNo + 1
                
        #Convert the current substitution data dictionary to a dataframe to use
        #Only extract the subs for the current round and match number
        df_subChecker = pd.DataFrame.from_dict(substitutionData).loc[(pd.DataFrame.from_dict(substitutionData)['roundNo'] == matchInfo['roundNo'][ff]) &
                                                                     (pd.DataFrame.from_dict(substitutionData)['matchNo'] == matchInfo['matchNo'][ff]),]
        
        #Convert the current score flow data dictionary to a dataframe to use
        #Only extract the scores for the current round and match number
        df_scoreChecker = pd.DataFrame.from_dict(scoreFlowData).loc[(pd.DataFrame.from_dict(scoreFlowData)['roundNo'] == matchInfo['roundNo'][ff]) &
                                                                    (pd.DataFrame.from_dict(scoreFlowData)['matchNo'] == matchInfo['matchNo'][ff]),]
        
        #Extract each squads lineups
        for nn in range(0,2):
            
            #Set current squad details within loop
            if nn == 0:
                currStartIndSquad = startIndSquad1
                currLineUpSquadId = lineUpSquadId1
                
            else:
                currStartIndSquad = startIndSquad2
                currLineUpSquadId = lineUpSquadId2
        
            #Get the starting lineup
            startLineUpId = list()
            startLineUpName = list()
            for pp in range(currStartIndSquad[0],currStartIndSquad[0]+7):
                startLineUpId.append(data['playerInfo']['player'][pp]['playerId'][0])
                startLineUpName.append(data['playerInfo']['player'][pp]['displayName'][0])
            
            #Get subs for the current squad
            df_subCheckerTeam = df_subChecker.loc[(df_subChecker['squadId'] == currLineUpSquadId),]  
            df_subCheckerTeam.reset_index(drop=True, inplace=True)
            
            #First check if dataframe is empty if a team makes no subs
            if len(df_subCheckerTeam) == 0:
                #No subs made by this team
                #This lineup stays in the whole game and can be treated that way
                #Set lineup ID and names
                lineUpData['lineUpId'].append(startLineUpId)
                lineUpData['lineUpName'].append(startLineUpName)
                lineUpData['squadId'].append(currLineUpSquadId)
                #Set match and round numbers
                lineUpData['roundNo'].append(matchInfo['roundNo'][ff])
                lineUpData['matchNo'].append(matchInfo['matchNo'][ff])
                #Set match seconds start and end to 0 and match length
                lineUpData['matchSecondsStart'].append(0)
                lineUpData['matchSecondsEnd'].append(sum(matchInfo['periodSeconds'][ff]))
                lineUpData['durationSeconds'].append(sum(matchInfo['periodSeconds'][ff]))
                #Set points for the lineup
                #Simply across the whole match
                lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId),
                                                                   ['scorePoints']].sum()['scorePoints'])
                #Set points against the lineup
                #Simply across the whole match
                lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId),
                                                                       ['scorePoints']].sum()['scorePoints'])
                #Calculate plus/minus
                plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId),
                                                ['scorePoints']].sum()['scorePoints'] - \
                    df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId),
                                        ['scorePoints']].sum()['scorePoints']
                lineUpData['plusMinus'].append(plusMinus)
            else:
                #Set the first lineup data based on the first substituion made by the team
                #Set lineup ID and names
                lineUpData['lineUpId'].append(startLineUpId)
                lineUpData['lineUpName'].append(startLineUpName)
                lineUpData['squadId'].append(currLineUpSquadId)
                #Set match and round numbers
                lineUpData['roundNo'].append(matchInfo['roundNo'][ff])
                lineUpData['matchNo'].append(matchInfo['matchNo'][ff])
                #Set match seconds start and end to 0 and the first substitution
                lineUpData['matchSecondsStart'].append(0)
                lineUpData['matchSecondsEnd'].append(df_subCheckerTeam['matchSeconds'][0])
                lineUpData['durationSeconds'].append(df_subCheckerTeam['matchSeconds'][0])
                #Set points for the lineup
                #Search in score flow for less than the substitution end time
                lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                                   (df_scoreChecker['matchSeconds'] <= df_subCheckerTeam['matchSeconds'][0]),
                                                                   ['scorePoints']].sum()['scorePoints'])
                #Set points against the lineup
                #Simply across the whole match
                lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                                                   (df_scoreChecker['matchSeconds'] <= df_subCheckerTeam['matchSeconds'][0]),
                                                                   ['scorePoints']].sum()['scorePoints'])
                #Calculate plus/minus
                plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                (df_scoreChecker['matchSeconds'] <= df_subCheckerTeam['matchSeconds'][0]),
                                                ['scorePoints']].sum()['scorePoints'] - \
                    df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                        (df_scoreChecker['matchSeconds'] <= df_subCheckerTeam['matchSeconds'][0]),
                                        ['scorePoints']].sum()['scorePoints']
                lineUpData['plusMinus'].append(plusMinus)
                
                #Loop through substitutions, identify lineups and calculate data
                
                #Identify the substitutions that are grouped together
                uniqueSubs = df_subCheckerTeam['matchSeconds'].unique()
                #Loop through unique subs
                for uu in range(0,len(uniqueSubs)):
        
                    #Get substitutions for current time point
                    #Only take the ones that shift into a lineup position
                    df_currSubs = df_subCheckerTeam.loc[(df_subCheckerTeam['matchSeconds'] == uniqueSubs[uu]) &
                                                        (df_subCheckerTeam['toPos'] != 'S'),]
                    df_currSubs.reset_index(drop=True, inplace=True)
                    
                    #If current subs dataframe is empty, this is an error or even the
                    #random situation of a player being sent off (i.e. GIANTS match
                    #in round 5). This needs to be accounted for by pulling the position
                    #from the lineup
                    if len(df_currSubs) == 0:
                        
                        #Extract the player going to the bench in isolation
                        df_currSubs = df_subCheckerTeam.loc[(df_subCheckerTeam['matchSeconds'] == uniqueSubs[uu]) &
                                                            (df_subCheckerTeam['toPos'] == 'S'),]    
                        df_currSubs.reset_index(drop=True, inplace=True)
                        
                        #Create a new lineup variable to edit from the previous lineup
                        newLineUpId = list()
                        newLineUpName = list()
                        for pp in range(0,7):
                            newLineUpId.append(lineUpData['lineUpId'][len(lineUpData['lineUpId'])-1][pp])
                            newLineUpName.append(lineUpData['lineUpName'][len(lineUpData['lineUpName'])-1][pp])
                            
                        #Loop through substitutions and replace the lineup with an
                        #empty value where appropriate
                        for cc in range(0,len(df_currSubs)):
                            #Check for position and replace appropriately
                            if df_currSubs['fromPos'][cc] == 'GS':
                                #Replace player ID
                                newLineUpId[0] = []
                                #Replace player name
                                newLineUpName[0] = []
                            elif df_currSubs['fromPos'][cc] == 'GA':
                                #Replace player ID
                                newLineUpId[1] = []
                                #Replace player name
                                newLineUpName[1] = []
                            elif df_currSubs['fromPos'][cc] == 'WA':
                                #Replace player ID
                                newLineUpId[2] = []
                                #Replace player name
                                newLineUpName[2] = []
                            elif df_currSubs['fromPos'][cc] == 'C':
                                #Replace player ID
                                newLineUpId[3] = []
                                #Replace player name
                                newLineUpName[3] = []
                            elif df_currSubs['fromPos'][cc] == 'WD':
                                #Replace player ID
                                newLineUpId[4] = []
                                #Replace player name
                                newLineUpName[4] = []
                            elif df_currSubs['fromPos'][cc] == 'GD':
                                #Replace player ID
                                newLineUpId[5] = []
                                #Replace player name
                                newLineUpName[5] = []
                            elif df_currSubs['fromPos'][cc] == 'GK':
                                #Replace player ID
                                newLineUpId[6] = []
                                #Replace player name
                                newLineUpName[6] = []
                        
                    else:
                    
                        #Create a new lineup variable to edit from the previous lineup
                        newLineUpId = list()
                        newLineUpName = list()
                        for pp in range(0,7):
                            newLineUpId.append(lineUpData['lineUpId'][len(lineUpData['lineUpId'])-1][pp])
                            newLineUpName.append(lineUpData['lineUpName'][len(lineUpData['lineUpName'])-1][pp])
                        
                        #Loop through substitutions and replace the lineup
                        for cc in range(0,len(df_currSubs)):
                            #Check for position and replace appropriately
                            if df_currSubs['toPos'][cc] == 'GS':
                                #Replace player ID
                                newLineUpId[0] = df_currSubs['playerId'][cc]
                                #Get and replace player name
                                newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[0])]
                                newLineUpName[0] = newPlayerName
                            elif df_currSubs['toPos'][cc] == 'GA':
                                #Replace player ID
                                newLineUpId[1] = df_currSubs['playerId'][cc]
                                #Get and replace player name
                                newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[1])]
                                newLineUpName[1] = newPlayerName
                            elif df_currSubs['toPos'][cc] == 'WA':
                                #Replace player ID
                                newLineUpId[2] = df_currSubs['playerId'][cc]
                                #Get and replace player name
                                newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[2])]
                                newLineUpName[2] = newPlayerName
                            elif df_currSubs['toPos'][cc] == 'C':
                                #Replace player ID
                                newLineUpId[3] = df_currSubs['playerId'][cc]
                                #Get and replace player name
                                newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[3])]
                                newLineUpName[3] = newPlayerName
                            elif df_currSubs['toPos'][cc] == 'WD':
                                #Replace player ID
                                newLineUpId[4] = df_currSubs['playerId'][cc]
                                #Get and replace player name
                                newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[4])]
                                newLineUpName[4] = newPlayerName
                            elif df_currSubs['toPos'][cc] == 'GD':
                                #Replace player ID
                                newLineUpId[5] = df_currSubs['playerId'][cc]
                                #Get and replace player name
                                newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[5])]
                                newLineUpName[5] = newPlayerName
                            elif df_currSubs['toPos'][cc] == 'GK':
                                #Replace player ID
                                newLineUpId[6] = df_currSubs['playerId'][cc]
                                #Get and replace player name
                                newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[6])]
                                newLineUpName[6] = newPlayerName
                        
                    #Calculate and set data in lineup structure
                    #Set lineup ID and names
                    lineUpData['lineUpId'].append(newLineUpId)
                    lineUpData['lineUpName'].append(newLineUpName)
                    lineUpData['squadId'].append(currLineUpSquadId)
                    #Set match and round numbers
                    lineUpData['roundNo'].append(matchInfo['roundNo'][ff])
                    lineUpData['matchNo'].append(matchInfo['matchNo'][ff])
                    #Set match seconds start and end to 0 and the first substitution
                    lineUpData['matchSecondsStart'].append(uniqueSubs[uu]+1)
                    #Match seconds end will be next sub or match end when last sub
                    if uu < len(uniqueSubs)-1:
                        lineUpData['matchSecondsEnd'].append(uniqueSubs[uu+1])
                        lineUpData['durationSeconds'].append(uniqueSubs[uu+1] - uniqueSubs[uu])
                    else:
                        lineUpData['matchSecondsEnd'].append(sum(matchInfo['periodSeconds'][ff]))
                        lineUpData['durationSeconds'].append(sum(matchInfo['periodSeconds'][ff]) - uniqueSubs[uu])
                    #Search in score flow for less than the substitution end time
                    #If last sub need to only search for greater than the seconds time
                    if uu < len(uniqueSubs)-1:
                        #Set points for the lineup
                        lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                                       (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1) & 
                                                                       (df_scoreChecker['matchSeconds'] <= uniqueSubs[uu+1]),
                                                                       ['scorePoints']].sum()['scorePoints'])
                        #Set points against the lineup
                        lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                                                       (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1) & 
                                                                       (df_scoreChecker['matchSeconds'] <= uniqueSubs[uu+1]),
                                                                       ['scorePoints']].sum()['scorePoints'])
                        #Calculate plus/minus
                        plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                        (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1) & 
                                                        (df_scoreChecker['matchSeconds'] <= uniqueSubs[uu+1]),
                                                        ['scorePoints']].sum()['scorePoints'] - \
                            df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                                (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1) & 
                                                (df_scoreChecker['matchSeconds'] <= uniqueSubs[uu+1]),
                                                ['scorePoints']].sum()['scorePoints']
                        lineUpData['plusMinus'].append(plusMinus)
                    else:
                        #Set points for the lineup
                        lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                                       (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                                       ['scorePoints']].sum()['scorePoints'])
                        #Set points against the lineup
                        lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                                                       (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                                       ['scorePoints']].sum()['scorePoints'])
                        #Calculate plus/minus
                        plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                        (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                        ['scorePoints']].sum()['scorePoints'] - \
                            df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                                (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                ['scorePoints']].sum()['scorePoints']
                        lineUpData['plusMinus'].append(plusMinus)
                        
        #Extract individual player 'lineup' data
        #Loop through two teams
        for nn in range(0,2):
            
            #Set current squad details within loop
            if nn == 0:
                currStartIndSquad = startIndSquad1
                if currStartIndSquad < startIndSquad2:
                    currEndIndSquad = startIndSquad2
                else:
                    currEndIndSquad = [len(data['playerInfo']['player'])]                
            else:
                currStartIndSquad = startIndSquad2
                if currStartIndSquad < startIndSquad1:
                    currEndIndSquad = startIndSquad1
                else:
                    currEndIndSquad = [len(data['playerInfo']['player'])]    
        
            #Start with first squad players
            for pp in range(currStartIndSquad[0],currEndIndSquad[0]):
                
                #Extract current player info
                currPlayerId = data['playerInfo']['player'][pp]['playerId'][0]
                currPlayerName = data['playerInfo']['player'][pp]['displayName'][0]
                currPlayerSquadId = playerInfo['squadId'][playerInfo['playerId'].index(currPlayerId)]
                
                #Check if player is in starting lineup
                if pp <= (currStartIndSquad[0] + 6):
                    isStarter = True
                else:
                    isStarter = False
                
                #Grab the substitution data that contains this players id
                df_subCheckerPlayer = df_subChecker.loc[(df_subChecker['playerId'] == currPlayerId),]
                df_subCheckerPlayer.reset_index(drop=True, inplace=True)
                
                #Check combinations of starter vs. no starter and number of subs
                if len(df_subCheckerPlayer) == 0:
                    
                    #If the player started the game and had no subs, they played the whole game
                    #If they didn't then we won't add them as they didn't play
                    if isStarter:
                    
                        #Player started and played the whole game
                        #Set player/squad ID and names
                        individualLineUpData['playerId'].append(currPlayerId)
                        individualLineUpData['playerName'].append(currPlayerName)
                        individualLineUpData['playerPosition'].append(starterPositions[pp - currStartIndSquad[0]])
                        individualLineUpData['squadId'].append(currPlayerSquadId)
                        #Set match and round numbers
                        individualLineUpData['roundNo'].append(matchInfo['roundNo'][ff])
                        individualLineUpData['matchNo'].append(matchInfo['matchNo'][ff])
                        #Set match seconds start and end to 0 and match length
                        individualLineUpData['matchSecondsStart'].append(0)
                        individualLineUpData['matchSecondsEnd'].append(sum(matchInfo['periodSeconds'][ff]))
                        individualLineUpData['durationSeconds'].append(sum(matchInfo['periodSeconds'][ff]))
                        #Set points for the lineup
                        #Simply across the whole match
                        individualLineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId),
                                                                           ['scorePoints']].sum()['scorePoints'])
                        #Set points against the lineup
                        #Simply across the whole match
                        individualLineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId),
                                                                               ['scorePoints']].sum()['scorePoints'])
                        #Calculate plus/minus
                        plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId),
                                                        ['scorePoints']].sum()['scorePoints'] - \
                            df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId),
                                                ['scorePoints']].sum()['scorePoints']
                        individualLineUpData['plusMinus'].append(plusMinus)
                    
                else:
                    
                    #Player incurred some form of substitution and game time
                    
                    #Loop through substitutions and address accordingly
                    for ss in range(0,len(df_subCheckerPlayer)+1):
                        
                        #Set player/squad ID and names
                        individualLineUpData['playerId'].append(currPlayerId)
                        individualLineUpData['playerName'].append(currPlayerName)
                        individualLineUpData['squadId'].append(currPlayerSquadId)
                        #Set match and round numbers
                        individualLineUpData['roundNo'].append(matchInfo['roundNo'][ff])
                        individualLineUpData['matchNo'].append(matchInfo['matchNo'][ff])
                        
                        #Check substitution number and code accordingly
                        if ss == 0:
                            #Starters first substitution involvement                    
                            #Set starting position
                            if isStarter:
                                individualLineUpData['playerPosition'].append(starterPositions[pp - currStartIndSquad[0]])
                            else:
                                individualLineUpData['playerPosition'].append('S')                        
                            #Set match start, end and duration
                            individualLineUpData['matchSecondsStart'].append(0)
                            individualLineUpData['durationSeconds'].append(df_subCheckerPlayer['matchSeconds'][ss])
                            individualLineUpData['matchSecondsEnd'].append(df_subCheckerPlayer['matchSeconds'][ss])
                            #Set points for and against the lineup
                            individualLineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                                                         (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                                                         ['scorePoints']].sum()['scorePoints'])
                            individualLineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                                                         (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                                                         ['scorePoints']].sum()['scorePoints'])
                            #Calculate plus/minus
                            plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                            (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                            ['scorePoints']].sum()['scorePoints'] - \
                                df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                    (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                    ['scorePoints']].sum()['scorePoints']
                            individualLineUpData['plusMinus'].append(plusMinus)    
                            
                        elif ss == len(df_subCheckerPlayer):
                            
                            #Starters last substituion involvement
                            #Set starting position
                            individualLineUpData['playerPosition'].append(df_subCheckerPlayer['toPos'][ss-1])
                            #Set match start and duration
                            individualLineUpData['matchSecondsStart'].append(df_subCheckerPlayer['matchSeconds'][ss-1]+1)
                            individualLineUpData['durationSeconds'].append(sum(matchInfo['periodSeconds'][ff]) - df_subCheckerPlayer['matchSeconds'][ss-1]+1)
                            individualLineUpData['matchSecondsEnd'].append(sum(matchInfo['periodSeconds'][ff]))
                            #Set points for and against the lineup
                            individualLineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                                                         (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                                                         (df_scoreChecker['matchSeconds'] <= sum(matchInfo['periodSeconds'][ff])),
                                                                                         ['scorePoints']].sum()['scorePoints'])
                            individualLineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                                                         (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                                                         (df_scoreChecker['matchSeconds'] <= sum(matchInfo['periodSeconds'][ff])),
                                                                                         ['scorePoints']].sum()['scorePoints'])
                            #Calculate plus/minus
                            plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                            (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                            (df_scoreChecker['matchSeconds'] <= sum(matchInfo['periodSeconds'][ff])),
                                                            ['scorePoints']].sum()['scorePoints'] - \
                                df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                    (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                    (df_scoreChecker['matchSeconds'] <= sum(matchInfo['periodSeconds'][ff])),
                                                    ['scorePoints']].sum()['scorePoints']
                            individualLineUpData['plusMinus'].append(plusMinus)
                            
                        else:
                            
                            #Substitutions throughout match
                            #Set substituting position
                            individualLineUpData['playerPosition'].append(df_subCheckerPlayer['toPos'][ss-1])
                            #Set match start, end and duration
                            individualLineUpData['matchSecondsStart'].append(df_subCheckerPlayer['matchSeconds'][ss-1]+1)
                            individualLineUpData['durationSeconds'].append(df_subCheckerPlayer['matchSeconds'][ss] - df_subCheckerPlayer['matchSeconds'][ss-1]+1)
                            individualLineUpData['matchSecondsEnd'].append(df_subCheckerPlayer['matchSeconds'][ss])
                            #Set points for and against the lineup
                            individualLineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                                                         (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                                                         (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                                                         ['scorePoints']].sum()['scorePoints'])
                            individualLineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                                                         (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                                                         (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                                                         ['scorePoints']].sum()['scorePoints'])                
                            #Calculate plus/minus
                            plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                            (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]+1) & 
                                                            (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                            ['scorePoints']].sum()['scorePoints'] - \
                                df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                    (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]+1) & 
                                                    (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                    ['scorePoints']].sum()['scorePoints']
                            individualLineUpData['plusMinus'].append(plusMinus)
                    
        #Extract game statistic data
        
        #### TODO: why did I copy-paste rather than put in loop???????
        
        #Loop through the player by period list
        for pp in range(0,len(data['playerPeriodStats']['player'])):
            
            #Get player, round, match details
            
            #Extract statistics from current player and period
            playerStatsData['playerId'].append(data['playerPeriodStats']['player'][pp]['playerId'][0])
            playerStatsData['playerName'].append(playerInfo['displayName'][playerInfo['playerId'].index(data['playerPeriodStats']['player'][pp]['playerId'][0])])
            playerStatsData['squadId'].append(data['playerPeriodStats']['player'][pp]['squadId'][0])
            playerStatsData['matchNo'].append(matchInfo['matchNo'][ff])
            playerStatsData['matchId'].append(matchInfo['id'][ff])
            playerStatsData['roundNo'].append(matchInfo['roundNo'][ff])
            playerStatsData['period'].append(data['playerPeriodStats']['player'][pp]['period'][0])
            
            #Extract statistical data
            playerStatsData['attempt_from_zone1'].append(data['playerPeriodStats']['player'][pp]['attempt_from_zone1'][0])
            playerStatsData['attempt_from_zone2'].append(data['playerPeriodStats']['player'][pp]['attempt_from_zone2'][0])
            playerStatsData['badHands'].append(data['playerPeriodStats']['player'][pp]['badHands'][0])
            playerStatsData['badPasses'].append(data['playerPeriodStats']['player'][pp]['badPasses'][0])
            playerStatsData['blocked'].append(data['playerPeriodStats']['player'][pp]['blocked'][0])
            playerStatsData['blocks'].append(data['playerPeriodStats']['player'][pp]['blocks'][0])
            playerStatsData['breaks'].append(data['playerPeriodStats']['player'][pp]['breaks'][0])
            playerStatsData['centrePassReceives'].append(data['playerPeriodStats']['player'][pp]['centrePassReceives'][0])
            playerStatsData['centrePassToGoalPerc'].append(data['playerPeriodStats']['player'][pp]['centrePassToGoalPerc'][0])
            playerStatsData['contactPenalties'].append(data['playerPeriodStats']['player'][pp]['contactPenalties'][0])
            playerStatsData['deflectionWithGain'].append(data['playerPeriodStats']['player'][pp]['deflectionWithGain'][0])
            playerStatsData['deflectionWithNoGain'].append(data['playerPeriodStats']['player'][pp]['deflectionWithNoGain'][0])
            playerStatsData['deflections'].append(data['playerPeriodStats']['player'][pp]['deflections'][0])
            playerStatsData['disposals'].append(data['playerPeriodStats']['player'][pp]['disposals'][0])
            playerStatsData['feedWithAttempt'].append(data['playerPeriodStats']['player'][pp]['feedWithAttempt'][0])
            playerStatsData['feeds'].append(data['playerPeriodStats']['player'][pp]['feeds'][0])
            playerStatsData['gain'].append(data['playerPeriodStats']['player'][pp]['gain'][0])
            playerStatsData['gainToGoalPerc'].append(data['playerPeriodStats']['player'][pp]['gainToGoalPerc'][0])
            playerStatsData['generalPlayTurnovers'].append(data['playerPeriodStats']['player'][pp]['generalPlayTurnovers'][0])
            playerStatsData['goalAssists'].append(data['playerPeriodStats']['player'][pp]['goalAssists'][0])
            playerStatsData['goalAttempts'].append(data['playerPeriodStats']['player'][pp]['goalAttempts'][0])
            playerStatsData['goalMisses'].append(data['playerPeriodStats']['player'][pp]['goalMisses'][0])
            playerStatsData['goal_from_zone1'].append(data['playerPeriodStats']['player'][pp]['goal_from_zone1'][0])
            playerStatsData['goal_from_zone2'].append(data['playerPeriodStats']['player'][pp]['goal_from_zone2'][0])
            playerStatsData['goals'].append(data['playerPeriodStats']['player'][pp]['goals'][0])
            playerStatsData['interceptPassThrown'].append(data['playerPeriodStats']['player'][pp]['interceptPassThrown'][0])
            playerStatsData['intercepts'].append(data['playerPeriodStats']['player'][pp]['intercepts'][0])
            playerStatsData['missedGoalTurnover'].append(data['playerPeriodStats']['player'][pp]['missedGoalTurnover'][0])
            playerStatsData['netPoints'].append(data['playerPeriodStats']['player'][pp]['netPoints'][0])
            playerStatsData['obstructionPenalties'].append(data['playerPeriodStats']['player'][pp]['obstructionPenalties'][0])
            playerStatsData['offsides'].append(data['playerPeriodStats']['player'][pp]['offsides'][0])
            playerStatsData['passes'].append(data['playerPeriodStats']['player'][pp]['passes'][0])
            playerStatsData['penalties'].append(data['playerPeriodStats']['player'][pp]['penalties'][0])
            playerStatsData['pickups'].append(data['playerPeriodStats']['player'][pp]['pickups'][0])
            playerStatsData['possessionChanges'].append(data['playerPeriodStats']['player'][pp]['possessionChanges'][0])
            playerStatsData['possessions'].append(data['playerPeriodStats']['player'][pp]['possessions'][0])
            playerStatsData['rebounds'].append(data['playerPeriodStats']['player'][pp]['rebounds'][0])
            playerStatsData['tossUpWin'].append(data['playerPeriodStats']['player'][pp]['tossUpWin'][0])
    
        #Loop through team and period list
        for tt in range(0,len(data['teamPeriodStats']['team'])):
            
            #Get team, match and period details
            teamStatsData['squadId'].append(data['teamPeriodStats']['team'][tt]['squadId'][0])
            teamStatsData['matchNo'].append(matchInfo['matchNo'][ff])
            teamStatsData['matchId'].append(matchInfo['id'][ff])
            teamStatsData['roundNo'].append(matchInfo['roundNo'][ff])
            teamStatsData['period'].append(data['teamPeriodStats']['team'][tt]['period'][0])
            
            #Extract statistical data
            teamStatsData['attempt_from_zone1'].append(data['teamPeriodStats']['team'][tt]['attempt_from_zone1'][0])
            teamStatsData['attempt_from_zone2'].append(data['teamPeriodStats']['team'][tt]['attempt_from_zone2'][0])
            teamStatsData['badHands'].append(data['teamPeriodStats']['team'][tt]['badHands'][0])
            teamStatsData['badPasses'].append(data['teamPeriodStats']['team'][tt]['badPasses'][0])
            teamStatsData['blocked'].append(data['teamPeriodStats']['team'][tt]['blocked'][0])
            teamStatsData['blocks'].append(data['teamPeriodStats']['team'][tt]['blocks'][0])
            teamStatsData['breaks'].append(data['teamPeriodStats']['team'][tt]['breaks'][0])
            teamStatsData['centrePassReceives'].append(data['teamPeriodStats']['team'][tt]['centrePassReceives'][0])
            teamStatsData['centrePassToGoalPerc'].append(data['teamPeriodStats']['team'][tt]['centrePassToGoalPerc'][0])
            teamStatsData['contactPenalties'].append(data['teamPeriodStats']['team'][tt]['contactPenalties'][0])
            teamStatsData['deflectionPossessionGain'].append(data['teamPeriodStats']['team'][tt]['deflectionPossessionGain'][0])
            teamStatsData['deflectionWithGain'].append(data['teamPeriodStats']['team'][tt]['deflectionWithGain'][0])
            teamStatsData['deflectionWithNoGain'].append(data['teamPeriodStats']['team'][tt]['deflectionWithNoGain'][0])
            teamStatsData['deflections'].append(data['teamPeriodStats']['team'][tt]['deflections'][0])
            teamStatsData['disposals'].append(data['teamPeriodStats']['team'][tt]['disposals'][0])
            teamStatsData['feedWithAttempt'].append(data['teamPeriodStats']['team'][tt]['feedWithAttempt'][0])
            teamStatsData['feeds'].append(data['teamPeriodStats']['team'][tt]['feeds'][0])
            teamStatsData['gain'].append(data['teamPeriodStats']['team'][tt]['gain'][0])
            teamStatsData['gainToGoalPerc'].append(data['teamPeriodStats']['team'][tt]['gainToGoalPerc'][0])
            teamStatsData['generalPlayTurnovers'].append(data['teamPeriodStats']['team'][tt]['generalPlayTurnovers'][0])
            teamStatsData['goalAssists'].append(data['teamPeriodStats']['team'][tt]['goalAssists'][0])
            teamStatsData['goalAttempts'].append(data['teamPeriodStats']['team'][tt]['goalAttempts'][0])
            teamStatsData['goalMisses'].append(data['teamPeriodStats']['team'][tt]['goalMisses'][0])
            teamStatsData['goal_from_zone1'].append(data['teamPeriodStats']['team'][tt]['goal_from_zone1'][0])
            teamStatsData['goal_from_zone2'].append(data['teamPeriodStats']['team'][tt]['goal_from_zone2'][0])
            teamStatsData['goals'].append(data['teamPeriodStats']['team'][tt]['goals'][0])
            teamStatsData['goalsFromCentrePass'].append(data['teamPeriodStats']['team'][tt]['goalsFromCentrePass'][0])
            teamStatsData['goalsFromGain'].append(data['teamPeriodStats']['team'][tt]['goalsFromGain'][0])
            teamStatsData['goalsFromTurnovers'].append(data['teamPeriodStats']['team'][tt]['goalsFromTurnovers'][0])
            teamStatsData['interceptPassThrown'].append(data['teamPeriodStats']['team'][tt]['interceptPassThrown'][0])
            teamStatsData['intercepts'].append(data['teamPeriodStats']['team'][tt]['intercepts'][0])
            teamStatsData['missedShotConversion'].append(data['teamPeriodStats']['team'][tt]['missedShotConversion'][0])
            teamStatsData['netPoints'].append(data['teamPeriodStats']['team'][tt]['netPoints'][0])
            teamStatsData['obstructionPenalties'].append(data['teamPeriodStats']['team'][tt]['obstructionPenalties'][0])
            teamStatsData['offsides'].append(data['teamPeriodStats']['team'][tt]['offsides'][0])
            teamStatsData['passes'].append(data['teamPeriodStats']['team'][tt]['passes'][0])
            teamStatsData['penalties'].append(data['teamPeriodStats']['team'][tt]['penalties'][0])
            teamStatsData['pickups'].append(data['teamPeriodStats']['team'][tt]['pickups'][0])
            teamStatsData['possessionChanges'].append(data['teamPeriodStats']['team'][tt]['possessionChanges'][0])
            teamStatsData['possessions'].append(data['teamPeriodStats']['team'][tt]['possessions'][0])
            teamStatsData['rebounds'].append(data['teamPeriodStats']['team'][tt]['rebounds'][0])
            teamStatsData['tossUpWin'].append(data['teamPeriodStats']['team'][tt]['tossUpWin'][0])

    
    
    # #Summarise substitution data
    
    # #Convert to dataframe
    # df_substitutionData = pd.DataFrame.from_dict(substitutionData)
    
    # #Create a new column that converts substitution timing to be relative to
    # #the quarter in the match (i.e. 0-1, 1-2, 2-3, 3-4)
    # normSubTime = list()
    # for ss in range(0,len(df_substitutionData)):
        
    #     #Get appropriate match and round timing data
    #     roundBool = df_substitutionData['roundNo'][ss] == matchInfo['roundNo']
    #     matchBool = df_substitutionData['matchNo'][ss] == matchInfo['matchNo']
    #     bothBool = [a and b for a, b in zip(roundBool,matchBool)]
    #     bothBoolInd = bothBool.index(bothBool == True) - 1
    #     currPeriodSeconds = matchInfo['periodSeconds'][bothBoolInd]
        
    #     #Normalise current substitution data to period seconds
    #     #Get current period index
    #     periodInd = df_substitutionData['period'][ss]-1
    #     #Normalise to seconds and append (ensure adding quarter val too)
    #     normSubTime.append(df_substitutionData['periodSeconds'][ss] / currPeriodSeconds[periodInd] + periodInd)
        
    # #Append to dataframe
    # df_substitutionData['normSubTime'] = normSubTime
    
    # #Calculate some summary substitution statistics
    
    # #Get unique squad ID's from substitution data
    # squadIds = df_substitutionData['squadId'].unique()
    # df_teamInfo = pd.DataFrame.from_dict(teamInfo)

    # #Print heading
    # print('Total number of substitutions by teams:')
    
    # #Loop through squads
    # for tt in range(0,len(squadIds)):
        
    #     #Get the current squads total points
    #     totalSubs = len(df_substitutionData.loc[(df_substitutionData['squadId'] == squadIds[tt]) &
    #                                             (df_substitutionData['fromPos'] == 'S'),])
        
    #     #Get the total number of games played
    #     totalGames = len(df_substitutionData['roundNo'].unique())
        
    #     #Calculate subs per game
    #     perSubs = totalSubs/totalGames
        
    #     #Get the current team name
    #     currTeamName = df_teamInfo.squadName[df_teamInfo['squadId'] == squadIds[tt]].reset_index()['squadName'][0]
        
    #     #Print results
    #     print(currTeamName+': '+str(totalSubs)+' Total Subs ('+str(round(perSubs,2))+' per game)')
        
    # #Plot a histogram of normalised sub time to determine details of when they
    # #are occurring
    # from matplotlib import pyplot as plt
    # num_bins = 40
    # df_currSubs = df_substitutionData.loc[(df_substitutionData['fromPos'] == 'S')]
    # plt.hist(df_currSubs['normSubTime'], num_bins, facecolor='blue', alpha=0.5)
    # plt.show()
    
    # #Loop through squads and see if any differences
    # colourDict = {'Fever': '#00953b',
    #           'Firebirds': '#4b2c69',
    #           'GIANTS': '#f57921',
    #           'Lightning': '#fdb61c',
    #           'Magpies': '#494b4a',
    #           'Swifts': '#0082cd',
    #           'Thunderbirds': '#e54078',
    #           'Vixens': '#00a68e'}
    
    # for tt in range(0,len(squadIds)):    
        
    #     #Get current team name
    #     currTeamName = df_teamInfo.squadNickname[df_teamInfo['squadId'] == squadIds[tt]].reset_index()['squadNickname'][0]
    #     currColour = colourDict[currTeamName]
        
    #     #Plot histogram
    #     num_bins = 40
    #     plt.figure()
    #     df_currSubs = df_substitutionData.loc[(df_substitutionData['squadId'] == squadIds[tt]) &
    #                                           (df_substitutionData['fromPos'] == 'S')]
    #     plt.hist(df_currSubs['normSubTime'], num_bins, facecolor = currColour, alpha=0.5)
    #     plt.title(currTeamName)
    #     plt.show()
        
        
    
    
    
    
    
    #Export data
    
    #Set a dictionary to pack data in to
    exportData = dict()
    
    #Team info
    if exportTeamData is True:
        #Set to dataframe
        df_teamInfo = pd.DataFrame.from_dict(teamInfo)
        #Check and return data
        if exportDict is True:
            exportData['teamInfo'] = teamInfo
        if exportDf is True:
            exportData['df_teamInfo'] = df_teamInfo
        
    #Player info
    if exportPlayerData is True:
        #Set to dataframe
        df_playerInfo = pd.DataFrame.from_dict(playerInfo)
        #Check and return data
        if exportDict is True:
            exportData['playerInfo'] = playerInfo
        if exportDf is True:
            exportData['df_playerInfo'] =df_playerInfo
        
    #Match info
    if exportMatchData is True:
        #Set to dataframe
        df_matchInfo = pd.DataFrame.from_dict(matchInfo)
        #Check and return data
        if exportDict is True:
            exportData['matchInfo'] = matchInfo
        if exportDf is True:
            exportData['df_matchInfo'] = df_matchInfo
    
    #Score flow data
    if exportScoreData is True:
        #Set to dataframe
        df_scoreFlow = pd.DataFrame.from_dict(scoreFlowData)
        #Check and return data
        if exportDict is True:
            exportData['scoreFlowData'] = scoreFlowData
        if exportDf is True:
            exportData['df_scoreFlow'] = df_scoreFlow
    
    #Lineup data
    if exportLineUpData is True:
        #Set to dataframe
        df_lineUp = pd.DataFrame.from_dict(lineUpData)
        df_individualLineUp = pd.DataFrame.from_dict(individualLineUpData)
        #Check and return data
        if exportDict is True:
            exportData['lineUpData'] = lineUpData
            exportData['individualLineUpData'] = individualLineUpData
        if exportDf is True:
            exportData['df_lineUp'] = df_lineUp
            exportData['df_individualLineUp'] = df_individualLineUp
            
    #Player stats data
    if exportPlayerStatsData is True:
        #Set to dataframe
        df_playerStatsData = pd.DataFrame.from_dict(playerStatsData)
        #Check and return data
        if exportDict is True:
            exportData['playerStatsData'] = playerStatsData
        if exportDf is True:
            exportData['df_playerStatsData'] = df_playerStatsData
            
    #Team stats data
    if exportTeamStatsData is True:
        #Set to dataframe
        df_teamStatsData = pd.DataFrame.from_dict(teamStatsData)
        #Check and return data
        if exportDict is True:
            exportData['teamStatsData'] = teamStatsData
        if exportDf is True:
            exportData['df_teamStatsData'] = df_teamStatsData
    
    #Return data dictionary
    return exportData
    
    ##### TODO: other dataframes once extracted
    
# %%
    
    