# just Server Leader Election
import socket
import pickle

import utils


def form_ring(members):
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    return sorted_ip_ring  # type of sorted_ip_ring: list


def get_neighbour(members, current_member_ip, direction = 'left'):
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


ring_port = 1001

ring_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ring_socket.bind(('', ring_port))

ring_ip = '127.0.0.1'

ring = form_ring(utils.SERVER_LIST)
print(f'Ring participants: {ring}')
print('Ring is up and running at {}:{}'.format(ring_ip, ring_port))

neighbour = get_neighbour(ring, utils.myIP, 'left')

#if len(utils.SERVER_LIST) == 1:
    # if no other server available
    #print('No neighbour available')
    #utils.leader = utils.myIP
    # no message to other servers necessary (there a none)
    #print(f'[SERVER] - LEADER]: {utils.leader}')

#if len(utils.SERVER_LIST) > 1:
    # if other servers are available: get neighbour
    #neighbour = get_neighbour(ring, utils.myIP, 'left')
    #print(f'My neighbour: {neighbour}')
    # also if there is already a leader (utils.leader != '') we start a new election in case a new member arrived
    #message = pickle.dumps([utils.myIP, False])
    #ring_socket.sendto(message, (neighbour, ring_port))

def start_election():

    while True:
        print('\nWaiting to receive election message...\n')
        try:
            data, addr = ring_socket.recvfrom(1024)
            if data:
                received_messagee = pickle.loads(data)
                check_leader(received_messagee, neighbour)
        except Exception as e:
            print(e)
            break

    print(f'My neighbour: {neighbour}')
    # also if there is already a leader (utils.leader != '') we start a new election in case a new member arrived
    message = pickle.dumps([utils.myIP, False])
    ring_socket.sendto(message, (neighbour, ring_port))

def check_leader(election_message, my_left_neighbour):
    ip_message = election_message[0]
    existing_leader = election_message[1]

    if ip_message < utils.myIP:  # check if ip from neighbour is smaller than own ip address
        # True: new_election_message: own IP is leader
        # existing_leader still False
        new_election_message = pickle.dumps([utils.myIP, existing_leader])
        # send new election message to left neighbour
        ring_socket.sendto(new_election_message, my_left_neighbour)

    if ip_message > utils.myIP:
        # True: myIP address is no leader
        # send received election message to left neighbour
        ring_socket.sendto(election_message, my_left_neighbour)

    if ip_message == utils.myIP and existing_leader == False:
        existing_leader = True
        new_election_message = pickle.dumps([utils.myIP, existing_leader])
        # send new election message to left neighbour
        ring_socket.sendto(new_election_message, my_left_neighbour)

    if ip_message == utils.myIP and existing_leader == True:
        # now every member in the ring has received the election_message that there is a new Leader
        # set new_leader in utils
        utils.leader = utils.myIP
        # write new leader in comando
        print(f'[SERVER] - LEADER]: {utils.leader}')
