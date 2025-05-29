from datetime import datetime
from pytz import timezone

from FantasyPointsCalculator_API.MatchResultFinder import MatchResultFinder
from PlayerStatsTracker import PlayerStatsTracker 
from DynamoAccess import DynamoAccess 
from Ranker import Ranker 

class DbUpdater(object): 
    def __init__(self, match_id):  
        self.match_id = match_id     
        self.__Initialize__()   
    
    def __Initialize__(self):   
        self.dynamo_access = DynamoAccess()

        ## find match result
        scorecard_info = self.dynamo_access.GetScorecardInfo(self.match_id) 
        scorecard_url = scorecard_info['scorecard_link'] 
        team_names = self.dynamo_access.GetTeamNames(self.match_id) 
        self.match_result_finder = MatchResultFinder(scorecard_url, team_names[0], team_names[1])  
        self.match_result = self.dynamo_access.GetMatchResult(self.match_id)
        if self.match_result == 'unknown': 
            try:
                match_result = self.match_result_finder.FindMatchResult() 
                if match_result:
                    self.match_result = match_result
            except: 
                print("DbUpdater::__Initialize__ failed to extract match result, something went wrong with webscraping")

        ## update player stats
        self.stats = PlayerStatsTracker(self.match_id) 
        self.batting_points = self.stats.GetBattingPoints() 
        self.bowling_points = self.stats.GetBowlingPoints() 
        self.fielding_points = self.stats.GetFieldingPoints() 
        self.summary_points = self.stats.GetSummaryPoints()  

        ## do fantasy rankings 
        self.ranker = Ranker(self.match_id, self.summary_points, self.match_result) 
        self.player_ranks = self.ranker.RankUsers()  


    def UpdateDataInDynamo(self): 
        ''' 
            map batting/bowling/fielding/summary/total 
            upload each to dynamo 
        '''   
        records = { 'match_id': self.match_id,   
                    'fantasy_ranks': self.player_ranks,
                    'batting_points': self.batting_points, 
                    'bowling_points': self.bowling_points, 
                    'fielding_points': self.fielding_points, 
                    'summary_points' : self.summary_points, 
                    'last_updated' : self.GetCurrentTimeInUtc(),  
                    'match_result' : self.match_result
                  } 
        self.dynamo_access.UpdateAllPoints(records) 
    
    def GetCurrentTimeInUtc(self):  
        # Get the current time in UTC
        now_utc = datetime.utcnow()

        # Format the time as a string and return it 
        time_str = now_utc.strftime('%Y-%m-%d %H:%M:%S UTC') 
        return time_str

             
        

def CheckLambdaPreConditions(match_id):  
    result = True
    dynamo_access = DynamoAccess() 
    scorecard_details = dynamo_access.GetScorecardInfo(match_id) 
    scorecard_link = scorecard_details['scorecard_link']   
    match_result = dynamo_access.GetMatchResult(match_id)

    ## condition1
    if len(scorecard_link) <= 5: 
        result = False  
    
    return result

def handle(event, context):  
    match_id = event['match_id']  
    print(f'got match id {match_id}') 
    if CheckLambdaPreConditions(match_id):
        db_updater = DbUpdater(match_id) 
        db_updater.UpdateDataInDynamo()
        return 'dynamo updated'
    
    return 'scorecard not available yet'


if __name__ == "__main__": 
    handle({'match_id':'1355723'},{})
