from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import random
import time
import threading
import os
import argparse
import Xlib.threaded
from concurrent import futures
import pandas
import datetime

"""
Creates several threads of normal users and/or attacking users to simulate concurrent user activity.

@version 1.0
@author Jerred Chen, Jonathan Loncanlale
Python 3.8.2
"""
class Node():
    def __init__(self, name, files=[], subf=[]):
        self.name = name
        self.files = files
        self.subf = subf

class DataFrame():
    def __init__(self):
        self.df = pandas.DataFrame(columns=['Date/Local Time', 'Experiment Number', 'IP/Location(s)',
            'Test Duration', 'Avg Typing Speed (char/s)', 'Hops', 'Filename'])
        self.lock = threading.Lock()
    def add(self, log):
        with self.lock():
            self.df.loc[len(self.df)] = log
    def to_csv(self):
        if os.path.exists("user_activity_log.csv"):
            self.df.to_csv("user_activity_log.csv", mode='a', index=False, header=False)
        else:
            self.df.to_csv("user_activity_log.csv", index=False)

class UserNum():
    def __init__(self):
        self.val = 0
        self.lock = threading.Lock()

    def update(self, newNum):
        with self.lock:
            oldval = self.val
            self.val = newNum
            return oldval

class TypeCommand():
    def __init__(self):
        self.lock = threading.Lock()

    def tab(self, times):
        keyboard.press(Key.ctrl_l)
        for i in range(0, times):
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
        keyboard.release(Key.ctrl_l)

    def type(self, command, currUser, count, typingSpeed):
        lines = []
        keyword = command
        nano = False
        pause = 0
        if command == "nano":
            nano = True
            with open('lines.txt', 'r') as fn:
                lines = fn.readlines()
            keyword = random.choice(lines).strip()
            if random.random() < 0.7:
                pause = random.randrange(len(keyword)//2, len(keyword))
        for i in range(0, len(keyword)):
            with self.lock:
                oldval = currUser.update(count)
                self.tab((count - oldval) % totalUsers)
                if nano and i == 0:
                    keyboard.type("nano")
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
                keyboard.type(keyword[i])
                if nano and i == len(keyword) - 1:
                    keyboard.press(Key.ctrl)
                    keyboard.press('x')
                    keyboard.release('x')
                    keyboard.release(Key.ctrl)
                    keyboard.type('n')
                elif i == len(keyword) - 1:
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
            time.sleep(random.betavariate(2, 8) * typingSpeed)
            if i == pause and command == "nano":
                time.sleep(3 * random.random() + 1)
        if command == "nano":
            return keyword[:keyword.find(':')]
            
    def UHlogin(self, currUser, count, ssh_cmd, pw):
        with self.lock:
            oldval = currUser.update(count)
            self.tab((count - oldval) % totalUsers)
            keyboard.type(ssh_cmd)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            time.sleep(2)
            keyboard.type(pw)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            
class NormalUser():

    def __init__(self, server, count, home):
        self.server = server.lower()
        if self.server == 'uh':
            credsList = []
            with open('secret.txt', 'r') as fn:
                for line in fn.readlines():
                    credsList.append(line.strip())
            creds = {'username': credsList[0], 'password': credsList[1]}
            self.ssh_cmd = f"ssh {creds['username']}@129.7.241.21"
            self.pw = creds['password']
        self.count = count
        self.commands = ['df', 'ls', 'lsblk', 'lscpu', 'mount', 'pwd', 'history', 'ss', f'mkdir Thread{self.count}', 
            'cal', 'cd', 'cd ..', 'nano', 'ls', 'cd', 'cd ..', 'pwd', f'mkdir Thread{self.count}', 'cat', 'cat']
        self.typingSpeed = (0.40 * random.random()) + 0.30
        self.tree = [home]

    def launch(self, currUser, typeCommand):
        global ip_location
        global exp
        global df
        df_user = pandas.DataFrame(columns=['Time', 'Command'])
        # Log into the server through SSH
        time.sleep(2)
        if self.server == 'uh':
            typeCommand.UHlogin(currUser, self.count, self.ssh_cmd, self.pw)
        else:
            typeCommand.type(f"ssh {self.server}", currUser, self.count, self.typingSpeed)
        time.sleep(4)
        prev_commands = []
        start_duration = time.time()
        typeTimes = random.randint(2, 3)
        for i in range(0, typeTimes):
            start = time.time()
            end = 0
            typeDuration = (15 * random.random()) + 10
            while (end < start + typeDuration):
                command = self.commands[random.randrange(0, len(self.commands))]
                if command == 'cd':
                    df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : 'ls'}, index=False)
                    typeCommand.type("ls", currUser, self.count, self.typingSpeed)
                    currDirect = self.tree[len(self.tree) - 1]
                    if len(currDirect.subf) != 0:
                        sub = currDirect.subf[random.randrange(0, len(currDirect.subf))]
                        command = f'cd {sub.name}'
                        self.tree.append(sub)
                    else:
                        command = 'cd ..'
                        self.tree.pop()
                elif command == 'cd ..':
                    if len(self.tree) == 1:
                        continue
                    self.tree.pop()
                elif command == 'cat':
                    df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : 'ls'}, index=False)
                    typeCommand.type("ls", currUser, self.count, self.typingSpeed)
                    currDirect = self.tree[len(self.tree) - 1]
                    if len(currDirect.files) == 0:
                        continue
                    file = currDirect.files[random.randrange(0, len(currDirect.files))]
                    command = f'cat {file}'
                if command in prev_commands:
                    continue
                current_time = time.time() - start_duration
                nanoKey = typeCommand.type(command, currUser, self.count, self.typingSpeed)
                if nanoKey:
                    df_user = df_user.append({"Time" : current_time, "Command" : "nano: " + nanoKey})
                else:
                    df_user = df_user.append({"Time" : current_time, "Command" : command})
                if command == f'mkdir Thread{self.count}':
                    time.sleep(2 * random.random() + 1)
                    df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : f'rmdir Thread{self.count}'}, index=False)
                    typeCommand.type(f'rmdir Thread{self.count}', currUser, self.count, self.typingSpeed)
                time.sleep(3 * random.betavariate(3, 7) + 0.7)
                prev_commands.append(command)
                if len(prev_commands) > 2:
                    prev_commands.pop(0)
                end = time.time()
            time.sleep(4 * random.random() + 1.5)
        df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : 'exit'}, index=False)
        typeCommand.type("exit", currUser, self.count, self.typingSpeed)
        elapsed = time.time() - start_duration
        print(f"Normal User at Thread {self.count} is exiting. Duration: {elapsed} s")
        client = ip_location[self.count + 1]
        filename = f"exp{exp}_{client.replace('.','-')}_1hop.csv"
        df_user.to_csv(filename, index=False)
        log = [
            str(datetime.datetime.now()),
            exp,
            client,
            elapsed,
            1/(0.2*self.typingSpeed),
            1,
            filename
        ]
        df.add(log)

