import socket
import struct
import pickle

from resources import utils

# Create the socket
multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#source: https://pymotw.com/3/socket/multicast.html
def start_receiver():
    # Bind to the server address
    multicast_socket.bind(('', utils.MULTICAST_PORT))

    # Tell the operating system to add the socket to
    # the multicast group on all interfaces.
    group = socket.inet_aton(utils.MULTICAST_GROUP_IP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    multicast_socket.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        mreq)

    # Receive/respond loop
    while True:
        try:
            data, address = multicast_socket.recvfrom(1024)
            message = utils.handle_pickle(data)

            #source: https://learnpython.com/blog/python-match-case-statement/
            match message.request_type:
                case utils.RequestType.SERVER_JOIN.value:
                    # when no server exists in the list -> first server
                    print(f'[SERVER] {address} wants to join Multicast-Group: {utils.MULTICAST_GROUP_ADDRESS}')
                    if not message.received_server_list:
                        utils.SERVER_LIST.append(address[0]) if address[0] not in utils.SERVER_LIST else utils.SERVER_LIST
                        multicast_socket.sendto(b'JOINED', address)
                        utils.network_changed = True

                    # server already exists -> 2nc e.g. Server is joining
                    # when leader received and current leader is empty (!= my host address) -> (utils.leader is at this stagee empty)
                    elif message.received_leader and utils.leader != utils.myIP:
                        # used from Server Replicas to update the own variables or if a Server Replica crashed
                        # elif pickle.loads(message)[1] and utils.leader != utils.myIP or pickle.loads(message)[3]:
                        utils.SERVER_LIST = message.received_server_list
                        utils.CLIENT_LIST = message.received_client_list
                        utils.leader = message.received_leader
                        multicast_socket.sendto(b'JOINED', address)
                        utils.network_changed = True
                        utils.new_server = True

                case utils.RequestType.CLIENT_JOIN.value:
                    print(f'[CLIENT]: {address} - {message.received_name} wants to join')
                    # answer Chat Client with Server Leader address
                    message = pickle.dumps([utils.leader])
                    multicast_socket.sendto(message, address)

                case utils.RequestType.CLIENT_QUIT.value:
                    print(f'[CLIENT]: {address} - {message.received_name} quit chatroom')
                    utils.client_quit = True


            #if len(message[0]) == 0:


            # used from Server Replicas to update the own variables or if a Server Replica crashed
            #elif pickle.loads(message)[1] and utils.leader != utils.myIP or pickle.loads(message)[3]:
            #    utils.SERVER_LIST = pickle.loads(message)[0]
            #    utils.leader = pickle.loads(message)[1]
            #    utils.CLIENT_LIST = pickle.loads(message)[4]

            #    multicast_socket.sendto(b'ack', address)
            #    utils.network_changed = True

        except KeyboardInterrupt:
            print('close')