import pickle
import socket

from time import sleep
from multicast import multicast_sender, multicast_receive
from resources import utils, leader_election, heartbeat
from broadcast import broadcast_listener


# terminal printer for info
def print_participants_details():
    print(f'\n[SERVER LIST]: {utils.SERVER_LIST} ==> CURRENT LEADER: {utils.leader}')
    print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')


# send message to broadcast that server has quit to inform at later point the clients
def send_server_crashed():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = pickle.dumps([utils.RequestType.QUIT_SERVER.value, 'SERVER', 'SERVER HAS QUIT'])
    s.sendto(message, (utils.leader, 10000))


def reset_utils():
    utils.leader_crashed = False
    utils.network_changed = False
    utils.replica_crashed = False


if __name__ == '__main__':
    utils.start_thread(broadcast_listener.start_broadcast_listener, ())

    receiver_exists = multicast_sender.start_sender()

    if not receiver_exists:
        utils.SERVER_LIST.append(utils.myIP)
        utils.leader = utils.myIP
        print(f'[SERVER] - Leader {utils.leader}')

    else:
        print('\n[SERVER] - Leader already exists - updating...')
        leader_election.start_notleader_election()

    utils.start_thread(multicast_receive.start_receiver, ())

    if utils.neighbour != '':
        utils.start_thread(heartbeat.start_heartbeat_listener, ())
        print_participants_details() # print out the list

    while True:
        try:
            if utils.leader == utils.myIP and utils.network_changed or utils.replica_crashed:
                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)
                multicast_sender.start_sender()
                # reset the client_list so that the client join can be freshly filled
                if utils.leader_crashed:
                    utils.CLIENT_LIST = []
                # resetting here the utils
                reset_utils()
                print_participants_details()
                if utils.neighbour != '':
                    utils.start_thread(heartbeat.start_heartbeat_listener, ())

            if utils.leader != utils.myIP and utils.network_changed:
                utils.network_changed = False
                leader_election.start_leader_election(utils.SERVER_LIST, utils.leader)
                print_participants_details()
                if utils.neighbour != '':
                    utils.start_thread(heartbeat.start_heartbeat_listener, ())

        except KeyboardInterrupt:
            print(f'[SERVER] - Closing Server with BROADCAST on IP {utils.myIP} with PORT {utils.SERVER_PORT} in 2 seconds.')
            # send message that server crashed
            if utils.leader == utils.myIP:
                send_server_crashed()
                sleep(2) #let application sleep for 2 seconds, because otherwise the send_server_crashed() messagee is not sent (takes too long)
            utils.sock.close()
            break # needed so it can escape while loop