class HackerUser():
    def __init__(self, server, count, home):
        self.server = server.lower()
        if self.server == 'uh':
            credsList = []
            with open('secret.txt', 'r') as fn:
                for line in fn.readlines():
                    credsList.append(line.strip())
            creds = {'username': credsList[0], 'password': credsList[1]}
            self.ssh_cmd = f"ssh {creds['username']}@129.7.241.21"
            self.pw = creds['password']
        self.count = count
        self.typingSpeed = (0.40 * random.random()) + 0.30
        self.tree = [home]
        self.visited = set()
    def launch(self, currUser, typeCommand):
        global ip_location
        global exp
        global df
        df_user = pandas.DataFrame(columns=["Time", "Commands"])
        # Log into the server through SSH
        time.sleep(2)
        if self.server == 'uh':
            typeCommand.UHlogin(currUser, self.count, self.ssh_cmd, self.pw)
        else:
            typeCommand.type(f"ssh {self.server}", currUser, self.count, self.typingSpeed)
        time.sleep(4)
        start_time = time.time()
        while len(self.tree) != 0:
            typeCommand.type("ls", currUser, self.count, self.typingSpeed)
            currDirect = self.tree[len(self.tree) - 1]
            if currDirect not in self.visited:
                for file in currDirect.files:
                    typeCommand.type(f"cat {file}", currUser, self.count, self.typingSpeed)
                    time.sleep(random.random() + 0.5)
                self.visited.add(currDirect)
            for sub in currDirect.subf:
                if sub not in self.visited:
                    self.tree.append(sub)
                    break
            if set(currDirect.subf).issubset(self.visited):
                typeCommand.type(f"cd ..", currUser, self.count, self.typingSpeed)
                self.tree.pop()
            else:
                typeCommand.type(f"cd {self.tree[len(self.tree) - 1].name}", currUser, self.count, self.typingSpeed)
            time.sleep(random.random() + 0.5)
        typeCommand.type("exit", currUser, self.count, self.typingSpeed)
        elapsed = time.time() - start_time
        print(f"Hacker at Thread {self.count} is exiting. Duration: {elapsed} s")
        client = ip_location[self.count + 1]
        filename = f"exp{exp}_{client.replace('.','-')[:client.find(',')]}_3hop.csv"
        df_user.to_csv(filename, index=False)
        log = [
            str(datetime.datetime.now()),
            exp,
            client,
            elapsed,
            1/(0.2*self.typingSpeed),
            3,
            filename
        ]
        df.add(log)


