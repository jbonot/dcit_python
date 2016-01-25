'''
@Author - Kunwar Abhinav Aditya, Sakshi Syal
The program below is an implemenation of client-server architecture, where-in new nodes can typically
join in and sign off from the existing network. A master node keeps track of the nodes in the network
and...'''


import threading
import xmlrpclib
import random
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer
nodes = []
ip = 0
port = 0
myID = 0
masterNode = []
masterWordString = []
waitingQueue = []


def rantomInt():
    print (random.randint(0,9))
    return  


def initMasterString():
    global masterWordString
    masterWordString = ""
    
    
# Function to append string every-time
def appendString(newString, word):
    newString += appendString(word)
    return


def randomStringGenerator():
    WORDS = ("apple", "banana", "carrot", "date", "eggplant", "fig", "guava")
    word = random.choice(WORDS)
    return word
    
    
''' User input to receive IP and port for the new node created!
The code snippet below also takes care of a likely warning message
if the user gives a not-a-number input for the port number '''

import socket
ip = socket.gethostbyname(socket.gethostname())
while True:    
    try:
        port = int(raw_input('Assign me a port: '))
    except ValueError:
        print '\n Please enter something in digits'
        continue
    break


# Code to check if id already exists
def checkID(clientID):
    global myID
    if clientID == myID:
        print "\n ID is the same as my ID...changing ID..."
        clientID = createNewID()
        clientID = checkID(clientID)
    if len(nodes) > 0:
        print "\n checking if ID is unique..."
        for entry in nodes:
            if clientID == entry[2]:
                print "\n ID isn't unique...changing ID..."
                clientID = createID()
                clientID = checkID(clientID)
                break
    return clientID
    
    
# Joining
def joinRequest(clientIP, clientPort, clientID):
    global nodes
    newNode = [clientIP, clientPort, clientID]
    myDetails = [ip, port, myID]
    if checkInList(clientIP, clientPort) == False:
        newID = checkID(clientID)
        print "\n New id..."+str(newID)
        if newID == clientID:
            print "\n ID unique...joining node!"
        else:
            print "\n ID wasn't unique. Sending new ID to new node!"
            updateId(clientIP, clientPort, clientID)
        if len(nodes) > 1:
            sendToAll(newNode)
        proxyServer = xmlrpclib.ServerProxy("http://"+clientIP+":"+clientPort+"/", allow_none=True)
        proxyServer.buildClientNetwork(ip, port, myID)  
        for entry in nodes:
            proxyServer.buildClientNetwork(entry[0], entry[1], entry[2])          
        nodes.append(myDetails)
        return
    else:
        print "\n Node already in network!"
    return



def buildClientNetwork(nodeIP, nodePort, nodeID):
    newNode = [nodeIP, nodePort, nodeID]
    nodes.append(newNode)
    return
    
def updateId(clientIP, clientPort, clientID):
    proxyServer = xmlrpclib.ServerProxy("http://"+clientIP+":"+clientPort+"/", allow_none=True)
    proxyServer.myUpdatedID(clientID)
    return
    
    
# Code to update node's ID
def myUpdatedID(newID):
    global myID
    myID = newID
    return


# Code to check in the existing list
def checkInList(clientIP, clientPort):
    flag = False
    # Code segment to check whether the calling node is the same node as the called node
    if clientIP == ip and clientPort == port:
        flag = True
        print "\n This is the same node as me!!"
        return flag
    print "\n checking if node already exists..."
    for entry in nodes:
        if clientIP == entry[0] and clientPort == entry[1]:
            flag = True
            break
        else:
            continue
    return flag


# Create a random Id for each node
def createID():
    return random.randrange(0,10000)


# This code is executed by the node called by the joining node, if the id of the calling node is same as of one of the already existing nodes
def createNewID():
    global nodes
    newID = createID()
    for entry in nodes:
        if newID == entry[2]:
            createNewID()
    return newID


