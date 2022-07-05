import sys

from multicast import multicast_sender, multicast_receive
from resources import utils, leader_election, heartbeat
from broadcast import broadcast_listener

# terminal printer for info
def print_participants_details(): #Funktion, um über aktuelle Server, den Leader und die momentanen Clients zu informieren
    print(f'[SERVER LIST]: {utils.SERVER_LIST} ==> CURRENT LEADER: {utils.leader}')
    print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')

#start
if __name__ == '__main__':
    utils.start_thread(broadcast_listener.start_broadcast_listener, ()) #Broadcast Listener wird mit neuem Thread gestartet

    # Start Multicast Sender, um zu überprüfen, ob es einen Receiver gibt
    receiver_exists = multicast_sender.start_sender()
    # 1. Nachricht wird vorbereitet. Enthält ???
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
        print(f'[SERVER] - LEADER]: {utils.leader}') #neuer Leader wird ausgegeben

    else: #heißt vorherige Funktion gibt True aus:
        print('[LEADER ALREADY EXISTS] - UPDATING...')
        print('Leader_election hast started ...')
        leader_election.start_notleader_election()

        """
        def start_notleader_election():
            while True:
                if utils.new_leader != '':
                    break
                else:
                    print('\nWaiting to receive election message...\n')
                    try:
                        data, addr = ring_socket.recvfrom(1024)
                        if data:
                            print(f'DATA: {pickle.loads(data)}')
                            received_message = pickle.loads(data)
                            start_leader_election(received_message[1], utils.myIP)
                            utils.SERVER_LIST = received_message[1]
                    except Exception as e:
                        print(e)
                        breaks
            """

    # Start Multicast Receiver, um Nachrichten empfangen zu können
    utils.start_thread(multicast_receive.start_receiver, ())

    if utils.neighbour != '':
        utils.start_thread(heartbeat.start_heartbeat_listener())

    while True:
        try:

            if utils.leader == utils.myIP and utils.network_changed or utils.replica_crashed:
                multicast_sender.start_sender()
                print('Leader_election hast started ...')
                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)
                utils.leader_crashed = False
                utils.network_changed = False
                utils.replica_crashed = ''
                print_participants_details()
                if utils.neighbour != '':
                    utils.start_thread(heartbeat.start_heartbeat_listener())

            if utils.leader != utils.myIP and utils.network_changed:
                utils.network_changed = False
                print('Leader_election hast started 2...')
                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)
                print_participants_details()
                if utils.neighbour != '':
                    utils.start_thread(heartbeat.start_heartbeat_listener())

            if utils.leader == utils.myIP and utils.new_server:
                utils.new_server = False
                print('Leader_election hast started 3...')
                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)
                print_participants_details()
                if utils.neighbour != '':
                    utils.start_thread(heartbeat.start_heartbeat_listener())

            if utils.client_quit:
                utils.client_quit = False
                print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')

        except KeyboardInterrupt:
            utils.sock.close()
            print(f'Closing Server on IP {utils.myIP} with PORT {utils.SERVER_PORT}', file=sys.stderr)
            break

#TODO: Code umstrukturieren und vereinfachen -> Teils Done
#TODO: Clients verbinden und Chatten -> Done -> Name des Clients auch mitgeben -> Done, done


#TODO: Heartbeat einbauen -> gehört zusammen: #TODO: Server crash testen und einbauen
#TODO: Clients nach Server Crash mit neuem Server verbinden
