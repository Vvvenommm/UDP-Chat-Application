import socket
import random
import pickle #Umwandlung der Python-Objekthierarchie in einen Byte-Stream. Ein Objekt wird also quasi als bytes gespeichert und kann später wieder "entpackt" werden
import os

from time import sleep
from resources import utils
from multicast import multicast_sender

name = input('To enter chatroom please write your name: ')

port = random.randint(6000, 10000) #Client wählt zufälligen Port zwischen 6000 und 10000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP-Socket für Nachrichtenaustausch

def send_messages():
    while True:
        cmd_message = input("")
        message = pickle.dumps(['CHAT', name, cmd_message]) #Nachricht (cmd_message) wird über input empfangen und zusammen mit dem Marker "CHAT" und dem Usernamen des Client als byte-Datei gespeichert (pickle.dumps)
        try:
            server = (str(utils.leader), 10000) #Verbindung mit dem momentanen Leader-Server, der für die Bereitstellung des UDP-Broadcast zuständig ist. Abfrage aus Variable _leader_ aus utils. Als Port für den Broadcast ist pauschal 10000 festgelegt
            s.sendto(message, server) #byte-Datei wird an den zuvor identifizierten Server geschickt

        except Exception as e:
            print(e)
            break

def receive_messages():
    while True:

        try:
            data, addr = s.recvfrom(1024) #Daten ??Was ist hier enthalten?? werden über den Broadcast empfangen
            received_message = data.decode(utils.UNICODE)
            print(received_message)  # Empfangene Variable _data_ wird dekodiert und im Terminal gedruckt

            if received_message.endswith('SERVER HAS QUIT'):
                print("[CLIENT] - Server leader is not available. Reconnecting with new server leader in 3 seconds.") #Falls keine Daten ankommen: Server nicht erreichbar wird gedruckt !!Was, wenn einfach nichts geschrieben wird? Wird der Server nicht "zu schnell für tot erklärt"?
                s.close()
                sleep(15) # let client sleep for a few seconds before retriggering connection to new server leader again

                # Start reconnecting to new server leader
                establish_connection()

        except Exception as e:
            print(e)
            break


def establish_connection():
    server_leader_found = multicast_sender.join_multicast_group(name) #Leader server wird identifiziert
    # 1. Nachricht für Multicast Group wird erstellt. Diese enthält den Wert aus der Aufzählung von _CLIENT_JOIN_ ??Was ist hier genau enthalten, was ist Name und was ist Wert?? + die Namen der momentan vorhandenen Clients
    # 2. Nachricht wird an _MULTICAST_GROUP_ADRESS_ gesendet
    # 3. Es wird gewartet, bis über den Multicast aktuelle Infos zum Leader bereitgestellt werden. Die empfangene Variable _data_ kommt als byte und wird deshalb über pickle entpackt. Anschließend wird auch die Variable leader in utils aktualisiert

    """
    def join_multicast_group(name):
    # Send data to the multicast group
        message = pickle.dumps([utils.RequestType.CLIENT_JOIN.value, '', utils.CLIENT_LIST, '', name])
        multicast_socket.sendto(message, utils.MULTICAST_GROUP_ADDRESS)

    # try to get Server Leader
    try:
        data, address = multicast_socket.recvfrom(1024)
        received_leader = pickle.loads(data)[0]
        utils.leader = received_leader
        utils.CLIENT_LIST = received_leader[1]
        return True

    except socket.timeout:
        return False
    """

    if server_leader_found:
        print(f'[SERVER] - LEADER: {utils.leader}') #Leader Server wird im Terminal gedruckt
        leader_address = (utils.leader, utils.SERVER_PORT) # _leader_adress_ besteht aus dem Namen des leaders zusammen mit dem aus utils abgerufenen Port (allerdings immer 10000)

        s.bind(('', port)) #Client wird an seinen Broadcast port gebindet

        message = pickle.dumps(['JOIN', name, '']) #Nachricht wird gepackt, die neben dem Marker "JOIN" den Usernamen enthält ??Was sollen hier die leeren ''??
        s.sendto(message, leader_address) # Nachricht wird an die Leader-Adresse geschickt
    # if there is no Server available, exit the script
    else:
        print("[CLIENT] - New Server Leader not found! Please try to join later again.")
        s.close()
        os._exit(0)


#start
if __name__ == '__main__':
    try:
        establish_connection()

        utils.start_thread(send_messages, ()) #Starte Thread für Senden von Nachrichten
        utils.start_thread(receive_messages, ()) #Starte Thread für Empfangen von Nachrichten

        while True:
            pass

    except KeyboardInterrupt: #User bricht das Programm über Tastaturbefehl ab
        print("[CLIENT] - You left the chatroom") #Drucken, dass der Chatroom verlassen wird
        leader_server = (str(utils.leader), 10000) #Leader Server wird identifiziert
        message_to_send = pickle.dumps(['QUIT', name, 'Left the chatroom']) #Nachricht an den Server wird vorbereitet, die über das Verlassen informiert
        s.sendto(message_to_send, leader_server) #Nachricht wird gesendet
        s.close()
        #tell via Multicast that the client left the chatroom -> not directly necessary, broadcast_listener takes care
        #multicast_sender.multicast_socket.sendto(pickle.dumps([utils.RequestType.CLIENT_QUIT.value, '', '', '', '']), utils.MULTICAST_GROUP_ADDRESS)
        os._exit(0)