import socket
import threading

# Constantes
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Função para receber mensagens do servidor
def receive_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(BUFFER_SIZE)
            print(f"Message received: {message.decode('utf-8')}")
        except:
            print("Error while receiving message")
            break

# Função para enviar mensagens ao servidor
def send_messages(client_socket, msg_type, sender_id, receiver_id, message):
    msg_type_bytes = msg_type.to_bytes(4, byteorder='big')
    sender_id_bytes = sender_id.to_bytes(4, byteorder='big')
    receiver_id_bytes = receiver_id.to_bytes(4, byteorder='big')
    message_size_bytes = len(message).to_bytes(4, byteorder='big')
    message_bytes = message.encode('utf-8') + b'\0'

    message = msg_type_bytes + sender_id_bytes + receiver_id_bytes + message_size_bytes + message_bytes
    client_socket.sendto(message, (SERVER_IP, SERVER_PORT))

# Inicialização do cliente
def start_client(client_id, client_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Envia mensage "OI" ao servidor
    send_messages(client_socket, 0, client_id, 0, client_name)

    # Inicia thread para receber mensagens do servidor
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        try:
            message = input("Type a message (or 'leave' to disconnect): ")

            if message.lower() == 'leave':
                send_messages(client_socket, 1, client_id, 0, "Disconnecting from the server")
                break
            
            receiver_id = int(input("Type the receiver id (0 to broadcast): "))
            send_messages(client_socket, 2, client_id, receiver_id, message)

        except Exception as e:
            print(f"Client error: {e}")
            break

    client_socket.close()

if __name__ == '__main__':
    client_id = int(input("Type your client id: "))
    client_name = input("Type your username: ")

    start_client(client_id, client_name)