import socket
import threading
import time
from datetime import datetime

# Definição de parâmetros
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
MAX_CLIENTS = 15

# Armazenamento de clientes ativos
clients = {}
lock = threading.Lock()

# Envia mensagem formatada ao cliente
def send_message(msg_type, server_socket, receiver_id, message):
    message = format_message(msg_type, 0, receiver_id, message)

    if receiver_id in clients:
        server_socket.sendto(message, clients[receiver_id])

# Transmite a mensagem a todos os clientes conectados
def broadcast_message(server_socket, sender_id, message):
    for client_id, client_address in clients.items():
        if client_id != sender_id:
            server_socket.sendto(message, client_address)

# Decodifica a mensagem recebida
def parse_message(message):
    msg_type = int.from_bytes(message[0:4], byteorder='big')
    sender_id = int.from_bytes(message[4:8], byteorder='big')
    receiver_id = int.from_bytes(message[8:12], byteorder='big')
    text_size = int.from_bytes(message[12:16], byteorder='big')

    return msg_type, sender_id, receiver_id, text_size

# Codifica a mensagem a ser enviada
def format_message(msg_type, sender_id, receiver_id, message):
    msg_type_bytes = msg_type.to_bytes(4, byteorder='big')
    sender_id_bytes = sender_id.to_bytes(4, byteorder='big')
    receiver_id_bytes = receiver_id.to_bytes(4, byteorder='big')
    message_size_bytes = len(message).to_bytes(4, byteorder='big')
    message_bytes = message.encode('utf-8') + b'\0'

    return msg_type_bytes + sender_id_bytes + receiver_id_bytes + message_size_bytes + message_bytes

# Mensagem periódica para manter a conexão ativa
def periodic_message(server_socket):
    while True:
        time.sleep(60)
        with lock:
            message = f"Server is Active, {len(clients)} clients connected. Time since start: {int(time.time())} seconds"

            for client_id in clients:
                send_message(2, server_socket, client_id, message)

# Função para tratar as mensagens enviadas por um cliente
def handle_client(client_socket, client_address):
    while True:
        try:
            message, client_address = client_socket.recvfrom(BUFFER_SIZE)

            if not message:
                break
        except:
            # Tratando possíveis falhas na comunicação
            print(f'Erro ao receber mensagem do cliente {client_address}')
            break

def handle_message(message, client_address):
    msg_type, sender_id, receiver_id, text_size = parse_message(message)

    # OI
    if msg_type == 0:
        with lock:
            if len(clients) < MAX_CLIENTS:
                clients[sender_id] = client_address
                send_message(0, server_socket, sender_id, "Successfully connected to the server")
            else:
                send_message(3, server_socket, sender_id, "Max Clients number reached, server is full")
    # TCHAU
    elif msg_type == 1:
        with lock:
            if sender_id in clients:
                # clients.pop(sender_id)
                del clients[sender_id]
                send_message(1, server_socket, sender_id, "Successfully disconnected from the server")
            else:
                send_message(3, server_socket, sender_id, "You are not connected to the server")
    # MSG
    elif msg_type == 2:
        if receiver_id == 0:
            broadcast_message(server_socket, sender_id, message)
        else:
            if receiver_id in clients:
                server_socket.sendto(message, clients[receiver_id])
            else:
                send_message(3, server_socket, sender_id, "Receiver is not connected to the server")
    # ERROR
    elif msg_type == 3:
        send_message(3, server_socket, sender_id, "Unknown error")

# Inicializa o servidor UDP
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    print(f'Server started at {SERVER_IP}:{SERVER_PORT}')

    # Inicializando thread para manter conexão ativa
    threading.Thread(target=periodic_message, args=(server_socket,)).start()

    while True:
        try:
            message, client_address = server_socket.recvfrom(BUFFER_SIZE)
            client_handler = threading.Thread(target=handle_client, args=(server_socket, client_address))
            client_handler.start()
        except Exception as e:
            print(f"Server error: {e}")

if __name__ == '__main__':
    start_server()