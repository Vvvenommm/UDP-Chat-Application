import pickle
import socket
from resources import utils

# Create a UDP socket
broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the socket to broadcast and enable reusing addresses
broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind socket to address and port
broadcast_socket.bind(('', utils.SERVER_PORT))

def start_broadcast_listener():
    print(f'[SERVER] - started on IP: {utils.get_host_ip()} on PORT: {utils.SERVER_PORT}')
    print('[SERVER] - waiting for participants...')

    while True:
        data, addr = broadcast_socket.recvfrom(1024)
        client_message = utils.handle_client_message(data)

        # when Server quits forward message to clients
        if client_message.chat_type == utils.RequestType.QUIT_SERVER.value:
            send_message_to_clients(client_message, addr)

        # forward message that new leader joined to reconnect
        elif client_message.chat_type == utils.RequestType.NEW_LEADER.value:
            send_message_to_clients(client_message, addr)

        else:
            if addr not in utils.CLIENT_LIST:
                utils.CLIENT_LIST.append(addr)
                if client_message:
                    handle_incoming_messages(client_message, addr)
                    broadcast_socket.sendto(f'[SERVER]: {client_message.client_name}, you are connected with chatroom'.encode(utils.UNICODE), addr)
                    client_message.client_message = 'joined chatroom'
                    send_message_to_clients(client_message, addr)
                    continue

            handle_incoming_messages(client_message, addr)
            send_message_to_clients(client_message, addr)


def handle_incoming_messages(message=None, addr=None):
    # source: https://learnpython.com/blog/python-match-case-statement/
    # match case is a new functionality which came with python 3.10
    match message.chat_type:
        case utils.MessageType.JOIN.value:
            print(f'[CLIENT]: {addr} - {message.client_name} is connected with chatroom')
        case utils.MessageType.CHAT.value:
            print(get_formatted_message(addr, message.client_name, message.client_message))
        case utils.MessageType.QUIT.value:
            utils.CLIENT_LIST.remove(addr)
            print(get_formatted_message(addr, message.client_name, message.client_message))
            print(f'[CLIENT LIST]: {utils.CLIENT_LIST}')


def send_message_to_clients(message=None, addr=None):
    # send messages to all clients back
    for client in utils.CLIENT_LIST:
        if client != addr:
            message_to_send = get_formatted_message(addr, message.client_name, message.client_message)
            broadcast_socket.sendto(message_to_send.encode(utils.UNICODE), client)


def get_formatted_message(address=None, name=None, message=None):
    return f'[CLIENT]: {address} - {name}: {message}'
