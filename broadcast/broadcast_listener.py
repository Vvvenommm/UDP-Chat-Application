import pickle
import socket

from resources import utils

# Create a UDP socket
broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the socket to broadcast and enable reusing addresses
broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind socket to address and port
broadcast_socket.bind((utils.get_host_ip(), utils.SERVER_PORT))

def start_broadcast_listener():
    print(f'[SERVER] started on IP: {utils.get_host_ip()} on PORT: {utils.SERVER_PORT}')
    print('[SERVER] waiting for participants...')

    while True:
        data, addr = broadcast_socket.recvfrom(1024)
        client_message = utils.handle_client_message(data)

        if addr not in utils.CLIENT_LIST:
            utils.CLIENT_LIST.append(addr)
            if client_message:
                handle_incoming_messages(client_message, addr)
                broadcast_socket.sendto(f'[SERVER]: {client_message.client_name}, you are connected with chatroom'.encode(utils.UNICODE), addr)
                broadcast_socket.sendto(f'[CLIENT LIST]: {utils.CLIENT_LIST}'.encode(utils.UNICODE), addr)
                client_message.client_message = 'joined chatroom'
                send_message_to_clients(client_message, addr)
                continue

        handle_incoming_messages(client_message, addr)
        send_message_to_clients(client_message, addr)


def handle_incoming_messages(message=None, addr=None):
    match message.chat_type:
        case 'JOIN':
            print(f'[CLIENT]: {addr} - {message.client_name} is connected with chatroom')
        case 'CHAT':
            print(get_formatted_message(addr, message.client_name, message.client_message))
        case 'QUIT':
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
