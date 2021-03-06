from pynput.keyboard import Key, Controller, Listener
import time
import argparse
import datetime
import os
import pandas
import json

df_log = pandas.DataFrame(columns=['Date/Local Time', 'Experiment Number', 'Client IP/Location',
    'Test Duration', 'Typing Speed (char/s)', 'Hops', 'Intermediate Hosts (Client->Server)', 'Filename'])
df_user = pandas.DataFrame(columns=['Time', 'Command'])
df_type = pandas.DataFrame(columns=['Time', 'Key Gaps', 'Command Gaps'])
start_count = 0
def on_press_start(key):
    global start_count
    start_count += 1
    if start_count == 2:
        print("Please press the Esc button so the recording will start.")
        start_count = 0

def on_release_start(key):
    if key == Key.esc:
        return False

command = ""
count = 0
def on_press(key):
    global command
    global count
    global prev
    global prev_key
    global df_type
    count += 1
    try:
        command += key.char
    except AttributeError:
        if key == Key.backspace:
            command = command[:len(command)-1]
        elif key == Key.space:
            command += " "
    if prev_key[0] == Key.enter or prev_key[0] == Key.ctrl:
        df_type = df_type.append({"Time" : time.time() - start_time, "Command Gaps" : time.time() - prev_key[1]}, ignore_index=True)
    else:
        df_type = df_type.append({"Time" : time.time() - start_time, 'Key Gaps' : time.time() - prev}, ignore_index=True)

def on_release(key):
    global command
    global df_user
    global prev
    global prev_key
    prev = time.time()
    if ("exit" in command or "logout" in command) and key == Key.enter:
        return False
    if key == Key.enter or key == Key.ctrl:
        df_user = df_user.append({'Time': time.time() - start_time, 'Command': command}, ignore_index=True)
        command = ""
    prev_key[0] = key
    prev_key[1] = time.time()

# Collect events until released
parser = argparse.ArgumentParser(description="Logs the activity of a human user for experimentation.")
# parser.add_argument("expNum", type=int, help="The experiment number being performed.")
parser.add_argument("client", help="The IP address and location of the client, in the following format: 0.0.0.0_Tokyo")
parser.add_argument("hops", type=int, help="The number of hops that the connection has to the server.")
parser.add_argument("--ih", "--inter", help="If a hacker, the intermediate hosts that are in chain.")
args = parser.parse_args()
# exp = args.expNum
client = args.client
hops = args.hops
ih = args.ih

with open("count.txt", 'r') as f:
    exp = int(f.read())
with open("count.txt", 'w') as f:
    f.write(str(exp + 1))
print("After you have logged into the server, please press the Esc button so the recording will start.")
with Listener(on_press=on_press_start,
            on_release=on_release_start) as listener:
    listener.join()
start_time = time.time()
print("Recording data started. Type any linux commands.")
print("Once you exit the server, the recording will stop.")
prev = time.time()
prev_key = [None, time.time()]
with Listener(on_press=on_press,
            on_release=on_release) as listener:
    listener.join()
elapsed = time.time() - start_time
print("The recording has stopped.")
filename1 = f"exp{exp}_{client.replace('.','_')}.csv"
filename2 = f"exp{exp}_{client.replace('.','_')}_type.csv"
df_user.to_csv(filename1, index=False)
df_type.to_csv(filename2, index=False)
log = [
    str(datetime.datetime.now()),
    exp,
    client,
    elapsed,
    count/elapsed,
    hops,
    ih,
    filename1
]
df_log.loc[len(df_log)] = log
if os.path.exists("human_user_activity_log.csv"):
    df_log.to_csv("human_user_activity_log.csv", mode='a', index=False, header=False)
else:
    df_log.to_csv("human_user_activity_log.csv", index=False)