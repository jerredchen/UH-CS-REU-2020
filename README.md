# UH-CS-REU-2020

This Github repository consists of the tools and research developed for Using Anomaly Detection to Differentiate between Short and Long Chains with Dr. Stephen Huang at the 2020 University of Houston's Data-Driven Computing REU.

## Background

As stated in [this research survey](https://jwcn-eurasipjournals.springeropen.com/articles/10.1186/s13638-018-1303-2#Abs1):
>Attackers on the Internet often launch network intrusions through compromised hosts, called stepping-stones, in order to reduce the chance of being detected. In a stepping-stone attack, an intruder uses a chain of hosts on the Internet as relay machines and remotely log in these hosts using tools such as telnet, rlogin, or SSH.

A vast majority of everyday users will create a single, "1-hop connection" to a respective server for work, administrative, or personal purposes. Because longer connections will delay the client's network connection, these longer chains often imply malicious intent. Most research in stepping-stone intrusion relies on detecting whether or not a host is being used as a stepping-stone as opposed of protecting the victim server. However, not protecting the server leaves it defenseless from stepping-stone intruders since only the first line of network connections is available to the server. Our research aims to differentiate a 3-hop chain among several 1-hop chains in a single, "live" packet capture using anomaly detection.

## Simulated User Program

The experiments performed for this research required several people on 1-hop connections to serve as a normal, everyday user connecting to a single server while one person on a 3-hop connection to serve as a stepping-stone intruder. Data analysis would be performed on the differences of times for network packets between the server and respective client servers. The servers were deployed in different locations globally using AWS.

However, it is infeasible to perform machine learning techniques on a few dozen collected experiments using human users. 
