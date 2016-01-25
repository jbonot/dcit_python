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
import cme

nodes = []
ip = 0
port = 0
myID = 0
masterNode = []
masterWordString = []
waitingQueue = []
algorithm = None

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
    myDetails = [ip, port, myID]
    if checkInList(clientIP, clientPort) == False:
        newID = checkID(clientID)
        print "\n New id..."+str(newID)
        if newID == clientID:
            print "\n ID unique...joining node!"
        else:
            print "\n ID wasn't unique. Sending new ID to new node!"
            updateId(str(clientIP), int(clientPort), int(clientID))
        if len(nodes) > 1:
            sendToAll(str(clientIP), int(clientPort), int(clientID))
        proxyServer = xmlrpclib.ServerProxy("http://"+clientIP+":"+clientPort+"/", allow_none=True)
        proxyServer.receiver.nodeJoined(str(ip), int(port), int(myID))  
        for entry in nodes:
            proxyServer.receiver.nodeJoined(str(entry[0]), int(entry[1]), int(entry[2]))        
        nodes.append([clientIP, clientPort, newID])
        return
    else:
        print "\n Node already in network!"
    return

    
def updateId(clientIP, clientPort, clientID):
    proxyServer = xmlrpclib.ServerProxy("http://"+clientIP+":"+clientPort+"/", allow_none=True)
    proxyServer.receiver.idUpdate(clientID)
    return
    
    
# Code to update node's ID
def idUpdate(newID):
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
def sendToAll(clientIP, clientPort, clientID):
    global nodes
    for entry in nodes:
        proxyServer = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
        proxyServer.receiver.nodeJoined(clientIP, clientPort, clientID)
    return

        
# Function to acknowledge the joining of a new node to an already existing node
def nodeJoined(clientIP, clientPort, clientID):
    global nodes
    node = [clientIP, clientPort, clientID]
    nodes.append(node)
    print "\n New node with IP: "+str(node[0])+" and port: "+str(node[1])+" added in the network"
    return


# Start Elections
def callForElection():
    global ip
    global port
    global myID
    receivedOK = 0
    timeout_start = time.time()
    timeout = 5
    idList = []
    for entry in nodes:
        idList.append(entry[2]) 
    if myID == max(idList):
        print "\n Highest ID. I'm the Winner!"
        setMasterNode()
    else:
        while time.time() < (timeout_start + timeout):
            print "\n Initiating Master Node Election..."
            for entry in nodes:
                if entry[2] > myID:
                    proxyServer = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
                    proxyServer.receiver.startElection(ip, port, myID)
                    receivedOK = 1                
                    return
            if receivedOK == 0:
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
    print ("\n Usage: start <algorithm (CME or RA)>: "),
    global algorithm    
    algorithm = raw_input()
    if str(algorithm).upper() == "CME":
        centralizedMutualExclusion()
    elif str(algorithm).upper() == "RA":
        buildMasterNode()
        timeout_start = time.time()
        timeout = 20
        while time.time() < (timeout_start + timeout):
            if str(algorithm).upper() == "CME":
                sendStart("CENTRALIZED_MUTUAL_EXCLUSION");
            elif str(algorithm).upper() == "RA":
                sendStart("RICART_AGRAWALA")
    else: print('unknown algorithm: ' + algorithm)
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
    for node in nodes:
        proxyServer = cme.get_proxy_server(node)
        proxyServer.receiver.startDistributedReadWrite(0)
    cme.start([ip, port, myID], nodes)

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


def notifyToTheClient(clientID, ClientPort, nodeID):
    proxyServer = xmlrpclib.ServerProxy("http://"+str(clientID)+":"+str(ClientPort)+"/", allow_none=True)
    proxyServer.receiver.electionResponse(ip, port, myID)
    return
    
    
def electionResponse (nodeIP, nodePort, nodeID):
    print "\nThe node with ID: "+str(nodeIP)+", port: "+str(nodePort)+" and ID: "+str(nodeID)+" has responded to take over the election"
    print "\nI lost the election!"
    return
    
# Notification For Election
def startElection(nodeIP, nodePort, nodeID):
    print "\n Message received: ELECTION from "+str(nodeIP)+", "+str(nodePort)+", "+str(nodeID)+""
    print "\n My ID is higher so I'll start my own election!"
    notifyToTheClient(nodeIP, nodePort, nodeID)
    callForElection()
    return 
    
        
# Set Master Node
def setMasterNode():
    for entry in nodes:
                proxyServer = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
                proxyServer.receiver.masterNodeAnnouncement(myID)
    return
    

# Master Node Confirmation
def masterNodeAnnouncement(clientID):
    print "\n The node with ID: "+str(clientID)+" is the new master"
    return

    
# Logging out
def nodeSignOff(nodeID):
    global nodes
    try:
        for entry in nodes:
            if nodeID == entry[2]:
                nodes.remove(entry)
            print ("\n Node with IP: "+str(entry[0])+" and Port: "+str(entry[1])+" has left the network")
            break
    except Exception:
        print '\n Not able to remove this node'
    return


def startDistributedReadWrite(algorithm_code):
    global algorithm
    if algorithm_code == 0:
        algorithm = "CME"
        cme.start([ip, port, myID], nodes)

def wordStringUpdate(value):
    if algorithm.upper() == "CME":
        threading.Thread(target=cme.receive_word_string, args=(value,)).start()
    else:
        print "ReceiveWordStringRequest"
        
def wordStringRequest(requesterId, time):
    if algorithm.upper() == "CME":
        cme.receive_word_string_request(requesterId, time)
    else:
        print "ReceiveWordStringRequest"

# Server implementation
def server():
    server = SimpleXMLRPCServer((ip, port), allow_none=True)
    server.register_function(initMasterString, "receiver.initMasterString")
    server.register_function(joinRequest, "receiver.joinRequest")
    server.register_function(electionResponse, "receiver.electionResponse")
    server.register_function(nodeSignOff, "receiver.nodeSignOff")
    server.register_function(idUpdate, "receiver.idUpdate")   
    server.register_function(nodeJoined, "receiver.nodeJoined")
    server.register_function(masterNodeAnnouncement, "receiver.masterNodeAnnouncement")
    server.register_function(requestMasterString, "receiver.requestMasterString")
    server.register_function(startElection, "receiver.startElection")
    server.register_function(cme.timeAdvance, "receiver.timeAdvance")
    server.register_function(startDistributedReadWrite, "receiver.startDistributedReadWrite")
    server.register_function(wordStringUpdate, "receiver.wordStringUpdate")
    server.register_function(wordStringRequest, "receiver.wordStringRequest")
    #server.register_function(startThreads, "startThreads")
    print "\nServer started and listening..."
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
    print "["+str(ip)+", "+str(port)+", "+str(myID)+"]"
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
            proxyServer.receiver.joinRequest(str(ip), str(port), int(myID))
            print '\n Connection established'
            continue   
        elif ans == "2":
            callForElection()
            continue
        elif ans == "3":
            startReadWrite()
            break
        elif ans == "4":
            for entry in nodes:
                    proxy = xmlrpclib.ServerProxy("http://"+str(entry[0])+":"+str(entry[1])+"/", allow_none=True)
                    proxy.receiver.nodeSignOff(int(myID))
            nodes = []         
            continue
client()