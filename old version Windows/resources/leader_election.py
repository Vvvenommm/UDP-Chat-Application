# just Server Leader Election
import socket
import pickle
from resources import utils

ring_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ring_socket.bind(('', utils.RING_PORT))


def form_ring(members):
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    return sorted_ip_ring  # type of sorted_ip_ring: list


def get_neighbour(members, current_member_ip, direction='left'):
    current_member_index = members.index(current_member_ip) if current_member_ip in members else -1  # ??
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
    print(f'[SERVER] - Leader election has started')
    utils.new_leader = ''  # Variable _new_leader wird auf leer gesetzt
    ring = form_ring(server_list)  # Ring wird aus vorhandenen Servern gebildet
    neighbour = get_neighbour(ring, leader_server, 'left')  # neighbour wird identifiziert
    if neighbour != utils.get_host_ip():  # ?? Was genau heißt in diesem Zusammenhang host ??
        if neighbour:  # falls Nachbar vorhanden
            print(f'[SERVER] - My neighbour: {neighbour}')
            utils.neighbour = neighbour  # Nachbar wird auch in Variable in utils gespeichert
            message = pickle.dumps(
                [utils.myIP, server_list, False])  # Nachricht mit eigener IP, Server-Liste und ?? FALSE ?? wird gepackt
            ring_socket.sendto(message, (neighbour, utils.RING_PORT))  # Nachricht wird an den Ring-Socket geschickt
            print('[SERVER] - Election message to neighbour sent...')
            while True:
                if utils.new_leader != '':  # sobald es einen neuen Leader gibt ist die election beendet
                    print('[SERVER] - Leader election FINISHED.')
                    break
                else:
                    print('\n[SERVER] - Waiting to receive election message...\n')
                    try:
                        data, addr = ring_socket.recvfrom(1024)  # auf Daten vom Ring-Socket warten
                        if data:
                            received_message = pickle.loads(data)
                            check_leader(received_message, (neighbour, utils.RING_PORT))  # ?? Was passiert hier ??
                    except Exception as e:
                        print(e)
                        break
    else:
        None


def start_notleader_election():
    print(f'[SERVER] - Leader election has started')
    while True:
        if utils.new_leader != '':
            break
        else:
            print('\n[SERVER] - Waiting to receive election message...\n')
            try:
                data, addr = ring_socket.recvfrom(1024)
                if data:
                    print(f'DATA: {pickle.loads(data)}')
                    received_message = pickle.loads(data)
                    start_leader_election(received_message[1], utils.myIP)
                    utils.SERVER_LIST = received_message[1]
                    break
            except Exception as e:
                print(e)
                break


def check_leader(election_message, my_left_neighbour):
    ip_message = election_message[0]
    existing_leader = election_message[2]

    if ip_message < utils.myIP:  # check if ip from neighbour is smaller than own ip address
        # True: new_election_message: own IP is leader
        # existing_leader still False
        # election_message[1] = server_list - we need to add to have 3 message elements
        new_election_message = pickle.dumps([utils.myIP, election_message[1], existing_leader])
        # send new election message to left neighbour
        ring_socket.sendto(new_election_message, my_left_neighbour)

    if ip_message > utils.myIP:
        # True: myIP address is no leader
        # send received election message to left neighbour
        new_election_message = pickle.dumps(election_message)
        ring_socket.sendto(new_election_message, my_left_neighbour)

    if ip_message == utils.myIP and not existing_leader:
        existing_leader = True
        # election_message[1] = server_list - we need to add to have 3 message elements
        new_election_message = pickle.dumps([utils.myIP, election_message[1], existing_leader])
        # send new election message to left neighbour
        ring_socket.sendto(new_election_message, my_left_neighbour)

    if ip_message == utils.myIP and existing_leader:
        # now every member in the ring has received the election_message that there is a new Leader
        # set new_leader in utils
        utils.leader = utils.myIP
        # write new leader in comando
        utils.new_leader = utils.myIP
        print(f'[SERVER] - Leader {utils.leader}') #neuer Leader wird ausgegeben
        leader_message = pickle.dumps([utils.leader, '', True])
        ring_socket.sendto(leader_message, my_left_neighbour)
        leader_message_to_clients = pickle.dumps([utils.leader])
        multicast_sender.multicast_socket.sendto(leader_message_to_clients, utils.MULTICAST_GROUP_ADDRESS)
        print('Sent Leader message to clients by Multicast group address')

    if existing_leader and ip_message != utils.myIP:
        utils.new_leader = ip_message
        utils.leader = ip_message
        print(f'[SERVER] - Leader {utils.leader}') #neuer Leader wird ausgegeben
