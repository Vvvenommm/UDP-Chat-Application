import socket
import sys
from time import sleep
from resources import utils


def start_heartbeat_listener():
    print(f'[HEARTBEAT] - started on IP: {utils.get_host_ip()} on PORT: {utils.HEARTBEAT_PORT}')
    print('[HEARTBEAT] - waiting for SERVERs...')
    while True:
        neigbour_crash_count = 0
        is_crashed = False
        # get own Server Neighbour by using Leader Election algorithm
        host_address = (utils.neighbour, utils.SERVER_PORT)
        # only executed if a Neighbour is available to whom the Server can establish a connection
        if host_address:

            # create the UDP Socket for Heartbeat
            heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Set the socket to broadcast and enable reusing addresses
            heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            heartbeat_socket.settimeout(0.5)

            heartbeat_socket.bind(('', utils.HEARTBEAT_PORT))

            heartbeat_socket.sendto(b'PING', (utils.neighbour, utils.HEARTBEAT_PORT))

            while True:
                try:
                    data, addr = heartbeat_socket.recvfrom(1024)
                    if data:
                        sleep(3)
                        print(f'[HEARTBEAT] - Neighbour {utils.neighbour} response',
                              file=sys.stderr)
                        heartbeat_socket.sendto(b'PING', addr)
                        neigbour_crash_count = 0
                    else:
                        print('Closing receive')
                        heartbeat_socket.close()
                        break

                except Exception as e:
                    sleep(3)
                    print(f'[HEARTBEAT] - connection lost to Neighbour: {utils.neighbour} with exception: {e}')
                    neigbour_crash_count += 1

                    if neigbour_crash_count > 5:
                        # remove crashed Neighbour from Server List
                        utils.SERVER_LIST.remove(utils.neighbour)

                        # used if the crashed Neighbour was the Server Leader
                        if utils.leader == utils.neighbour:
                            print(f'[HEARTBEAT] - Server Leader {utils.neighbour} crashed',
                                  file=sys.stderr)
                            utils.leader_crashed = True

                            # assign own IP address as new Server Leader
                            utils.leader = utils.myIP
                            utils.network_changed = True
                            heartbeat_socket.close()
                            break

                        # used if crashed Neighbour was a Server Replica
                        else:
                            print(f'[HEARTBEAT] - Server Replica {utils.neighbour} crashed',
                                  file=sys.stderr)
                            utils.replica_crashed = True
                            heartbeat_socket.close()
                            break

                        break

                else:
                    print('Closing')
                    heartbeat_socket.close()
                    break
