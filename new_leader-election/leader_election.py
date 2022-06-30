# just Server Leader Election
import socket
import pickle

import utils


def form_ring(members):
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    return sorted_ip_ring  # type of sorted_ip_ring: list


ring = form_ring(utils.SERVER_LIST)
print(ring)


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


neighbour = get_neighbour(ring, utils.myIP, 'left')
print(neighbour)

IP = utils.myIP

election_message = {
    "mIP": IP,
    "isLeader": False
}

ring_ip = '127.0.0.1'
ring_port = 10001
leader_ip = ''
participant = False

ring_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ring_socket.bind((ring_ip, ring_port))
print('Node is up and running at {}:{}'.format(ring_ip, ring_port))

print('\nWaiting to receive election message...\n')

data, address = ring_socket.recvfrom(1024)
election_message = pickle.dumps(data)

if election_message['isLeader']: #wenn von election_message isLeader = True:
    leader_ip = election_message['mIP'] # dann IP aus election_message zu leader_ip abändern
    #hand received election message to left neighbour
    participant = False #d.h.: keine Teilnehmer vorhanden
    ring_socket.sendto(pickle.dumps(election_message, neighbour))

if election_message['mIP'] < utils.myIP and not participant: #wenn mIP von election_message kl. als meine eigene IP Adresse, ändere election_message ab
    new_election_message = {
        "mIP": utils.myIP,  #eigene IP wird eingetragen
        "isLeader": False #bleibt bei False - noch kein Leader gefunden
    }
    participant = True

    #send received election message to left neighbour
    ring_socket.sendto(pickle.dumps(new_election_message, neighbour))

elif election_message['mIP'] > utils.myIP:
    #send received election message to left neighbour
    participant = True
    ring_socket.sendto(pickle.dumps(election_message, neighbour))

elif election_message ['mIP'] == utils.myIP:
    leader_ip = utils.myIP
    new_election_message = {
        "mIP": utils.myIP,
        "isLeader": True
    }
    #send new election message to left neighbour
    participant = False
    ring_socket.sendto(pickle.dumps(new_election_message, neighbour))



