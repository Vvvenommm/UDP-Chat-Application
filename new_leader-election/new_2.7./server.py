import sys
import broadcast_listener
import multicast_sender
import multicast_receive
import utils
import heartbeat
import leader_election

# terminal printer for info
def print_participants_details():
    print(f'[SERVER LIST]: {utils.SERVER_LIST} ==> CURRENT LEADER: {utils.leader}')
    print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')

if __name__ == '__main__':
    utils.start_thread(broadcast_listener.start_broadcast_listener, ())

    # Start Multicast Sender, um zu überprüfen, ob es einen Receiver gibt
    receiver_exists = multicast_sender.start_sender()

    if not receiver_exists:
        utils.SERVER_LIST.append(utils.myIP)

    else:
        # leader_election.start_election(True)
        print(f'[LEADER ALREADY EXISTS] - UPDATING...')

    leader_election.start_election()

    # Start Multicast Receiver, um Nachrichten empfangen zu können
    utils.start_thread(multicast_receive.start_receiver, ())


    # Start Heartbeat for getting neighbours
    utils.start_thread(heartbeat.start_heartbeat, ())

    while True:
        try:

            if utils.leader == utils.myIP and utils.network_changed or utils.replica_crashed:
                multicast_sender.start_sender()
                utils.leader_crashed = False
                utils.network_changed = False
                utils.replica_crashed = ''
                print_participants_details()

            if utils.leader != utils.myIP and utils.network_changed:
                utils.network_changed = False
                print_participants_details()

            if utils.leader == utils.myIP and utils.new_server:
                utils.new_server = False
                print_participants_details()

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
