from datetime import datetime
import time
import copy

from LambdaHandler import DbUpdater


scorecard_url:str = input("Scorecard URL: ").strip()
match_id:str = input("Match ID: ").strip()
team1:str = input("Team 1: ").strip()
team2: str = input("Team 2: ").strip()
start_time:int = int(input('Start time in UNIX: ')) # in unix
duration:int = int(input('Duration in hours: '))

end_time = start_time + (duration * 3600) # in unix

readable_start_time = datetime.fromtimestamp(start_time)
readable_end_time = datetime.fromtimestamp(end_time)

print(f'start time = {readable_start_time}')
print(f'end time = {readable_end_time}')

db_updater = DbUpdater(match_id, False, scorecard_url, team1, team2)
previous_record = None

while True:
    print('============================================')
    current_time = int(time.time())
    if current_time >= end_time:
        print(f'End time reached: {readable_end_time}, terminating event trigger')
        break
    elif current_time >= start_time:
        current_record = copy.deepcopy(db_updater.generate_record())
        if current_record != previous_record:
            print("change detected in scorecard, will proceed to update leaderboard")
            previous_record = current_record
            try:
                dynamo_record:dict = db_updater.add_ranking_record()
                db_updater.UpdateDataInDynamo()
                print("Updated leaderboard")
            except Exception as e:
                print(e)
        else:
            print('no change detected in scorecard, no updates will occur')

    time.sleep(10) # wait n seconds between scrapings