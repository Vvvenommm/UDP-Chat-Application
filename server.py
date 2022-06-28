import socket
import threading
import sys

from broadcast import broadcast_listener
from multicast import multicast_sender, multicast_receive
from resources import utils, heartbeat

# terminal printer for info
def print_participants_details():
    print(f'[SERVER LIST]: {utils.SERVER_LIST} ==> CURRENT LEADER: {utils.leader}')
    print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')

# standardized for creating and starting Threads
def new_thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()

if __name__ == '__main__':

    print('[STARTING SERVER]')
    new_thread(broadcast_listener.start_broadcast_listener, ())

    # Start Multicast Sender, um zu überprüfen, ob es einen Receiver gibt
    receiver_exists = multicast_sender.start_sender()

    if not receiver_exists:
        utils.SERVER_LIST.append(utils.myIP)
        utils.leader = utils.myIP
        print(f'[SERVER LEADER]: {utils.leader}')

    else:
        print(f'[LEADER ALREADY EXISTS] - UPDATING...')

    # Start Multicast Receiver, um Nachrichten empfangen zu können
    new_thread(multicast_receive.start_receiver, ())
    #new_thread(heartbeat.start_heartbeat, ())

    while True:
        try:

            if utils.leader == utils.myIP and utils.network_changed:
                multicast_sender.start_sender()
                #utils.leader_crashed = False
                utils.network_changed = False
                #utils.replica_crashed = ''
                print_participants_details()

            if utils.leader != utils.myIP and utils.network_changed:
                utils.network_changed = False
                print_participants_details()

            if utils.leader == utils.myIP and utils.new_server:
                utils.new_server = False
                print_participants_details()

            if utils.client_joined:
                utils.client_joined = False
                print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')

            if utils.client_quit:
                utils.client_quit = False
                print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')

        except KeyboardInterrupt:
            utils.sock.close()
            print(f'Closing Server on IP {utils.myIP} with PORT {utils.SERVER_PORT}', file=sys.stderr)
            break

#TODO: Code umstrukturieren und vereinfachen -> Teils Done
#TODO: Clients verbinden und Chatten -> Done -> Name des Clients auch mitgeben -> Done, done


#TODO: Heartbeat einbauen
#TODO: Server crash testen und einbauen
#TODO: Clients nach Server Crash mit neuem Server verbinden
