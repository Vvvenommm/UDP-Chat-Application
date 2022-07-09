import socket
import threading
import enum #zur Verwendung und Implementierung von Aufzählungen
import pickle

UNICODE = 'utf-8'

# SERVER
SERVER_PORT = 10001

# HEARTBEAT
HEARTBEAT_PORT = 10002

# RING
RING_PORT = 10003

# MULTICAST
MULTICAST_GROUP_IP = '224.0.0.0'
MULTICAST_PORT = 10000
MULTICAST_GROUP_ADDRESS = (MULTICAST_GROUP_IP, MULTICAST_PORT)

# PARTICIPANTS
SERVER_LIST = []
CLIENT_LIST = []

# ATTRIBUTES
leader = ''
new_leader = ''
neighbour = ''
leader_crashed = ''
network_changed = False
replica_crashed = False
client_quit = False
new_server = False


# ENUM
class RequestType(enum.Enum):
    SERVER_JOIN = 'SERVER_JOIN'
    CLIENT_JOIN = 'CLIENT_JOIN'
    CLIENT_QUIT = 'CLIENT_QUIT'


# Source: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib?page=1&tab=scoredesc#tab-top
# Get local IP-Address with all details with UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]


# Get host name (IP-Address & Port)
def get_host():
    return sock.getsockname()


def get_host_ip():
    return sock.getsockname()[0]


def get_host_port():
    return sock.getsockname()[1]


# THREADING
def start_thread(target, args):
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()


def handle_pickle(data=None):
    received_data = pickle.loads(data)
    return ReturnObject(received_data[0], received_data[1], received_data[2], received_data[3], received_data[4])


class ReturnObject(object):
    def __init__(self, request_type, received_server_list, received_client_list, received_leader, received_name):
        self.request_type = request_type
        self.received_server_list = received_server_list
        self.received_client_list = received_client_list
        self.received_leader = received_leader
        self.received_name = received_name


def handle_client_message(data=None):
    received_data = pickle.loads(data)
    return ClientMessage(received_data[0], received_data[1], received_data[2])


class ClientMessage(object):
    def __init__(self, chat_type, client_name, client_message):
        self.chat_type = chat_type
        self.client_name = client_name
        self.client_message = client_message