# Function to broadcast the message of new nodes joining the network
def sendToAll(newNode):
    global nodes
    for entry in nodes:
        proxyServer = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
        proxyServer.acknowledgeNewJoin(newNode)
    return

        
# Function to acknowledge the joining of a new node to an already existing node
def acknowledgeNewJoin(newNode):
    global nodes
    nodes.append(newNode)
    print "\n New node with IP: "+str(newNode[0])+" and port: "+str(newNode[1])+" added in the network"
    return


# Start Elections
def callForElection():
    global ip
    global port
    global myID
    receiveOK = ""
    timeout_start = time.time()
    timeout = 5
    highest = "YES"
    while time.time() < (timeout_start + timeout):
        print "\n Initiating Master Node Election..."
        for entry in nodes:
            if entry[2] > myID:
                highest = "NO"
                proxyServer = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
                receiveOK = proxyServer.notificationForElection(ip, port, myID)                 
                if receiveOK == "OK":
                    print "\n I lost the election!"
                    return
        if highest == "YES":
            print "\n Highest ID. I'm the Winner!"
            setMasterNode()
            return
    if receiveOK == "":
            print "\n No response. I'm the Winner!"
            setMasterNode()
    return

def isJoined():
    if nodes == []:
        return False
    else:
        return True
        

# Start read-write
def startReadWrite():
    buildMasterNode()
    print ("\n Usage: start <algorithm (CME or RA)>: "),    
    algorithm = raw_input
    timeout_start = time.time()
    timeout = 20
    while time.time() < (timeout_start + timeout):
        if str(algorithm).upper() == "CME":
            sendStart("CENTRALIZED_MUTUAL_EXCLUSION");
        elif str(algorithm).upper() == "RA":
            sendStart("RICART_AGRAWALA")
    return


def sendStart(entry):
    if entry == "CENTRALIZED_MUTUAL_EXCLUSION":
        centralizedMutualExclusion()
    if entry == "RICART_AGRAWALA":
        ricartAgrawala()
    return

#-----------------------------------------------#
#-----------------------------------------------#
#---------CENTRALIZED MUTUAL EXCLUSION----------#
#-----------------------------------------------#
#-----------------------------------------------#    

def centralizedMutualExclusion():
    for entry in nodes:
        proxyServer = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
        proxyServer.readWriteStarted("start")
    word = randomStringGenerator()
    proxyServer = xmlrpclib.ServerProxy("http://"+str(masterNode[0])+":"+str(masterNode[1])+"/", allow_none=True)
    proxyServer.requestMasterString(ip, port, myID, word)  
    proxyServer.initMasterString()               
    checkRequestQueue()
    return


def readWriteStarted(entry):
    print "received the message: "+str(entry)
    
def receiveRequest():
    print "Receive request"
    
def requestMasterString(clientIP, clientPort, clientID, word):
    if clientIP == masterNode[0] and clientPort == masterNode[1]:
        wordString = [word, clientID]
        masterWordString.append(wordString)
        print "Finished Servicing: "+masterNode
    else:
        if checkCriticalSection() == False:
            print "Permission granted"
        else:
            checkRequestQueue()           
            print "Added to the waiting queue"
            waitingObject = [clientIP, clientPort, clientID]
            waitingQueue.append(waitingObject)
    return

def checkRequestQueue():
    if waitingQueue == []:
        return "OK"
    else:
        return


tLock = threading.Lock()
def checkCriticalSection():
    if tLock.locked() == True:
        return True
    else:
        return False
    
def syncBlock(word):
    tLock.acquire()
    appendString(masterWordString, word)
    print "Updated String: "+masterWordString
    tLock.release()
#-----------------------------------------------#
#-----------------------------------------------#
#---------------RICART AGRAWALA-----------------#
#-----------------------------------------------#
#-----------------------------------------------#
def ricartAgrawala(masterNode):   
    return


def buildMasterNode():
    if isJoined() == False:
        print "You must join a network before you can start"
        return
    callForElection()
    return


