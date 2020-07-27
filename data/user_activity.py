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
        with self.lock:
            self.df = self.df.append(log, ignore_index=True)
    def to_csv(self):
        if os.path.exists("user_activity_log.csv"):
            old_df = pandas.read_csv("user_activity_log.csv")
            result = pandas.concat([old_df, self.df], ignore_index=True)
            result = result.drop_duplicates(subset=["Date/Local Time"], ignore_index=True)
            result.to_csv("user_activity_log.csv", index=False)
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
        credsList = []
        with open('secret.txt', 'r') as fn:
            for line in fn.readlines():
                credsList.append(line.strip())
        creds = {'username': credsList[0], 'password': credsList[1]}
        self.ssh_cmd = f"ssh {creds['username']}@129.7.241.21"
        self.pw = creds['password']

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
    
    def UHlogin(self, currUser, count, typingSpeed):
        self.type(self.ssh_cmd, currUser, count, typingSpeed)
        time.sleep(2)
        self.type(self.pw, currUser, count, typingSpeed)

class NormalUser():

    def __init__(self, server, count, home):
        self.server = server.lower()
        self.count = count
        self.commands = ['df', 'ls', 'lsblk', 'lscpu', 'mount', 'pwd', 'history', 'ss', f'mkdir Thread{self.count}', 
            'cal', 'cd', 'cd ..', 'nano', 'pwd', f'mkdir Thread{self.count}', 'echo this is a random statement', 
            'echo this long statement is to generate a lot of data packets', 'history', 'ss', 'lsblk']
        self.typingSpeed = (0.20 * random.random()) + 0.30
        self.tree = [home]

    def launch(self, currUser, typeCommand):
        """
        Here is an edit to make the normal user have almost no gap in between commands. I edited the the pauses 
        for the normal user to be as close to zero as possible.
        """
        global ip_location
        global exp
        global df
        global totalUsers
        df_user = pandas.DataFrame(columns=['Time', 'Command'])
        # Log into the server through SSH
        time.sleep(2)
        if self.server == 'uh':
            typeCommand.UHlogin(currUser, self.count, self.typingSpeed)
        else:
            typeCommand.type(f"ssh {self.server}", currUser, self.count, self.typingSpeed)
        time.sleep((totalUsers - self.count) + 2)
        prev_commands = []
        start_duration = time.time()
        typeTimes = 3
        for i in range(typeTimes):
            start = time.time()
            end = 0
            typeDuration = (7.5 * random.random()) + 17.5
            while (end < start + typeDuration and time.time() - start_duration <= 75):
                command = self.commands[random.randrange(len(self.commands))]
                # print(f"Normal User as Thread{self.count}: " + command)
                if command == 'cd':
                    df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : 'ls'}, ignore_index=True)
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
                    df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : 'ls'}, ignore_index=True)
                    typeCommand.type("ls", currUser, self.count, self.typingSpeed)
                    currDirect = self.tree[len(self.tree) - 1]
                    if len(currDirect.files) == 0:
                        continue
                    file = currDirect.files[random.randrange(0, len(currDirect.files))]
                    command = f'cat {file}'
                if command in prev_commands or (command == "nano" and time.time() - start_duration >= 70):
                    continue
                current_time = time.time() - start_duration
                nanoKey = typeCommand.type(command, currUser, self.count, self.typingSpeed)
                if nanoKey:
                    df_user = df_user.append({"Time" : current_time, "Command" : "nano: " + nanoKey}, ignore_index=True)
                else:
                    df_user = df_user.append({"Time" : current_time, "Command" : command}, ignore_index=True)
                if command == f'mkdir Thread{self.count}':
                    time.sleep(2 * random.random() + 1)
                    df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : f'rmdir Thread{self.count}'}, ignore_index=True)
                    typeCommand.type(f'rmdir Thread{self.count}', currUser, self.count, self.typingSpeed)
                # time.sleep(3 * random.betavariate(3, 7) + 0.7)
                # time.sleep(random.betavariate(3, 7))
                prev_commands.append(command)
                if len(prev_commands) > 1:
                    prev_commands.pop(0)
                end = time.time()
            # time.sleep(4 * random.random() + 1.5)
            time.sleep(0.25)
        df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : 'logout'}, ignore_index=True)
        typeCommand.type("logout", currUser, self.count, self.typingSpeed)
        elapsed = time.time() - start_duration
        print(f"Normal User at Thread {self.count} is exiting. Duration: {elapsed} s")
        client = ip_location[self.count].strip()
        filename = f"exp{exp}_{client.replace('.','-')}_1hop.csv"
        path = os.getcwd() + '/experiment_logs/' + filename
        df_user.to_csv(path, index=False)
        log = {
            "Date/Local Time" : str(datetime.datetime.now()),
            "Experiment Number" : exp,
            "IP/Location(s)" : client,
            "Test Duration" : elapsed,
            "Avg Typing Speed (char/s)" : 1/(0.2*self.typingSpeed),
            "Hops" : 1,
            "Filename" : filename
        }
        df.add(log)

