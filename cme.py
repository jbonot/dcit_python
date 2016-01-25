from threading import Thread
from time import sleep
import xmlrpclib
import Queue
import random

request_queue = Queue.Queue()
done_nodes = []
awaiting_final_string = False
next_request_time = 0
master_node = None
node_list = None
ip = None
port = None
id = None

def timeAdvance(time):
    thread = Thread(target=time_advance_grant, args=(time,))
    thread.start()

def get_proxy_server(ip, port):
    return xmlrpclib.ServerProxy("http://"+ip+":"+str(port)+"/", allow_none=True)

def get_random_waiting_time():
    return random.randint(1,9)

def request_final_string():
    return

def request_word_string(node):
    return

def time_advance_grant(time):
    global awaiting_final_string, next_request_time
    print('Time: ' + str(time))
    if (time == 20):
        awaiting_final_string = True
        request_final_string()
        return
    if (next_request_time == time):
        request_word_string(master_node)

def is_master_node():
    return master_node[0] == ip and master_node[1] == port and master_node[2] == id

def timer():
    for time in range(1,21):
        sleep(1)
        print('Advance time to: ' + str(time))
        for ip, port, id in node_list:
            print('sending to ' + str([ip, port, id]))
            proxyServer = get_proxy_server(ip, port)
            proxyServer.receiver.timeAdvance(time)

def start(node, nodes):
    global master_node, ip, port, id, node_list
    print nodes
    ip = node[0]
    port = node[1]
    id = node[2]
    master_node = max(max([n[2] for n in nodes]), id)
    master_node = [ip, port, id] if master_node == id else [n for n in nodes if n[2] == master_node]
    print('master node: ' + str(master_node))
    node_list = nodes
    global next_request_time, serviced_node
    print('Starting with algorithm: Centralized Mutual Exclusion')
    print('IP: ' + str(ip) + ' Port: ' + str(port) + ' ID: ' + str(id))
    print('------------')
    next_request_time = -1
    serviced_node = None
    while not request_queue.empty(): request_queue.get()
    done_nodes = []
    if is_master_node():
        thread = Thread(target=timer)
        thread.start()
    else:
        next_request_time = get_random_waiting_time()
        print('Waiting for ' + str(next_request_time) + ' seconds')
    