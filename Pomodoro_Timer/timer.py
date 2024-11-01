import time
from datetime import datetime

work_time = 25
short_break = 5

def start_timer(session_type):
    print('Pomodoro Timer started!')
    if session_type == work_time:
        print(f'Starting work session for {work_time} minutes.')
        time.sleep(work_time * 60)
        print('Work session ended.')
    elif session_type == short_break:
        print(f'Starting short break for {short_break} minutes.')
        time.sleep(short_break * 60)
        print('Short break ended.')

if __name__ == '__main__':
    start_timer(work_time)
    start_timer(short_break)
    print('Pomodoro Timer finished!')
