# UH-CS-REU-2020

This Github repository consists of the tools and research developed for Using Anomaly Detection to Differentiate between Short and Long Chains with Dr. Stephen Huang at the 2020 University of Houston's Data-Driven Computing REU.

## Background

As stated in [this research survey](https://jwcn-eurasipjournals.springeropen.com/articles/10.1186/s13638-018-1303-2#Abs1):
>Attackers on the Internet often launch network intrusions through compromised hosts, called stepping-stones, in order to reduce the chance of being detected. In a stepping-stone attack, an intruder uses a chain of hosts on the Internet as relay machines and remotely log in these hosts using tools such as telnet, rlogin, or SSH.

![](https://github.com/jerredchen/UH-CS-REU-2020/blob/master/stepping-stone-diagram.png)

A vast majority of everyday users will create a single, "1-hop connection" to a respective server for work, administrative, or personal purposes. Because longer connections will delay the client's network connection, these longer chains often imply malicious intent. Most research in stepping-stone intrusion relies on detecting whether or not a host is being used as a stepping-stone as opposed of protecting the victim server. However, not protecting the server leaves it defenseless from stepping-stone intruders since only the first line of network connections is available to the server. Our research aims to differentiate a 3-hop chain among several 1-hop chains in a single, "live" packet capture using anomaly detection.

## Simulated User Program

The experiments performed for this research required several people on 1-hop connections to serve as a normal, everyday user connecting to a single server while one person on a 3-hop connection to serve as a stepping-stone intruder. Data analysis would be performed on the differences of times for network packets between the server and respective client servers. The servers were deployed in different locations globally using AWS.

However, it is infeasible to perform machine learning techniques on a few dozen collected experiments using human users. Created a simulated user program would allow for automating the experimentation process and using simulated users on a single computer instead of gathering data from several human users connected to the server.

![](https://github.com/jerredchen/UH-CS-REU-2020/blob/master/simulated-users.gif)

(Link of video for better quality: https://youtu.be/2831js2RWKY?t=45)

Features:
- Multithreading is implemented for each user to reside on an individual thread. This allows the typing among users to occur as simultaneous as possible.
- To switch between the simultaneous users typing, the Linux terminal app [Terminator](https://gnometerminator.blogspot.com/p/introduction.html) is used with the help of a threading lock. Each user types on a separate terminal using Terminator.
  - After a respective user thread reaches the lock and is able to unlock it, the user calculates which terminal is currently being used and how to get to its respective terminal from the current terminal.
- A list of Linux commands are randomly typed by each user as well as some basic file traversal. These commands are used to generate network packets that will be used in analysis.
- The gaps between each typed character and the pauses between each typed command were modelled after human typing data, which was collected from the previous experiments. The gaps for the simulated users were then sampled from probability distributions of human typing.
- A log is created using Pandas with the location of the host(s), IP addresses, duration of the typing session (varies randomly between 60-90 seconds), and a list of all commands typed out.
