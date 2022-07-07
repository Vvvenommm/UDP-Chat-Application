import os
import pickle
import socket

from time import sleep
from multicast import multicast_sender, multicast_receive
from resources import utils, leader_election, heartbeat
from broadcast import broadcast_listener

# terminal printer for info
def print_participants_details(): #Funktion, um über aktuelle Server, den Leader und die momentanen Clients zu informieren
    print(f'\n[SERVER LIST]: {utils.SERVER_LIST} ==> CURRENT LEADER: {utils.leader}')
    print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')

def send_server_crashed():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP-Socket für Nachrichtenaustausch
    message = pickle.dumps(['QUIT_SERVER', 'SERVER', 'SERVER HAS QUIT'])
    s.sendto(message, (utils.leader, 10000))

#start
if __name__ == '__main__':
    utils.start_thread(broadcast_listener.start_broadcast_listener, ()) #Broadcast Listener wird mit neuem Thread gestartet

    """
    -------------------------------
    def start_thread(target, args):
        threading.Thread(target=target, args=args).start()
-------------------------------
    """
    
    # Start Multicast Sender, um zu überprüfen, ob es einen Receiver gibt
    receiver_exists = multicast_sender.start_sender()
    # 1. Nachricht wird vorbereitet. Enthält ??? SERVER_JOIN.value aus Enum, aktuelle SERVER_LIST, aktuelle CLIENT_LIST, aktuellen Leader laut utils
    # 2. Nachricht wird an die MULTICAST_GROUP_ADDRESS gesendet
    # 3. Warten auf Nachrichten von allen Teilnehmern. Falls ja, wird _return True_ gemacht
    # 4. Falls keine Antwort kommt: _return False_

    """
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
            return False
    """

    if not receiver_exists: #Falls die vorherige Funktion False ausgibt:
        utils.SERVER_LIST.append(utils.myIP) #Server fügt eigene Adresse an _SERVER_LIST_ an
        utils.leader = utils.myIP #neuer Server ernennt sich selbst zum Leader
        print(f'[SERVER] - Leader {utils.leader}') #neuer Leader wird ausgegeben

    else: #heißt vorherige Funktion gibt True aus: es muss schon einen Leader geben, da mindestens ein weiterer Server vorhanden ist
        print('\n[SERVER] - Leader already exists - updating...')
        leader_election.start_notleader_election()

        """
        def start_notleader_election():
            while True:
                if utils.new_leader != '': # falls es keinen neuen Leader gibt
                    break
                else:
                    print('\nWaiting to receive election message...\n')
                    try:
                        data, addr = ring_socket.recvfrom(1024)
                        if data:
                            print(f'DATA: {pickle.loads(data)}')
                            received_message = pickle.loads(data)
                            start_leader_election(received_message[1], utils.myIP) #neue Leader election wird gestartet; Pos. 1 von received_message enthält Server List. Warum wird die eigene IP als Leader angegeben?

                            ----------------------------------------------------------------	
                                def start_leader_election(server_list, leader_server):    
                                    utils.new_leader = '' #Variable _new_leader wird auf leer gesetzt
                                    ring = form_ring(server_list) #Ring wird aus vorhandenen Servern gebildet
                                    -------------------------------
                                        def form_ring(members):
                                            sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
                                            sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring] 
                                            return sorted_ip_ring #type of sorted_ip_ring: listed
                                    -------------------------------
                                    neighbour = get_neighbour(ring, leader_server, 'left') #neighbour wird identifiziert
                                    -------------------------------
                                        def get_neighbour(members, current_member_ip, direction='left'):
                                            current_member_index = members.index(current_member_ip) if current_member_ip in members else -1 # ??
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
                                    -------------------------------
                                    if neighbour != utils.get_host_ip(): # ?? Was genau heißt in diesem Zusammenhang host ??
                                        if neighbour: #falls Nachbar vorhanden
                                            print(f'My neighbour: {neighbour}')
                                            utils.neighbour = neighbour #Nachbar wird auch in Variable in utils gespeichert
                                            message = pickle.dumps([utils.myIP, server_list, False]) #Nachricht mit eigener IP, Server-Liste und ?? FALSE ?? wird gepackt
                                            ring_socket.sendto(message, (neighbour, utils.RING_PORT)) #Nachricht wird an den Ring-Socket geschickt
                                            print('Election message to neighbour was sent...')
                                            while True:
                                                if utils.new_leader != '': #sobald es einen neuen Leader gibt ist die election beendet
                                                    print('Leader_election FINISHED.')
                                                    break
                                                else:
                                                    print('\nWaiting to receive election message...\n')
                                                    try:
                                                        data, addr = ring_socket.recvfrom(1024) # auf Daten vom Ring-Socket warten
                                                        if data:
                                                            print(f'DATA: {pickle.loads(data)}')
                                                            received_message = pickle.loads(data)
                                                            check_leader(received_message, (neighbour, utils.RING_PORT)) # ?? Was passiert hier ??
                                                    except Exception as e:
                                                        print(e)
                                                        break
                                    else:
                                        None
                            --------------------------------------------------------------------


                            utils.SERVER_LIST = received_message[1]
                    except Exception as e:
                        print(e)
                        breaks
            """

    # Start Multicast Receiver, um Nachrichten empfangen zu können
    utils.start_thread(multicast_receive.start_receiver, ())

    if utils.neighbour != '': # falls keiner existiert?
        utils.start_thread(heartbeat.start_heartbeat_listener, ())
        print_participants_details() # print out the list

    server_crashed = False

    while True:

        try:

            if utils.leader == utils.myIP and utils.network_changed or utils.replica_crashed:
                multicast_sender.start_sender()

                """
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
                        return False_
                """

                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)

                """
                def start_leader_election(server_list, leader_server):
                    utils.new_leader = '' #Variable _new_leader wird auf leer gesetzt
                    ring = form_ring(server_list) #Ring wird aus vorhandenen Servern gebildet
                    neighbour = get_neighbour(ring, leader_server, 'left') #neighbour wird identifiziert
                    if neighbour != utils.get_host_ip(): # ?? Was genau heißt in diesem Zusammenhang host ??
                        if neighbour: #falls Nachbar vorhanden
                            print(f'My neighbour: {neighbour}')
                            utils.neighbour = neighbour #Nachbar wird auch in Variable in utils gespeichert
                            message = pickle.dumps([utils.myIP, server_list, False]) #Nachricht mit eigener IP, Server-Liste und ?? FALSE ?? wird gepackt
                            ring_socket.sendto(message, (neighbour, utils.RING_PORT)) #Nachricht wird an den Ring-Socket geschickt
                            print('Election message to neighbour was sent...')
                            while True:
                                if utils.new_leader != '': #sobald es einen neuen Leader gibt ist die election beendet
                                    print('Leader_election FINISHED.')
                                    break
                                else:
                                    print('\nWaiting to receive election message...\n')
                                    try:
                                        data, addr = ring_socket.recvfrom(1024) # auf Daten vom Ring-Socket warten
                                        if data:
                                            print(f'DATA: {pickle.loads(data)}')
                                            received_message = pickle.loads(data)
                                            check_leader(received_message, (neighbour, utils.RING_PORT)) # ?? Was passiert hier ??
                                    except Exception as e:
                                        print(e)
                                        break
                    else:
                        NoneMetadataError
                """

                utils.leader_crashed = False
                utils.network_changed = False
                utils.replica_crashed = ''
                print_participants_details()

                """
                def print_participants_details(): #Funktion, um über aktuelle Server, den Leader und die momentanen Clients zu informieren
                    print(f'[SERVER LIST]: {utils.SERVER_LIST} ==> CURRENT LEADER: {utils.leader}')
                    print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')
                """

                if utils.neighbour != '':
                    utils.start_thread(heartbeat.start_heartbeat_listener, ())

            if utils.leader != utils.myIP and utils.network_changed:
                utils.network_changed = False
                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)
                print_participants_details()
                if utils.neighbour != '':
                    utils.start_thread(heartbeat.start_heartbeat_listener, ())

            if utils.leader == utils.myIP and utils.new_server:
                utils.new_server = False
                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)
                print_participants_details()
                if utils.neighbour != '':
                    utils.start_thread(heartbeat.start_heartbeat_listener, ())

            if utils.client_quit:
                utils.client_quit = False
                print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')

        except KeyboardInterrupt:
            print(f'[SERVER] - Closing Server with BROADCAST on IP {utils.myIP} with PORT {utils.SERVER_PORT} in 2 seconds.')
            if utils.leader == utils.myIP:
                send_server_crashed()
                sleep(2) #let application sleep for 2 seconds, because otherwise the send_server_crashed() messagee is not sent (takes too long)
            utils.sock.close()
            break # needed so it can escape while loop
