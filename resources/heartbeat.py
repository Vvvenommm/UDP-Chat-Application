import socket
import sys
from time import sleep
from resources import utils

# create the UDP Socket for Heartbeat
heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the socket to broadcast and enable reusing addresses
heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
heartbeat_socket.settimeout(0.5)


def start_heartbeat_listener():
    print(f'\n[HEARTBEAT] - started on IP: {utils.get_host_ip()} on PORT: {utils.HEARTBEAT_PORT}'
          f'\n[HEARTBEAT] - waiting for SERVERs...\n')
    while True:
        neighbour_crash_count = 0

        # get own Server Neighbour by using Leader Election algorithm
        # host_address = (utils.neighbour, utils.SERVER_PORT)
        # only executed if a Neighbour is available to whom the Server can establish a connection
        if utils.neighbour:
            #heartbeat_socket.bind(('', utils.HEARTBEAT_PORT))
            heartbeat_socket.sendto(b'PING', (utils.neighbour, utils.HEARTBEAT_PORT))

            while True:
                try:
                    data, addr = heartbeat_socket.recvfrom(1024)
                    if data:
                        # since HEARTBEAT is working over UDP we could receive from every SERVER a HEARTBEAT
                        # therefore we have a check if the given neighbour matches the message we are receiving
                        # from the heartbeat socket of the neighbour server
                        # addr[0] = IP-Address
                        # addr[1] = Port
                        if utils.neighbour == addr[0]:
                            print(f'[HEARTBEAT] - Neighbour {utils.neighbour} response')
                            heartbeat_socket.sendto(b'PING', addr)
                            neighbour_crash_count = 0
                            sleep(1)
                        else:
                            None

                except Exception as e:
                    sleep(1.5)
                    print(f'[HEARTBEAT] - connection lost to Neighbour: {utils.neighbour} with exception: {e}')
                    neighbour_crash_count += 1
                    # due to UDP we are counting the neigbour crash. It is getting resetted everytime we receive a
                    # PING from the neigbour if we do not receive any PING we count till 2 and remove the SERVER and
                    # do the respective steps (leader_election, etc.)
                    if neighbour_crash_count > 2:
                        # remove crashed Neighbour from Server List
                        utils.SERVER_LIST.remove(utils.neighbour)

                        # used if the crashed Neighbour was the Server Leader
                        if utils.leader == utils.neighbour:
                            print(f'[HEARTBEAT] - Server Leader {utils.neighbour} crashed')
                            utils.leader_crashed = True

                            # assign own IP address as new Server Leader
                            utils.leader = utils.myIP
                            utils.network_changed = True
                            break

                        # used if crashed Neighbour was a Server Replica
                        else:
                            print(f'[HEARTBEAT] - Server Replica {utils.neighbour} crashed')
                            utils.replica_crashed = True
                            break

            utils.neighbour = ''  # reset neighbour to escape while loop and reassign in next iteration
        # heartbeat_socket.close() # close broadcoast_socket to prevent errors
        break  # escape while loop