# Notification For Election
def notificationForElection(nodeIP, nodePort, nodeID):
    print "\n Message received: ELECTION from "+str(nodeIP)+", "+str(nodePort)+", "+str(nodeID)+""
    print "\n My ID is higher so I'll start my own election!"
    try:
        return "OK"
    finally:
        callForElection()       

'''
def startThreads(nodeIP, nodePort, nodeID):
    global thrElection1
    global thrElection2
    thrElection1 = threading.Thread(target = notificationForElection, args =(ip, port, myID))
    thrElection1.start()
    thrElection2 = threading.Thread(target = notificationForElection, args =(ip, port, myID))
    thrElection2.start()
    return
'''

# Send OK
def sendOK(nodeIP, nodePort, nodeID):
    proxyServer = xmlrpclib.ServerProxy("http://"+str(nodeIP)+":"+str(nodePort)+"/", allow_none=True)
    proxyServer.receiveOK(ip, port, myID)
    proxyServer.amIStillEligible("NO")
    return
    
    
# Receive OK
def receiveOK(nodeIP, nodePort, nodeID):
    print "\n Node with ip: "+str(nodeIP)+" and port: "+str(nodePort)+" took over."
    return
    
        
# Set Master Node
def setMasterNode():
    for entry in nodes:
                proxyServer = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
                proxyServer.masterNodeConfirmation(ip, port, myID)
    return
    

# Master Node Confirmation
def masterNodeConfirmation(clientIP, clientPort, clientID):
    print "\n The node with ip: "+str(clientIP)+" and port: "+str(clientPort)+" is the new master"
    return

    
# Logging out
def logout(myIP):
    global nodes
    try:
        nodes.remove(myIP)
        print ("\n Node with IP: "+str(myIP[0])+" and Port: "+str(myIP[1])+" has left the network")
    except Exception:
        print '\n Not able to remove this node'
    return


# Server implementation
def server():
    server = SimpleXMLRPCServer((ip, port), allow_none=True)
    server.register_function(initMasterString, "initMasterString")
    server.register_function(joinRequest, "joinRequest")
    server.register_function(logout, "logout")
    server.register_function(myUpdatedID, "myUpdatedID")   
    server.register_function(acknowledgeNewJoin, "acknowledgeNewJoin")
    server.register_function(masterNodeConfirmation, "masterNodeConfirmation")
    server.register_function(requestMasterString, "requestMasterString")
    server.register_function(notificationForElection, "notificationForElection")
    #server.register_function(startThreads, "startThreads")
    print "\n Server started and listening with IP = "+str(ip)+" and port = "+str(port)
    server.serve_forever()


# Threading implementation
thr = threading.Thread(target = server)
thr.start()
    

# Client implementation
def client():
    global nodes
    global ip
    global port
    global myID
    myID = createID()
    myInfo = [ip, port, myID]
    while True:
        print("""
        1. Join
        2. Elect
        3. Start Read/ Write
        4. Sign off
        """)
        ans = raw_input("\n What would you like to do? ")
        if ans == "1":
            print '\n Which server do you want to join?'
            print '\n Server IP: ', 
            serverip = raw_input()
            print '\n Server Port: ', 
            serverPort = raw_input()
            if str(ip) == str(serverip) and str(port) == str(serverPort):
                print '\n Connecting yourself to yourself? Not possible'
                continue
            proxyServer = xmlrpclib.ServerProxy("http://"+str(serverip)+":"+str(serverPort)+"/", allow_none=True)
            proxyServer.joinRequest(ip, str(port), myID)
            print '\n Connection established'
            continue   
        elif ans == "2":
            callForElection()
            continue
        elif ans == "3":
            startReadWrite()
            continue
        elif ans == "4":
            for entry in nodes:
                if entry != myInfo:
                    proxy = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
                    proxy.logout(ip)
            nodes.remove(myInfo)
            nodes = []
            nodes.append(myInfo)          
            break
client()