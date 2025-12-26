from datetime import datetime
from pytz import timezone

from FantasyPointsCalculator_API.MatchResultFinder import MatchResultFinder
from PlayerStatsTracker import PlayerStatsTracker 
from DynamoAccess import DynamoAccess 
from Ranker import Ranker 

class DbUpdater(object): 
    def __init__(self, match_id, use_dynamo:bool = True, scorecard_url = None, team1 = None, team2 = None):
        self.match_id = match_id
        self.match_result_finder = None
        self.dynamo_access = None

        if use_dynamo:
            self.__initialize_with_dynamo()
        else:
            if scorecard_url and team1 and team2:
                self.__initialize_light(scorecard_url, team1, team2)
            else:
                raise Exception("Initialize light must know scorecard and teams")


    def __initialize_with_dynamo(self):
        self.dynamo_access = DynamoAccess()

        ## find match result
        scorecard_info = self.dynamo_access.GetScorecardInfo(self.match_id) 
        scorecard_url = scorecard_info['scorecard_link'] 
        team_names = self.dynamo_access.GetTeamNames(self.match_id) 
        self.match_result_finder = MatchResultFinder(scorecard_url, team_names[0], team_names[1])  
        self.match_result = self.dynamo_access.GetMatchResult(self.match_id)


    def __initialize_light(self, scorecard_url, team1, team2):
        self.match_result_finder = MatchResultFinder(scorecard_url, team1, team2)
        self.match_result = 'unknown'

    def __find_match_result(self):
        if self.match_result == 'unknown':
            try:
                match_result = self.match_result_finder.FindMatchResult()
                if match_result:
                    self.match_result = match_result
            except:
                print("DbUpdater::__Initialize__ failed to extract match result, something went wrong with webscraping")

    def __update_player_stats(self):
        ## update player stats
        self.stats = PlayerStatsTracker(self.match_id)
        self.batting_points = self.stats.GetBattingPoints()
        self.bowling_points = self.stats.GetBowlingPoints()
        self.fielding_points = self.stats.GetFieldingPoints()
        self.summary_points = self.stats.GetSummaryPoints()

    def generate_record(self):
        '''
           map batting/bowling/fielding/summary/total
        '''
        if self.match_result == 'unknown':
            self.__find_match_result()

        self.__update_player_stats()

        self.records = {'match_id': self.match_id,
                   'batting_points': self.batting_points,
                   'bowling_points': self.bowling_points,
                   'fielding_points': self.fielding_points,
                   'summary_points': self.summary_points,
                   'match_result': self.match_result
                   }
        return self.records

    def add_ranking_record(self):
        ## do fantasy rankings
        self.ranker = Ranker(self.match_id, self.summary_points, self.match_result)
        self.player_ranks = self.ranker.RankUsers()
        self.records['fantasy_ranks'] = self.player_ranks
        self.records['last_updated'] = self.GetCurrentTimeInUtc()

        return self.records


    def UpdateDataInDynamo(self):
        '''
        upload record to dynamo
        '''
        if not self.dynamo_access:
            self.dynamo_access = DynamoAccess()
        self.dynamo_access.UpdateAllPoints(self.records)

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

    ## condition1
    if len(scorecard_link) <= 5: 
        result = False  
    
    return result

def handle(event, context):  
    match_id = event['match_id']  
    print(f'got match id {match_id}') 
    if CheckLambdaPreConditions(match_id):
        db_updater = DbUpdater(match_id)
        db_updater.generate_record()
        db_updater.add_ranking_record()
        db_updater.UpdateDataInDynamo()
        return 'dynamo updated'
    
    return 'scorecard not available yet'


if __name__ == "__main__": 
    handle({'match_id':'1455614'},{})
