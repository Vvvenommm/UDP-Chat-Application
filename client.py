import socket
import random
import pickle
import os

from time import sleep
from resources import utils
from multicast import multicast_join, multicast_sender

name = input('To enter chatroom please write your name: ')


def send_messages():
    global client_socket
    while True:
        cmd_message = input("")
        message = pickle.dumps([utils.MessageType.CHAT.value, name, cmd_message])
        try:
            server = (str(utils.leader), 10000)
            client_socket.sendto(message, server)

        except Exception as e:
            print(e)
            break


def receive_messages():
    global client_socket
    while True:

        try:
            data, addr = client_socket.recvfrom(1024)
            received_message = data.decode(utils.UNICODE)

            if received_message.endswith('SERVER HAS QUIT'):
                print('\n[CLIENT] - Server leader is not available. Reconnecting with new server leader in 15 seconds.\n')
                client_socket.close()
                sleep(15) # let client sleep for a few seconds before retriggering connection to new server leader again

                # Start reconnecting to new server leader
                establish_connection()

            elif received_message.endswith('NEW_LEADER'):
                print('\n[CLIENT] -  new Leader has been elected. Reconnecting in 5 seconds.\n')
                client_socket.close()
                sleep(5)
                establish_connection()

            else:
                print(received_message)

        except Exception as e:
            print(e)
            break


def establish_connection():
    global client_socket
    port = random.randint(6000, 10000)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set the socket to broadcast and enable reusing addresses
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_leader_found = multicast_sender.join_multicast_group(name)

    if server_leader_found:
        print(f'[SERVER] - LEADER: {utils.leader}')
        leader_address = (utils.leader, utils.SERVER_PORT)

        client_socket.bind(('', port))

        message = pickle.dumps([utils.MessageType.JOIN.value, name, ''])
        client_socket.sendto(message, leader_address)
    # if there is no Server available, exit the script
    else:
        print('[CLIENT] - New Server Leader not found! Please try to join later again.')
        client_socket.close()
        os._exit(0)


if __name__ == '__main__':
    try:
        establish_connection()

        utils.start_thread(send_messages, ())
        utils.start_thread(receive_messages, ())

        while True:
            pass

    except KeyboardInterrupt:
        print("[CLIENT] - You left the chatroom")
        leader_server = (str(utils.leader), 10000)
        message_to_send = pickle.dumps([utils.MessageType.QUIT.value, name, 'Left the chatroom'])
        client_socket.sendto(message_to_send, leader_server)
        #tell via Multicast that the client left the chatroom -> not directly necessary, broadcast_listener takes care
        #multicast_sender.multicast_socket.sendto(pickle.dumps([utils.RequestType.CLIENT_QUIT.value, '', '', '', '']), utils.MULTICAST_GROUP_ADDRESS)
