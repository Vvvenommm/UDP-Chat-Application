import socket
import sys
import leader_election
import utils
from time import sleep

# used from Server
def start_heartbeat():
    while True:
        # create the TCP Socket for Heartbeat
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set the socket to broadcast and enable reusing addresses
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(0.5)

        # get own Server Neighbour by using Leader Election algorithm
        my_neighbour = leader_election.neighbour

        #host_address = (utils.neighbour, utils.SERVER_PORT)


        # only executed if a Neighbour is available to whom the Server can establish a connection
        if my_neighbour != "":
            sleep(3)

            # Heartbeat is realized by connecting to the Neighbour
            try:
                sock.connect(utils.host_address)
                print(f'[HEARTBEAT] Neighbour {my_neighbour} response',
                      file=sys.stderr)

            # if connecting to Neighbour was not possible, the Heartbeat failed -> Neighbour crashed
            except:
                # remove crashed Neighbour from Server List
                utils.SERVER_LIST.remove(my_neighbour)

                # used if the crashed Neighbour was the Server Leader
                if utils.leader == my_neighbour:
                    print(f'[HEARTBEAT] Server Leader {utils.neighbour} crashed',
                          file=sys.stderr)
                    utils.leader_crashed = True

                    # assign own IP address as new Server Leader
                    utils.leader = utils.myIP
                    utils.network_changed = True

                # used if crashed Neighbour was a Server Replica
                else:
                    print(f'[HEARTBEAT] Server Replica {my_neighbour} crashed',
                          file=sys.stderr)
                    utils.replica_crashed = True

            finally:
                sock.close()