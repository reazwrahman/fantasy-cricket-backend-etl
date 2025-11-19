#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 11:04:29 2022

@author: Reaz
"""


# python includes
#import requests
#from bs4 import BeautifulSoup
import pandas as pd 
#import re
#import numpy as np 

SQUAD_SUMMARY_KEYS=['Batting','Bowling','Fielding','Total']


## Project Includes 
try: ## for outside of flask project usecases
    from FantasyPointsCalculator.ScoreCardGenerator.BattingScoreCardGenerator import BattingScoreCard 
    from FantasyPointsCalculator.ScoreCardGenerator.BowlingScoreCardGenerator import BowlingScoreCard 
    from FantasyPointsCalculator.ScoreCardGenerator.FieldingScoreCardGenerator import FieldingScoreCard

    from FantasyPointsCalculator.FantasyBattingPointsGenerator import FantasyBattingPoints 
    from FantasyPointsCalculator.FantasyBowlingPointsGenerator import FantasyBowlingPoints
    from FantasyPointsCalculator.FantasyFieldingPointsGenerator import FantasyFieldingPoints
    
except ModuleNotFoundError: ## for inside of flask project environemnt 
    from .FantasyPointsCalculator.ScoreCardGenerator.BattingScoreCardGenerator import BattingScoreCard 
    from .FantasyPointsCalculator.ScoreCardGenerator.BowlingScoreCardGenerator import BowlingScoreCard 
    from .FantasyPointsCalculator.ScoreCardGenerator.FieldingScoreCardGenerator import FieldingScoreCard

    from .FantasyPointsCalculator.FantasyBattingPointsGenerator import FantasyBattingPoints 
    from .FantasyPointsCalculator.FantasyBowlingPointsGenerator import FantasyBowlingPoints
    from .FantasyPointsCalculator.FantasyFieldingPointsGenerator import FantasyFieldingPoints

''' 
user_inputs_dict=
{  
 score_card_url: 'abc.com',  
 squad:[{id: 12, name: 'kane batter'},...],   
 points_per_run: 1, 
 points_per_wicket: 20, 
 }  

output format: 
    Name    Batting     Bowling     Fielding   Total
    
    on the website we can display batting, bowling and fielding dfs separately as well, with view details breakdown button
'''
class FantasyPointsForFullSquad(object): 
    def __init__(self,user_inputs_dict): 
        self.parameters_dict=user_inputs_dict  
        
        ## get all the scorecards
        self.batting_scorecard=BattingScoreCard(self.parameters_dict['score_card_url'])
        self.bowling_scorecard=BowlingScoreCard(self.parameters_dict['score_card_url']) 
        self.fielding_scorecard=FieldingScoreCard(self.parameters_dict['score_card_url']) 
        
        ## calculate all the fantasy points
        self.batting_object=FantasyBattingPoints(self.batting_scorecard.GetBattingDf(),  
                                                    self.parameters_dict['squad'], 
                                                    points_per_run=self.parameters_dict['points_per_run']) 
        
        self.bowling_object=FantasyBowlingPoints(self.bowling_scorecard.GetBowlingDf(),  
                                                    self.parameters_dict['squad'], 
                                                    points_per_wicket=self.parameters_dict['points_per_wicket'])
        
        
        self.fielding_object=FantasyFieldingPoints(self.fielding_scorecard.GetFieldingDf(),  
                                                    self.parameters_dict['squad'])
        

        self.batting_df = self.batting_object.__GenerateFantasyPointsDf__() 
        self.bowling_df = self.bowling_object.__GenerateFantasyPointsDf__() 
        self.fielding_df = self.fielding_object.__GenerateFantasyPointsDf__() 
        
    
    def GetBattingDf(self):  
        return self.batting_df

    
    def GetBowlingDf(self):  
        return self.bowling_df

   
    def GetFieldingDf(self):  
        return self.fielding_df 
    
    
    def __AddZeroPointsPlayers__(self,final_dict):    
        contribution_areas= SQUAD_SUMMARY_KEYS
        for each in self.parameters_dict['squad']: 
            if each not in final_dict:  
                final_dict[each]={}
                for each_key in list(contribution_areas): 
                    final_dict[each][each_key]=0.0 
        return final_dict
        
    
    def GetFullSquadDict(self): 
        batting=self.batting_df
        bowling=self.bowling_df  
        fielding=self.fielding_df  
        
        all_dfs=[batting,bowling,fielding]
        df_keys=SQUAD_SUMMARY_KEYS
        
        final_dict={} 
        
        for i in range (len(all_dfs)):
            for j in range (len(all_dfs[i])):  
                if all_dfs[i].Name[j] not in final_dict: 
                    final_dict[all_dfs[i].Name[j]]={} 
                
                for k in range (len(df_keys)):  
                    if k == i: 
                        final_dict[all_dfs[i].Name[j]][df_keys[k]]=all_dfs[i].total_points[j] 
                    else: 
                        if df_keys[k] not in final_dict[all_dfs[i].Name[j]]: 
                            final_dict[all_dfs[i].Name[j]][df_keys[k]]=0.0
        
              
        for each in final_dict: 
            final_dict[each][SQUAD_SUMMARY_KEYS[3]]=sum([final_dict[each][SQUAD_SUMMARY_KEYS[0]], 
                                    final_dict[each][SQUAD_SUMMARY_KEYS[1]], 
                                    final_dict[each][SQUAD_SUMMARY_KEYS[2]]])
                    
        
        ## add all the non contributing players as 0 points
        final_dict=self.__AddZeroPointsPlayers__(final_dict)
        

        return final_dict  
    
    
    def GetFullSquadDf(self): 
        final_dict=self.GetFullSquadDict() 
        final_df_columns = ['Name','Batting','Bowling','Fielding','Total'] 
        records = [] 
        
        for each in final_dict:     
            new_record = [each,
                        final_dict[each]['Batting'], final_dict[each]['Bowling'], 
                        final_dict[each]['Fielding'],
                        final_dict[each]['Total']] 
            records.append(new_record) 
            
        final_df = pd.DataFrame(records, columns = final_df_columns)    
        return final_df 
    
    
    def GetTotalFantasyPoints(self): 
        return sum(self.GetFullSquadDf()['Total']) 
    
    
    @staticmethod 
    def GetDfHeadingsList(df): 
        return (list(df.columns)) 
    
    @staticmethod 
    def GetDfRowsList(df): 
        rows=[]
        for i in range(len(df)): 
            rows.append(list(df.loc[i]))
        return rows  
    
    @staticmethod 
    def CheckScorecardLinkValidity(score_url): 
        try:    
            scorecard_generator=BattingScoreCard(score_url)  
            batting_scorecard=scorecard_generator.GetBattingDf() 
            if len(batting_scorecard)>0:
                return True  
            else: 
                return False
        except: 
            return False
        
                  
def test():    

    from FantasyPointsCalculator.SquadGenerator.ListOfAllPlayers import AllPlayers 
    score_url = 'https://www.espncricinfo.com/series/pakistan-in-australia-2023-24-1375835/australia-vs-pakistan-2nd-test-1375843/full-scorecard'
    squad_url ='https://www.espncricinfo.com/series/pakistan-in-australia-2023-24-1375835/australia-vs-pakistan-2nd-test-1375843/match-squads'
    squad_generator = AllPlayers(squad_url)
    full_squad = squad_generator.GetFullSquad() 
    #print (full_squad)
    
    user_inputs_dict={ 
      'score_card_url': score_url,  
      'squad': full_squad,   
      'points_per_run': 1, 
      'points_per_wicket': 20, 
      }   
    
    test=FantasyPointsForFullSquad(user_inputs_dict) 
    
    #print (test.GetBattingDf())
    #print (test.GetTotalBattingPoints()) 
    print ('---------------------')
    '''print (test.GetBowlingDf())
    print (test.GetTotalBowlingPoints()) 
    print ('---------------------')
    print (test.GetFieldingDf())
    print (test.GetTotalFieldingPoints()) 
    
    print ('------------------') '''
    sorted_df = test.GetFullSquadDf().sort_values(by='Total', ascending=False)
    print (sorted_df)  
    #print(test.GetTotalFantasyPoints())  
    return sorted_df

    

if __name__=="__main__": 
    test()
