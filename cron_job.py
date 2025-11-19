import time
from datetime import datetime, timedelta

from LambdaHandler import handle


match_id:str = input("Match ID: ")
start_time:int = int(input('Start time in UNIX: ')) # in unix
duration:int = int(input('Duration in hours: '))
update_interval = int(input('Update Interval in minutes: ')) * 60  # in seconds

end_time = start_time + (duration * 3600) # in unix

readable_start_time = datetime.fromtimestamp(start_time)
readable_end_time = datetime.fromtimestamp(end_time)

print(f'start time = {readable_start_time}')
print(f'end time = {readable_end_time}')

while True:
    print('============================================')
    current_time = int(time.time())
    if current_time >= end_time:
        print(f'End time reached: {readable_end_time}, terminating cron job')
        break
    elif current_time >= start_time:
        handle({'match_id':match_id},{})

    print(f'Next execution in {update_interval} seconds')
    time.sleep(update_interval)
