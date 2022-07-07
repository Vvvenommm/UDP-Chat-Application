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

    # Start Multicast Sender, um zu überprüfen, ob es einen Receiver gibt
    receiver_exists = multicast_sender.start_sender()

    if not receiver_exists: #Falls die vorherige Funktion False ausgibt:
        utils.SERVER_LIST.append(utils.myIP) #Server fügt eigene Adresse an _SERVER_LIST_ an
        utils.leader = utils.myIP #neuer Server ernennt sich selbst zum Leader
        print(f'[SERVER] - Leader {utils.leader}') #neuer Leader wird ausgegeben

    else: #heißt vorherige Funktion gibt True aus: es muss schon einen Leader geben, da mindestens ein weiterer Server vorhanden ist
        print('\n[SERVER] - Leader already exists - updating...')
        leader_election.start_notleader_election()

    # Start Multicast Receiver, um Nachrichten empfangen zu können
    utils.start_thread(multicast_receive.start_receiver, ())

    if utils.neighbour != '': # falls keiner existiert?
        utils.start_thread(heartbeat.start_heartbeat_listener, ())
        print_participants_details() # print out the list

    while True:

        try:

            if utils.leader == utils.myIP and utils.network_changed or utils.replica_crashed:
                multicast_sender.start_sender()

                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)

                utils.leader_crashed = False
                utils.network_changed = False
                utils.replica_crashed = ''
                print_participants_details()
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
