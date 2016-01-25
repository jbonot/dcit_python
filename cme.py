from threading import Thread
from time import sleep
import xmlrpclib
import Queue
import random

words = ['pumpkin', 'potato', 'rice', 'coconut', 'beet', 'corn', 'spinach', 'hazelnut']
request_queue = Queue.Queue()
done_nodes = []
appended = []
awaiting_final_string = False
next_request_time = 0
master_node = None
node_list = None
ip = None
port = None
id = None
word_string = ''

def find_node_by_id(value):
    nodes = [n for n in node_list if n[2] == value]
    return nodes[0] if len(nodes) == 1 else None

def timeAdvance(time):
    thread = Thread(target=time_advance_grant, args=(time, master_node))
    thread.start()

def is_master_node():
    return master_node[0] == ip and master_node[1] == port and master_node[2] == id

def get_proxy_server(node):
    return xmlrpclib.ServerProxy("http://"+str(node[0])+":"+str(node[1])+"/", allow_none=True)

def get_random_waiting_time():
    return random.randint(1,9)

def request_final_string():
    return

def request_word_string(node, time):
    proxy_server = get_proxy_server(node)
    proxy_server.receiver.wordStringRequest(id, time)

def check_request_queue():
    print('Checking request queue')
    if not serviced_node == None:
        print('Error: Serviced node is not null')
        return
    node = request_queue.get()
    print('Now servicing ' + str(node))
    get_proxy_server(node).receiver.wordStringUpdate(word_string)

def check_final_string(value):
    return

def append_random_word(value):
    tokens = value.split()
    new_word = words[random.randint(0, len(words) - 1)]
    value += ('' if len(tokens) == 0 else ' ') + new_word
    appended.append([new_word, len(tokens)])
    return value

def receive_word_string(value):
    global word_string, serviced_node, awaiting_final_string
    if is_master_node():
        print('Updated word string: ' + value)
        word_string = value
        print('Finished servicing ' + str(serviced_node))
        serviced_node = None
        check_request_queue()
    else:
        if awaiting_final_string:
            check_final_string(value)
        else:
            global next_request_time
            print('old string: ' + value)
            word_string = append_random_word(value)
            print('new string: ' + word_string)
            seconds = get_random_waiting_time()
            print('Waiting for ' + str(seconds) + ' seconds')
            next_request_time += seconds
            get_proxy_server(master_node).receiver.wordStringUpdate(word_string)
    
def receive_word_string_request(requester, time):
    node = find_node_by_id(requester)
    if node == None:
        print('Unknown ID: ' + str(requester))
        return
    if is_master_node():
        print('Receive request from ' + str(node))
        request_queue.put(node)
        check_request_queue()

def time_advance_grant(time, master):
    global awaiting_final_string, next_request_time
    print('Time: ' + str(time))
    if (time == 20):
        awaiting_final_string = True
        request_final_string()
        return
    if (next_request_time == time):
        print(master)
        request_word_string(master, time)

def timer():
    for time in range(1,21):
        sleep(1)
        print('Advance time to: ' + str(time))
        for node in node_list:
            print('sending to ' + str(node))
            proxyServer = get_proxy_server(node)
            proxyServer.receiver.timeAdvance(time)

def start(node, nodes):
    global master_node, ip, port, id, node_list
    print nodes
    ip = node[0]
    port = node[1]
    id = node[2]
    master_node = max(max([n[2] for n in nodes]), id)
    master_node = [ip, port, id] if master_node == id else [n for n in nodes if n[2] == master_node][0]
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
    