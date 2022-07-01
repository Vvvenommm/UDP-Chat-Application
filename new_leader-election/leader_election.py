# just Server Leader Election
import socket
import pickle

import utils


def form_ring(members):
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    return sorted_ip_ring  # type of sorted_ip_ring: list


def get_neighbour(members: object, current_member_ip: object, direction: object = 'left') -> object:
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



def start_election(no_existing_leader):

    IP = ''

    election_message = pickle.dumps([IP, no_existing_leader])

    ring_ip = '127.0.0.1'
    ring_port = 1001
    participant = False

    ring = form_ring(utils.SERVER_LIST)
    print(f'Ring participants: {ring}')

    if election_message[1]: # if no_existing_leader = True
        print('No neighbour available')
        neighbour = ''

    if not election_message[1]:
        neighbour = get_neighbour(ring, utils.myIP, 'left')
        print(f'My neighbour: {neighbour}')

    ring_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ring_socket.bind((ring_ip, ring_port))
    print('Ring is up and running at {}:{}'.format(ring_ip, ring_port))

    print('\nWaiting to receive election message...\n')

    data, addr = ring_socket.recvfrom(1024)
    election_message = pickle.dumps([data, addr]) #Problem!



    if election_message[1]:  # wenn no_election_leader = True:
        election_message[0] = utils.leader  # dann IP aus election_message zu leader_ip abändern
        participant = False  # d.h.: keine Teilnehmer vorhanden
        print(f'[SERVER] - LEADER]: {utils.leader}')
        # hand received election message to left neighbour, if available
        # kann man rausnehmen, da es nur stattfindet, wenn no_election_leader = True - also definitiv kein
        # neighbour
         # if neighbour != '':
         # ring_socket.sendto(election_message, neighbour)

    if not election_message [1] :
        if election_message[0] < utils.myIP:
            # wenn mIP von election_message kl. als meine eigene IP Adresse, ändere election_message ab
            new_election_message = pickle.dumps([utils.myIP, no_existing_leader])

            # send received election message to left neighbour
            ring_socket.sendto(new_election_message, neighbour)

        if election_message[0] > utils.myIP:
            # send received election message to left neighbour
            ring_socket.sendto(election_message, neighbour)

        if election_message[0] == utils.myIP:
            utils.leader = utils.myIP
            new_election_message = pickle.dumps([utils.myIP, no_existing_leader])

            # send new election message to left neighbour
            ring_socket.sendto(new_election_message, neighbour)
