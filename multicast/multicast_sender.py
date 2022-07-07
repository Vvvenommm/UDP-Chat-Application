import socket
import struct
import pickle

from time import sleep
from resources import utils

# Create the datagram socket
# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
multicast_socket.settimeout(1)

# Set the time-to-live for messages to 1 so they do not
# go past the local network segment.
ttl = struct.pack('b', 1)
multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

#source: https://pymotw.com/3/socket/multicast.html
def start_sender():
    sleep(1)

    # Send data to the multicast group
    message = pickle.dumps([utils.RequestType.SERVER_JOIN.value, utils.SERVER_LIST, utils.CLIENT_LIST, utils.leader, ''])
    multicast_socket.sendto(message, utils.MULTICAST_GROUP_ADDRESS)

    try:
        # Look for responses from all recipients
        multicast_socket.recvfrom(1024)
        return True

    except socket.timeout:
        print('Here Error 6')
        return False

#finally:
 #   print('closing socket')
  #  sock.close()

def join_multicast_group(name):
    # Send data to the multicast group
    message = pickle.dumps([utils.RequestType.CLIENT_JOIN.value, '', utils.CLIENT_LIST, '', name])
    print(pickle.loads(message))
    multicast_socket.sendto(message, utils.MULTICAST_GROUP_ADDRESS)

    while True:
        # try to get Server Leader
        try:
            utils.leader = ''
            data, address = multicast_socket.recvfrom(1024)
            print(pickle.loads(data))
            print(address)
            received_leader = pickle.loads(data)[0]
            if received_leader == address[0]:
                utils.leader = received_leader
            else:
                utils.leader = address[0]
            return True

        except socket.timeout:
            return False