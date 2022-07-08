import socket
import struct
import pickle
from resources import utils


def join_multicast_group(name):
    multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_socket.settimeout(1)

    # Set the time-to-live for messages to 1 so they do not
    # go past the local network segment.
    ttl = struct.pack('b', 1)
    multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    # Send data to the multicast group
    message = pickle.dumps([utils.RequestType.CLIENT_JOIN.value, '', utils.CLIENT_LIST, '', name])
    multicast_socket.sendto(message, utils.MULTICAST_GROUP_ADDRESS)

    while True:
        # try to get Server Leader
        try:
            data, address = multicast_socket.recvfrom(1024)
            received_leader = pickle.loads(data)[0]
            utils.leader = received_leader
            return True

        except socket.timeout:
            return False