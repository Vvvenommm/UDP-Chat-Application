# just Server Leader Election
import socket
import pickle
from resources import utils
from multicast import multicast_sender


def form_ring(members):
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    return sorted_ip_ring #type of sorted_ip_ring: list

def get_neighbour(members, current_member_ip, direction='left'):
    current_member_index = members.index(current_member_ip) if current_member_ip in members else -1
    if current_member_index != -1:
        if direction == 'left':
            if current_member_index + 1 == len(members):
                return members[0]
            else:
                return members[current_member_index + 1]
        else:
            if current_member_index - 1 == 0:
                return members[0]
            else:
                return members[current_member_index - 1]
    else:
        return None


def start_leader_election(server_list, leader_server):
    ring = form_ring(server_list)
    neighbour = get_neighbour(ring, leader_server, 'right')
    if neighbour != utils.get_host_ip():
        return neighbour
    else:
        None

def send_leader_message (server_list):
    ring = form_ring(server_list)
    message = pickle.dumps([utils.leader])
    multicast_socket = multicast_sender.multicast_socket
    multicast_socket.sendto(message, utils.MULTICAST_GROUP_ADDRESS)
    return ring