if __name__ == "__main__":
    keyboard = KeyboardController()
    mouse = MouseController()
    parser = argparse.ArgumentParser(description="Simulate several normal and/or attacking users.")
    parser.add_argument("server", type=str, help="(str) The location of the connected server (e.g. 'uh' for UH Sever, 'frankfurt' for Frankfurt AWS)")
    parser.add_argument("totalUsers", type=int, help="(int) The total number of users connected to the server.")
    parser.add_argument("--hk", "--hacker", type=int, help="(int) The terminal window that the hacker will run. START FROM ZERO.")
    parser.add_argument("--r", "--repeat", type=int, help="Choose how many times to repeat")
    parser.add_argument("--c", "--connection")
    args = parser.parse_args()
    server = args.server
    totalUsers = args.totalUsers
    hacker = args.hk
    repeat = args.r

    ML = [Node('ML1', files=['samford']), Node('ML2'), Node('ML3', files=['traffic_analysis'])]
    JC = [Node('JC1', files=['gatech']), Node('JC2',files=['robotics']), Node('JC3',files=['anomaly'])]
    JL = [Node('JL1', files=['csun']), Node('JL2'), Node('JL3', files=['classification'])]
    home = Node('~', subf=[Node('Folder', files=['textToHTML', 'info'], subf=[Node('ML', subf=ML),
        Node('JC', files=['finances'], subf=JC), Node('JL', subf=JL)])])
    currUser = UserNum()
    typeCommand = TypeCommand()
    df = DataFrame()
    with open("ip_location.txt") as f:
        ip_location = f.readlines()
    with open("count.txt") as f:
        exp = int(f.read())
    f.close()
    with open("count.txt", 'w') as f:
        f.write(exp + 1)
    f.close()
    print("Place your mouse near the top right corner of the screeen.")
    # Wait to place mouse cursor in correct position
    time.sleep(5)
    keyboard.type("./pcap.sh")
    mouse.move(-1650, 0)
    mouse.click(Button.left)
    with futures.ThreadPoolExecutor(max_workers=totalUsers) as ex:
        for i in range(0, totalUsers):
            if i == hacker:
                ex.submit(HackerUser(server, i, home).launch, currUser, typeCommand)
            else:
                ex.submit(NormalUser(server, i, home).launch, currUser, typeCommand)
            time.sleep(random.random() * 3)
    df.to_csv()
    mouse.move(1650, 0)
    time.sleep(1)
    mouse.click(Button.left)
    keyboard.press(Key.ctrl)
    keyboard.press('c')
    keyboard.release('c')
    keyboard.release(Key.ctrl)