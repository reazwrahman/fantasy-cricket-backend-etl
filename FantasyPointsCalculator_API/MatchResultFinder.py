import requests
from bs4 import BeautifulSoup

from .FantasyPointsCalculator.ScoreCardGenerator.requests_helper import make_request, validate_link

class MatchResultFinder(object): 
    def __init__(self, scorecard_link, team1, team2): 
        self.scorecard_link = scorecard_link  
        self.team1 = team1 
        self.team2 = team2
    
    def __ExtractPage__(self):
        # create a BeautifulSoup object to parse the HTML content
        soup = make_request(self.scorecard_link)
        
        # find the match result element
        won_by = list(soup.find_all(lambda tag: tag.name == 'span' and ('won by' in tag.text)))    
        drawn = list(soup.find_all(lambda tag: tag.name == 'span' and ('Match drawn' in tag.text))) 
        tied = list(soup.find_all(lambda tag: tag.name == 'span' and ('Match tied' in tag.text)))

        match_results = won_by + drawn + tied
        return match_results 
    
    def FindMatchResult(self):
        match_results = self.__ExtractPage__()

        if len(match_results) == 0: 
            return None  


        for i in range (len(match_results)): 
            curr_result = str(match_results[i]).lower() 
            if self.team1.lower() in curr_result:   
                return 'team1'  
            if self.team2.lower() in curr_result: 
                return 'team2' 
            
            ## uncomment it later if conflicts can be avoided
            #elif (i == len(match_results)-1) and ('drawn' in match_results[i] or 'tied' in match_results[i]): 
            #    return 'draw' 
        
        return 'unknown'