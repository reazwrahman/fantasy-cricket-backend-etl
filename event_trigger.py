from datetime import datetime
import hashlib
import time

from FantasyPointsCalculator_API.FantasyPointsCalculator.ScoreCardGenerator.requests_helper import *
from LambdaHandler import handle


def scrape_url(scorecard_url):
    try:
        if validate_link(scorecard_url):
            bs = make_request(scorecard_url)
            table_body = bs.find_all('tbody')
        return table_body
    except Exception as ex:
        print(f"ran into issues while scraping {ex}")
        raise ex

def hash_scorecard(scorecard_url):
    # deterministic serialization: join bytes of each tbody in order
    table_bodies = scrape_url(scorecard_url)
    content = b"".join(t.encode("utf-8") for t in table_bodies)
    return hashlib.sha256(content).hexdigest()


scorecard_url:str = input("Scorecard URL: ")
match_id:str = input("Match ID: ")
start_time:int = int(input('Start time in UNIX: ')) # in unix
duration:int = int(input('Duration in hours: '))

end_time = start_time + (duration * 3600) # in unix

readable_start_time = datetime.fromtimestamp(start_time)
readable_end_time = datetime.fromtimestamp(end_time)

print(f'start time = {readable_start_time}')
print(f'end time = {readable_end_time}')


previous_hash = None

while True:
    print('============================================')
    current_time = int(time.time())
    if current_time >= end_time:
        print(f'End time reached: {readable_end_time}, terminating event trigger')
        break
    elif current_time >= start_time:
        current_hash = hash_scorecard(scorecard_url)
        if current_hash != previous_hash:
            print("change detected in scorecard, will proceed to update leaderboard")
            previous_hash = current_hash
            try:
                handle({'match_id':match_id},{})
                print("Updated leaderboard")
            except Exception as e:
                print(e)
        else:
            print('no change detected in scorecard, no updates will occur')

    time.sleep(10) # wait n seconds between scrapings