class HackerUser():
    def __init__(self, server, count, home):
        self.server = server.lower()
        self.count = count
        self.typingSpeed = (0.20 * random.random()) + 0.30
        self.commands = ['df', 'lsblk', 'lscpu', 'mount', 'pwd', 'history', 'ss', 'cal', 'nano', 'pwd', 'history', 'ss', 'lscpu',
            "echo this is a random command that does not mean anything", "echo this is only to generate as many data packets as possible"]
        self.tree = [home]
        self.visited = set()
    def launch(self, currUser, typeCommand):
        """
        Here is an edit to make the hacker have almost no gap in between commands. I commented out the the pauses 
        for the hacker and added some other longer commands to enter as well.
        """
        global ip_location
        global exp
        global df
        global totalUsers
        df_user = pandas.DataFrame(columns=["Time", "Command"])
        # Log into the server through SSH
        time.sleep(2)
        if self.server == 'uh':
            typeCommand.UHlogin(currUser, self.count, self.typingSpeed)
        else:
            typeCommand.type(f"ssh {self.server}", currUser, self.count, self.typingSpeed)
        time.sleep((totalUsers - self.count) + 2)
        start_duration = time.time()
        total_duration = 20 * random.random() + 55
        while len(self.tree) != 0 and time.time() - start_duration <= total_duration:
            df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : 'ls'}, ignore_index=True)
            # print(f"Hacker at Thread {self.count}: ls")
            typeCommand.type("ls", currUser, self.count, self.typingSpeed)
            currDirect = self.tree[len(self.tree) - 1]
            if currDirect not in self.visited:
                for file in currDirect.files:
                    df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : f'cat {file}'}, ignore_index=True)
                    # print(f"Hacker at Thread {self.count}: cat {file}")
                    typeCommand.type(f"cat {file}", currUser, self.count, self.typingSpeed)
                    # time.sleep(random.random() + 0.5)
                    time.sleep(0.2)
                self.visited.add(currDirect)
            for sub in currDirect.subf:
                if sub not in self.visited:
                    self.tree.append(sub)
                    break
            if set(currDirect.subf).issubset(self.visited):
                df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : 'cd ..'}, ignore_index=True)
                # print(f"Hacker at Thread {self.count}: cd ..")
                typeCommand.type(f"cd ..", currUser, self.count, self.typingSpeed)
                self.tree.pop()
            else:
                df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : f"cd {self.tree[len(self.tree) - 1].name}"}, ignore_index=True)
                # print(f"Hacker at Thread {self.count}: cd {self.tree[len(self.tree)-1].name}")
                typeCommand.type(f"cd {self.tree[len(self.tree) - 1].name}", currUser, self.count, self.typingSpeed)
            # time.sleep(random.random() + 0.1)
            time.sleep(0.2)
            # This is newly added to the hacker
            command = self.commands[random.randrange(len(self.commands))]
            current_time = time.time() - start_duration
            nanoKey = typeCommand.type(command, currUser, self.count, self.typingSpeed)
            if nanoKey:
                df_user = df_user.append({"Time" : current_time, "Command" : "nano: " + nanoKey}, ignore_index=True)
            else:
                df_user = df_user.append({"Time" : current_time, "Command" : command}, ignore_index=True)
        df_user = df_user.append({"Time" : time.time() - start_duration, "Command" : "logout"}, ignore_index=True)
        typeCommand.type("logout", currUser, self.count, self.typingSpeed)
        elapsed = time.time() - start_duration
        print(f"Hacker at Thread {self.count} is exiting. Duration: {elapsed} s")
        client = ip_location[self.count].strip()
        filename = f"exp{exp}_{client.replace('.','-')[:client.find(',')]}_3hop.csv"
        path = os.getcwd() + '/experiment_logs/' + filename
        df_user.to_csv(path, index=False)
        log = {
            "Date/Local Time" : str(datetime.datetime.now()),
            "Experiment Number" : exp,
            "IP/Location(s)" : client,
            "Test Duration" : elapsed,
            "Avg Typing Speed (char/s)" : 1/(0.2*self.typingSpeed),
            "Hops" : 3,
            "Filename" : filename
        }
        df.add(log)


