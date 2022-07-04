import socket
import random
import pickle
import os

import utils
import multicast_sender

name = input('To enter chatroom please write your name: ')

port = random.randint(6000, 10000)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_messages():
    while True:
        cmd_message = input("")
        message = pickle.dumps(['CHAT', name, cmd_message])
        try:
            server = (str(utils.leader), 10000)
            s.sendto(message, server)

        except Exception as e:
            print(e)
            break


def receive_messages():
    while True:

        try:
            data, addr = s.recvfrom(1024)
            print(f'{data.decode(utils.UNICODE)}')

            # if connection to server is lost (in case of server crash)
            if not data:
                print("\nChat server currently not available."
                      "Please wait 3 seconds for reconnection with new server leader.")
                s.close()
                #sleep(3)

                # Start reconnecting to new server leader
                #establish_connection()

        except Exception as e:
            print(e)
            break


def establish_connection():
    server_leader_found = multicast_sender.join_multicast_group(name)

    if server_leader_found:
        print(f'[SERVER] - LEADER: {utils.leader}')
        leader_address = (utils.leader, utils.SERVER_PORT)

        s.bind(('', port))

        message = pickle.dumps(['JOIN', name, ''])
        s.sendto(message, leader_address)
    # if there is no Server available, exit the script
    else:
        print("Please try to join later again.")
        os._exit(0)


if __name__ == '__main__':
    try:
        establish_connection()

        utils.start_thread(send_messages, ())
        utils.start_thread(receive_messages, ())

        while True:
            pass

    except KeyboardInterrupt:
        print("\nYou left the chatroom")
        leader_server = (str(utils.leader), 10000)
        message_to_send = pickle.dumps(['QUIT', name, 'Left the chatroom'])
        s.sendto(message_to_send, leader_server)
        #tell via Multicast that the client left the chatroom -> not directly necessary, broadcast_listener takes care
        #multicast_sender.multicast_socket.sendto(pickle.dumps([utils.RequestType.CLIENT_QUIT.value, '', '', '', '']), utils.MULTICAST_GROUP_ADDRESS)
        os._exit(0)