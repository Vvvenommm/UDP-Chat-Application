import socket
import sys

from time import sleep
from resources import utils, leader_election

leader_crashed = ''
replica_crashed = ''
network_changed = False


# just server heartbeat
def start_heartbeat():
    #utils.SERVER_LIST.append('192.168.178.27') # add as example
    #utils.SERVER_LIST.append('192.168.178.29') # add as example
    print(f'[HEARTBEAT] started.')
    print(f'[HEARTBEAT] SERVER_LIST: {utils.SERVER_LIST} ')
    neighbour = leader_election.start_leader_election(utils.SERVER_LIST, utils.get_host_ip())
    print(f'[HEARTBEAT] - NEIGHBOUR: {neighbour}')

    # send Leader Message: leader = first member in ring
    ring = leader_election.send_leader_message(utils.SERVER_LIST)
    utils.leader = ring[0]
    print(
        f'{ring[0]} is Leader')  # man sieht schon, dass die Sortierung geklappt hat. Unter Server_list ist .24 als erstes eingegeben, aber .21 ist Leader

    while True:
        # listener socket
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_socket.settimeout(0.5)

        # get own Server Neighbour by using Leader Election algorithm
        neighbour = leader_election.start_leader_election(utils.SERVER_LIST, utils.get_host_ip())
        host_address = (neighbour, utils.SERVER_PORT)

        # only executed if a Neighbour is available to whom the Server can establish a connection
        if neighbour:
            sleep(3)

            # Heartbeat is realized by connecting to the Neighbour
            try:
                listen_socket.connect(host_address)
                print(f'[HEARTBEAT] Neighbour {neighbour} response',
                      file=sys.stderr) #file=sys.stderr = rote Schrift ??

            # if connecting to Neighbour was not possible, the Heartbeat failed -> Neighbour crashed
            except:
                # remove crashed Neighbour from Server List
                utils.SERVER_LIST.remove(neighbour)

                # used if the crashed Neighbour was the Server Leader
                if utils.leader == neighbour:
                    print(f'[HEARTBEAT] Server Leader {neighbour} crashed',
                          file=sys.stderr)
                    utils.leader_crashed = True

                    # assign own IP address as new Server Leader
                    utils.leader = utils.get_host_ip()
                    utils.network_changed = True

                # used if crashed Neighbour was a Server Replica
                else:
                    print(f'[HEARTBEAT] Server Replica {neighbour} crashed',
                          file=sys.stderr)
                    utils.replica_crashed = True

            finally:
                listen_socket.close()