if __name__ == "__main__":
    keyboard = KeyboardController()
    mouse = MouseController()
    parser = argparse.ArgumentParser(description="Simulate several normal and/or attacking users.")
    # parser.add_argument("server", type=str, help="(str) The location of the connected server (e.g. 'uh' for UH Sever, 'frankfurt' for Frankfurt AWS)")
    parser.add_argument("--t", type=int, help="(int) The total number of users connected to the server.")
    parser.add_argument("--r", "--repeat", type=int, help="Choose how many times to repeat.")
    parser.add_argument("--c", "--connection", help="Establish the master/slave system by inputting 'master' or 'slave'.")
    args = parser.parse_args()
    # server = args.server
    totalUsers = args.t
    connection = args.c
    if connection and connection != "master" and connection != "slave":
        raise ValueError("Did not give 'master' or 'slave' input.")
    hacker = None
    hacker_hops = None
    repeat = args.r
    if not repeat:
        repeat = 1

    ML = [Node('ML1', files=['samford']), Node('ML2'), Node('ML3', files=['traffic_analysis'])]
    JC = [Node('JC1', files=['gatech']), Node('JC2',files=['robotics']), Node('JC3',files=['anomaly'])]
    JL = [Node('JL1', files=['csun']), Node('JL2'), Node('JL3', files=['classification'])]
    home = Node('~', subf=[Node('Folder', files=['textToHTML', 'info', 'info2', 'info5', 'info7', 'echo15'], subf=[Node('ML', subf=ML),
        Node('JC', files=['finances'], subf=JC), Node('JL', subf=JL)])])
    currUser = UserNum()
    typeCommand = TypeCommand()
    df = DataFrame()
    for rep in range(1, repeat+1):
        if connection:
            start_clock = time.time()
        currUser.val = 0
        with open('ip_location.txt') as f:
            ip_location = f.readlines()
            if (totalUsers != None) and len(ip_location) != totalUsers:
                raise AssertionError("The length of ip_location.txt does not match the given input.")
            elif not totalUsers:
                totalUsers = len(ip_location)
        with open("count.txt") as f:
            exp = int(f.read())
        with open("count.txt", 'w') as f:
            f.write(str(exp + 1))
        # Wait to place mouse cursor in correct position
        if rep == 1:
            print("Place your mouse cursor near the top left of your screen (the first simulated user terminal).")
            print("Make sure that all AWS machines are turned on, and the initial ip_location.txt is correct.")
        time.sleep(5)
        mouse.click(Button.left)
        time.sleep(1)
        # SSH into all of the respective client terminal windows
        if rep % 3 == 1 or rep == 1:
            for i in range(totalUsers):
                clients = ip_location[i].split(',')
                if len(clients) > 1:
                    hacker = i
                    hacker_hops = len(client)
                for client in clients:
                    keyboard.type("ssh " + client[:client.find('-')].lower())
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
                    time.sleep(4)
                # Ctrl-Tab to the next terminal window
                keyboard.press(Key.ctrl)
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                keyboard.release(Key.ctrl)
        # Moves mouse to right side of screen to start tshark command
        if not connection or connection == "master":
            mouse.move(1650, 0)
            time.sleep(0.5)
            mouse.click(Button.left)
            time.sleep(1)
            keyboard.type("./pcap.sh")
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            mouse.move(-1650, 0)
            mouse.click(Button.left, count=4)
            time.sleep(1.5)
        elif connection == "slave":
            time.sleep(1.8)
        # Generates simulated users
        with futures.ThreadPoolExecutor(max_workers=totalUsers) as ex:
            for i in range(totalUsers):
                if i == hacker:
                    ex.submit(HackerUser('uh', i, home).launch, currUser, typeCommand)
                else:
                    ex.submit(NormalUser('uh', i, home).launch, currUser, typeCommand)
                time.sleep(3*random.random()+0.2)
        print(f"Experiment {exp} has ended.")
        df.to_csv()
        if not connection or connection == "master":
            mouse.move(1650, 0)
            mouse.click(Button.left)
            time.sleep(1)
            keyboard.press(Key.ctrl)
            keyboard.press('c')
            keyboard.release('c')
            keyboard.release(Key.ctrl)
            mouse.move(-1650, 0)
            mouse.click(Button.left)
        elif connection == "slave":
            time.sleep(1.2)
        # Exit out of all of the terminal windows
        time.sleep(1)
        if exp % 3 == 0 or rep == repeat:
            for i in range(totalUsers):
                if i == hacker:
                    for j in range(2):
                        keyboard.type("logout")
                        keyboard.press(Key.enter)
                        keyboard.release(Key.enter)
                        time.sleep(1)
                        keyboard.press(Key.ctrl)
                        keyboard.press('c')
                        keyboard.release('c')
                        keyboard.release(Key.ctrl)
                        time.sleep(1)
                keyboard.type("logout")
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
                time.sleep(1)
                keyboard.press(Key.ctrl)
                keyboard.press('c')
                keyboard.release('c')
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                keyboard.release(Key.ctrl)  
        if repeat > 1:
            if exp % 9 == 0:
                hacker = None
                rand = random.randint(totalUsers//2,2*totalUsers//3)
                usa_count = random.sample(range(1, 5), rand)
                with open("ip_location_list.txt") as fr:
                    with open("ip_location.txt", 'w') as fw:
                        ip_location_list = fr.readlines()
                        for i in usa_count:
                            fw.write(ip_location_list[i])
                        foreign = ip_location_list[5:]
                        for i in range(totalUsers - rand):
                            host = foreign[random.randrange(0, len(foreign))]
                            fw.write(host)
                            foreign.remove(host)
            elif exp % 3 == 0 and connection != "slave":
                rand = random.randint(totalUsers//2,2*totalUsers//3)
                usa_count = random.sample(range(1, 5), rand)
                with open("ip_location_list.txt") as fr:
                    with open("ip_location.txt", 'w') as fw:
                        ip_location_list = fr.readlines()
                        for i in usa_count:
                            fw.write(ip_location_list[i])
                        foreign = ip_location_list[5:]
                        hacknum = random.randrange(totalUsers - rand)
                        for i in range(totalUsers - rand):
                            if i == hacknum:
                                hackerstr = ""
                                for j in range(3):
                                    host_h = foreign[random.randrange(0, len(foreign))]
                                    hackerstr += host_h.strip()
                                    if j != 2:
                                        hackerstr += ','
                                    else:
                                        hackerstr += '\n'
                                    foreign.remove(host_h)
                                host = hackerstr
                            else:
                                host = foreign[random.randrange(0, len(foreign))]
                                foreign.remove(host)
                            fw.write(host)
        if connection:
            time.sleep(170 - (time.time() - start_clock))
        else:
            time.sleep(10)